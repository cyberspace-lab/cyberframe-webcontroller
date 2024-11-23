import json
import logging
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from time import time
import psutil
import gc

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

sessions = {}
vue_session_id = 0
max_history_cache = {}
config = None

with open('vue-frontend/src/config.json') as config_file:
    config = json.load(config_file)

@app.route('/')
def index():
    return "Server is running."

@socketio.on('connect')
def handle_connect():
    app.logger.info('Client connected: ' + request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    app.logger.info('Client disconnected: ' + request.sid)

    if request.sid == vue_session_id:
        return

    for device_id, session in sessions.items():
        if session['sid'] == request.sid:
            session['last_ping'] = time()
            session['is_connected'] = False
            emit('unity_disconnected', {'device_id': device_id}, room=vue_session_id)
            break

    emit_sessions_update()

@socketio.on('register_vue')
def handle_register_vue():
    global vue_session_id
    vue_session_id = request.sid
    app.logger.info(f"Vue registered with session ID: {vue_session_id}")
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
    emit('unity_connected', room=vue_session_id)
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
    app.logger.info(f"Data recieved: {data}")
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
    emit('active_sessions_update', get_active_sessions(), room=vue_session_id)
    app.logger.info(f'Active sessions emmited to: {str(vue_session_id)}')

@socketio.on('get_inactive_sessions')
def handle_get_inactive_sessions():
    emit('inactive_sessions_update', get_inactive_sessions(), room=vue_session_id)
    app.logger.info(f'Inactive sessions emmited to: {str(vue_session_id)}')

@socketio.on('get_active_session')
def handle_get_active_session(data):
    device_id = data.get('device_id')
    app.logger.info(f"Requested active session for device ID: {device_id}")

    if not device_id:
        emit('error', {'message': 'device_id is required to fetch session'})
        return
    
    if device_id in sessions and sessions[device_id].get('is_connected'):
        emit('active_session', {'device_id': device_id, 'session': sessions[device_id]}, room=vue_session_id)
        app.logger.info(f"Active session emitted: {device_id}")

@socketio.on('get_inactive_session')
def handle_get_inactive_session(data):
    device_id = data.get('device_id')
    app.logger.info(f"Requested inactive session for device ID: {device_id}")

    if not device_id:
        emit('error', {'message': 'device_id is required to fetch session'})
        return
    
    if device_id in sessions and not sessions[device_id].get('is_connected'):
        emit('inactive_session', {'device_id': device_id, 'session': sessions[device_id]}, room=vue_session_id)
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
        emit_sessions_update()

def emit_session_data_key_update(data):
    device_id = data.get('device_id')
    key = data.get('key')

    if not device_id:
        emit('error', {'message': 'device_id is required to fetch session data'})
        return

    if device_id in sessions:
        emit('session_data_key_update', {'device_id': device_id, 'key': key, 'value': sessions[device_id]['data'][key]}, room=vue_session_id)

def emit_sessions_update():
    emit('active_sessions_update', get_active_sessions(), room=vue_session_id)
    emit('inactive_sessions_update', get_inactive_sessions(), room=vue_session_id)
    app.logger.info(f'Sessions emmited to: {str(vue_session_id)}')

def get_active_sessions():
    return {device_id: session for device_id, session in sessions.items() if session.get('is_connected')}

def get_inactive_sessions():
    return {device_id: session for device_id, session in sessions.items() if not session.get('is_connected')}

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

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=4000, debug=True)