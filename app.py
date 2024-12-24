import json
import logging
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from time import time
import psutil
import gc
import os

INACTIVE_SESSIONS_DIR = './inactive_sessions'

if not os.path.exists(INACTIVE_SESSIONS_DIR):
    os.makedirs(INACTIVE_SESSIONS_DIR)

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

sessions = {}
vue_sessions = set()
max_history_cache = {}
config = None

with open('vue-frontend/src/config.json') as config_file:
    config = json.load(config_file)

@app.route('/')
def index():
    return "Server is running."

@app.route('/test')
def test_interface():
    return app.send_static_file('test_interface.html')

@socketio.on('ping')
def ping():
    emit('pong', room=request.sid)

@socketio.on('connect')
def handle_connect():
    app.logger.info('Client connected: ' + request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    app.logger.info('Client disconnected: ' + request.sid)

    if request.sid in vue_sessions:
        vue_sessions.remove(request.sid)
        app.logger.info(f"Vue session removed: {request.sid}")
    else:
        for device_id, session in sessions.items():
            if session['sid'] == request.sid:
                session['last_ping'] = time()
                session['is_connected'] = False

                save_session_to_disk(device_id, session)

                emit('unity_disconnected', {'device_id': device_id}, broadcast=True)
                break

    emit_sessions_update()

@socketio.on('register_vue')
def handle_register_vue():
    vue_sessions.add(request.sid)
    app.logger.info(f"Vue registered with session ID: {request.sid}")
    emit_sessions_update()

@socketio.on('register')
def handle_register(data):
    cleanup_inactive_sessions()

    data = json.loads(data)
    device_id = data.get('device_id')
    session_name = data.get('session_name')

    if not device_id:
        emit('error', {'message': 'device_id is required'})
        return

    existing_session = load_session_from_disk(device_id)
    if existing_session:
        sessions[device_id] = existing_session
        sessions[device_id].update({
            'sid': request.sid,
            'is_connected': True,
            'last_ping': time()
        })
    else:
        sessions[device_id] = {
            'session_name': session_name,
            'start_time': time(),
            'last_ping': time(),
            'data': {},
            'sid': request.sid,
            'is_connected': True
        }

        app_config = config.get('applications', {}).get(session_name, {})
        receivers = app_config.get('receivers', [{}])

        for receiver in receivers:
            for key in receiver.keys():
                sessions[device_id]['data'][key] = []

    emit('registered', room=request.sid)
    emit('unity_connected', {'device_id': device_id}, broadcast=True)
    emit_sessions_update()

@socketio.on('send_command')
def handle_send_command(data):
    app.logger.info(f"Received command: {data}")

    eventName = data.get('payload', {}).get('eventName')
    parameters = data.get('payload', {}).get('parameters')
    sid = data.get('sid')

    emit(eventName, parameters, room=sid)
    app.logger.info(f"Command {eventName} sent with parameters: {parameters}")

@socketio.on('update_data')
def handle_update_data(data):
    app.logger.info(f"Data received: {data}")
    cleanup_inactive_sessions()

    try:
        data = json.loads(data)
        device_id = data.get('device_id')
        key = data.get('key')
        value = data.get('value')

        if not device_id or not key or not value:
            emit('error', 'device_id, key, and value are required', room=request.sid)
            return

        if key not in sessions[device_id]['data']:
            sessions[device_id]['data'][key] = []

        sessions[device_id]['data'][key].insert(0, value)
        sessions[device_id]['last_ping'] = time()

        session_name = sessions[device_id]['session_name']
        max_history_size = max_history_cache.get((session_name, key))
        if max_history_size is None:
            app_config = config.get('applications', {}).get(session_name, {})
            receivers = app_config.get('receivers', [{}])
            max_history_size = receivers[0].get(key, {}).get('maxHistory', 10)
            max_history_cache[(session_name, key)] = max_history_size

        if len(sessions[device_id]['data'][key]) > max_history_size:
            sessions[device_id]['data'][key] = sessions[device_id]['data'][key][:max_history_size]

        emit_session_data_key_update({'device_id': device_id, 'key': key})

    except Exception as e:
        emit('error', str(e), room=request.sid)

@socketio.on('get_active_sessions')
def handle_get_active_sessions():
    emit('active_sessions_update', get_active_sessions(), room=request.sid)
    app.logger.info(f'Active sessions emitted to: {request.sid}')

@socketio.on('get_inactive_sessions')
def handle_get_inactive_sessions():
    emit('inactive_sessions_update', get_inactive_sessions(), room=request.sid)
    app.logger.info(f'Inactive sessions emitted to: {request.sid}')

@socketio.on('get_active_session')
def handle_get_active_session(data):
    device_id = data.get('device_id')
    app.logger.info(f"Requested active session for device ID: {device_id}")

    if not device_id:
        emit('error', {'message': 'device_id is required to fetch session'})
        return

    if device_id in sessions and sessions[device_id].get('is_connected'):
        emit('active_session', {'device_id': device_id, 'session': sessions[device_id]}, room=request.sid)
        app.logger.info(f"Active session emitted: {device_id}")

@socketio.on('get_inactive_session')
def handle_get_inactive_session(data):
    device_id = data.get('device_id')

    if not device_id:
        emit('error', {'message': 'device_id is required to fetch session'})
        return

    if device_id in sessions and not sessions[device_id].get('is_connected'):
        emit('inactive_session', {'device_id': device_id, 'session': sessions[device_id]}, room=request.sid)
        app.logger.info(f"Inactive session emitted: {device_id}")

@socketio.on('delete_session')
def handle_delete_session(data):
    device_id = data.get('device_id')

    if not device_id:
        emit('error', {'message': 'device_id is required to delete session'})
        return

    session = sessions.pop(device_id, None)

    if session:
        app.logger.info(f"Deleted session for device ID: {device_id}")

        file_path = os.path.join(INACTIVE_SESSIONS_DIR, f"{device_id}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                app.logger.info(f"Deleted session file from disk: {file_path}")
            except Exception as e:
                app.logger.error(f"Error deleting session file from disk: {file_path}, Error: {e}")

        emit_sessions_update()

def emit_session_data_key_update(data):
    device_id = data.get('device_id')
    key = data.get('key')

    if not device_id:
        emit('error', {'message': 'device_id is required to fetch session data'})
        return

    if device_id in sessions:
        for vue_sid in vue_sessions:
            emit('session_data_key_update', {'device_id': device_id, 'key': key, 'value': sessions[device_id]['data'][key]}, room=vue_sid)

def emit_sessions_update():
    active_sessions = get_active_sessions()
    inactive_sessions = get_inactive_sessions()
    for vue_sid in vue_sessions:
        emit('active_sessions_update', active_sessions, room=vue_sid)
        emit('inactive_sessions_update', inactive_sessions, room=vue_sid)
    app.logger.info(f'Sessions emitted to all Vue clients')

def get_active_sessions():
    return {device_id: session for device_id, session in sessions.items() if session.get('is_connected')}

def get_inactive_sessions():
    inactive = {device_id: session for device_id, session in sessions.items() if not session.get('is_connected')}

    for file_name in os.listdir(INACTIVE_SESSIONS_DIR):
        device_id = os.path.splitext(file_name)[0]
        if device_id not in inactive and device_id not in sessions:
            file_path = os.path.join(INACTIVE_SESSIONS_DIR, file_name)
            try:
                with open(file_path, 'r') as f:
                    session = json.load(f)
                inactive[device_id] = session
                sessions[device_id] = session
            except Exception as e:
                app.logger.error(f"Error reading session file {file_name}: {e}")

    return inactive

def get_available_memory_percentage():
    memory_info = psutil.virtual_memory()
    available_percentage = 100 - memory_info.percent 
    app.logger.info(f"Memory available: {available_percentage}%")
    return available_percentage

def cleanup_inactive_sessions():
    available_percentage = get_available_memory_percentage()
    min_free_memory_percentage = config.get('min_free_memory_percentage', 30)

    if available_percentage < min_free_memory_percentage:
        app.logger.info(f"Low memory detected: {available_percentage}% available. Cleaning up sessions...")

        inactive_sessions = sorted(
            ((device_id, session) for device_id, session in sessions.items() if not session['is_connected']),
            key=lambda item: item[1].get('last_ping', 0)
        )

        for device_id, session in inactive_sessions:
            sessions.pop(device_id, None)
            app.logger.info(f"Removed inactive session for device ID: {device_id}")

            gc.collect()
            available_percentage = get_available_memory_percentage()
            if available_percentage >= min_free_memory_percentage:
                break

def save_session_to_disk(device_id, session):
    file_path = os.path.join(INACTIVE_SESSIONS_DIR, f"{device_id}.json")
    try:
        with open(file_path, 'w') as f:
            json.dump(session, f, default=str)
        app.logger.info(f"Saved inactive session to disk: {file_path}")
    except Exception as e:
        app.logger.error(f"Error saving session to disk: {e}")

def load_session_from_disk(device_id):
    file_path = os.path.join(INACTIVE_SESSIONS_DIR, f"{device_id}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                session = json.load(f)
            app.logger.info(f"Loaded session from disk: {file_path}")
            return session
        except Exception as e:
            app.logger.error(f"Error loading session from disk: {e}")
    return None

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=4000)