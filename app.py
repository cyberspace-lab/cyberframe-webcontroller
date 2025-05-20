import json
import logging
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from time import time
import psutil
import gc
import os

# Constants
INACTIVE_SESSIONS_DIR = './inactive_sessions'

password = os.getenv("PASSWORD", "0000")

# Create the inactive sessions directory if it doesn't exist
if not os.path.exists(INACTIVE_SESSIONS_DIR):
    os.makedirs(INACTIVE_SESSIONS_DIR)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize the Flask app and SocketIO
app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
sessions = {}  # {(device_id, session_name): session_data}
vue_sessions = set()
max_history_cache = {}
config = None

# Load the configuration file
with open('vue-frontend/src/config.json') as config_file:
    config = json.load(config_file)

# Routes
@app.route('/')
def index():
    return "Server is running."

# Test interface for sending commands to Unity
@app.route('/test')
def test_interface():
    return app.send_static_file('test_interface.html')

# Save the configuration file
@socketio.on('save_config')
def save_config(data):
    app.logger.info("Saving config")

    user_password = data["password"]
    config_content = data["config_content"]

     # Check if there are any active sessions
    active_sessions = get_active_sessions()
    if active_sessions:
        app.logger.info("Active sessions found, config not saved.")
        emit('error', {'message': 'Cannot save config due to active sessions.'}, room=request.sid)
        return

    if user_password == password:
        try:
            with open('/vue-frontend/src/config.json', 'w') as config_file:
                config_file.write(config_content)

            app.logger.info("Config saved successfully")
            emit('config_saved', room=request.sid)
        except Exception as e:
            app.logger.error(f"Error saving config: {e}")
            emit('error', {'message': 'Error saving config'}, room=request.sid)
    else:
        emit('error', {'message': 'Incorrect password'}, room=request.sid)

# Load the configuration file
@socketio.on('load_config')
def load_config(data):
    app.logger.info("Attempting to load config")

    user_password = data["password"]

    if user_password == password:
        try:
            with open('/vue-frontend/src/config.json', 'r') as config_file:
                config_content = config_file.read()

            # Send the config content back to the client
            emit('config_loaded', {'config_content': config_content}, room=request.sid)
            app.logger.info("Config loaded successfully")

        except Exception as e:
            app.logger.error(f"Error loading config: {e}")
            emit('error', {'message': 'Error loading config'}, room=request.sid)
    else:
        emit('error', {'message': 'Incorrect password'}, room=request.sid)

# Handle the ping event
@socketio.on('ping')
def ping():
    emit('pong', room=request.sid)

# Handle the connect and disconnect events
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
        # Find the session with the matching sid and mark it as disconnected
        for key, session in sessions.items():
            if session['sid'] == request.sid:
                session['last_ping'] = time()
                session['is_connected'] = False

                save_session_to_disk(key[0], key[1], session)

                emit('unity_disconnected', {'device_id': key[0], 'session_name': key[1]}, broadcast=True)
                break

    emit_sessions_update()

# Handle the register_vue and register events
@socketio.on('register_vue')
def handle_register_vue():
    vue_sessions.add(request.sid)
    app.logger.info(f"Vue registered with session ID: {request.sid}")
    emit_sessions_update()

# Handle the register event
@socketio.on('register')
def handle_register(data):
    # Cleanup inactive sessions if memory is low
    cleanup_inactive_sessions()

    # Get the device ID and session name from the data
    data = json.loads(data)
    device_id = data.get('device_id')
    session_name = data.get('session_name')

    if not device_id or not session_name:
        emit('error', {'message': 'device_id and session_name are required'})
        return

    # Check if the device ID is already registered
    key = (device_id, session_name)
    existing_session = load_session_from_disk(device_id, session_name)
    if existing_session:
        sessions[key] = existing_session
        sessions[key].update({
            'sid': request.sid,
            'is_connected': True,
            'last_ping': time()
        })
    else:
        # Create a new session
        sessions[key] = {
            'session_name': session_name,
            'start_time': time(),
            'last_ping': time(),
            'data': {},
            'sid': request.sid,
            'is_connected': True
        }

        # Initialize the data with the default values
        app_config = config.get('applications', {}).get(session_name, {})
        receivers = app_config.get('receivers', [{}])

        for receiver in receivers:
            for k in receiver.keys():
                sessions[key]['data'][k] = []

    emit('registered', room=request.sid)
    emit('unity_connected', {'device_id': device_id, 'session_name': session_name}, broadcast=True)
    # Emit the updated sessions to all clients
    emit_sessions_update()

# Handle the send_command event
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
    # Cleanup inactive sessions if memory is low
    cleanup_inactive_sessions()

    try:
        # Get the device ID, key, and value from the data
        data = json.loads(data)
        device_id = data.get('device_id')
        session_name = data.get('session_name')
        key_name = data.get('key')
        value = data.get('value')

        if not device_id or not session_name or not key_name or not value:
            emit('error', 'device_id, session_name, key, and value are required', room=request.sid)
            return

        key = (device_id, session_name)
        if key_name not in sessions[key]['data']:
            sessions[key]['data'][key_name] = []

        # Insert the value at the beginning of the list
        sessions[key]['data'][key_name].insert(0, value)
        sessions[key]['last_ping'] = time()

        # Limit the history size based on the configuration
        max_history_size = max_history_cache.get((session_name, key_name))
        if max_history_size is None:
            app_config = config.get('applications', {}).get(session_name, {})
            receivers = app_config.get('receivers', [{}])
            max_history_size = receivers[0].get(key_name, {}).get('maxHistory', 10)
            max_history_cache[(session_name, key_name)] = max_history_size

        # Trim the history size
        if len(sessions[key]['data'][key_name]) > max_history_size:
            sessions[key]['data'][key_name] = sessions[key]['data'][key_name][:max_history_size]

        emit_session_data_key_update({'device_id': device_id, 'session_name': session_name, 'key': key_name})

    except Exception as e:
        emit('error', str(e), room=request.sid)

@socketio.on('get_active_sessions')
def handle_get_active_sessions():
    # Emit the active sessions to the client
    emit('active_sessions_update', get_active_sessions(), room=request.sid)
    app.logger.info(f'Active sessions emitted to: {request.sid}')

@socketio.on('get_inactive_sessions')
def handle_get_inactive_sessions():
    # Emit the inactive sessions to the client
    emit('inactive_sessions_update', get_inactive_sessions(), room=request.sid)
    app.logger.info(f'Inactive sessions emitted to: {request.sid}')

# This event is used to fetch the active session for a device ID
@socketio.on('get_active_session')
def handle_get_active_session(data):
    # Get the device ID from the data
    device_id = data.get('device_id')
    session_name = data.get('session_name')
    app.logger.info(f"Requested active session for device ID: {device_id}")

    key = (device_id, session_name)

    # Check if the device ID is in the sessions and is connected
    if key in sessions and sessions[key].get('is_connected'):
        emit('active_session', {'device_id': device_id, 'session_name': session_name, 'session': sessions[key]}, room=request.sid)
        app.logger.info(f"Active session emitted: {device_id}")

# This event is used to fetch the inactive session for a device ID
@socketio.on('get_inactive_session')
def handle_get_inactive_session(data):
    device_id = data.get('device_id')

    session_name = data.get('session_name')
    key = (device_id, session_name)
    # Check if the device ID is in the sessions and is not connected
    if key in sessions and not sessions[key].get('is_connected'):
        emit('inactive_session', {'device_id': device_id, 'session_name': session_name, 'session': sessions[key]}, room=request.sid)
        app.logger.info(f"Inactive session emitted: {device_id}")

# This event is used to delete the session for a device ID
@socketio.on('delete_session')
def handle_delete_session(data):
    device_id = data.get('device_id')
    session_name = data.get('session_name')
    key = (device_id, session_name)

    session = sessions.pop(key, None)
    
    if session:
        app.logger.info(f"Deleted session for device ID: {device_id}")
        filename = f"{device_id}_{session_name}.json"

        file_path = os.path.join(INACTIVE_SESSIONS_DIR, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                app.logger.info(f"Deleted session file from disk: {file_path}")
            except Exception as e:
                app.logger.error(f"Error deleting session file: {e}")

        emit_sessions_update()

# This event is used to update the session data key for a device ID
def emit_session_data_key_update(data):
    device_id = data.get('device_id')
    session_name = data.get('session_name')
    key_name = data.get('key')
    key = (device_id, session_name)

    if key in sessions:
        for vue_sid in vue_sessions:
            emit('session_data_key_update', {
                'device_id': device_id,
                'session_name': session_name,
                'key': key_name,
                'value': sessions[key]['data'][key_name]
            }, room=vue_sid)

# This event is used to emit the updated sessions to all Vue clients
def emit_sessions_update():
    active_sessions = get_active_sessions()
    inactive_sessions = get_inactive_sessions()
    for vue_sid in vue_sessions:
        emit('active_sessions_update', active_sessions, room=vue_sid)
        emit('inactive_sessions_update', inactive_sessions, room=vue_sid)
    app.logger.info(f'Sessions emitted to all Vue clients')

def get_active_sessions_internal():
    return {(device_id, session['session_name']): session for (device_id, session_name), session in sessions.items() if session.get('is_connected')}

def get_active_sessions():
    # Return the active sessions
    active_sessions = get_active_sessions_internal()
    sessions = {}
    for (device_id, session_name), session in active_sessions.items():
        key = json.dumps([device_id, session_name])
        sessions[key] = session
    return sessions

def get_inactive_sessions_internal():
    inactive = {
        (device_id, session_name): session
        for (device_id, session_name), session in sessions.items()
        if not session.get('is_connected')
    }

    # Load the inactive sessions from disk
    for file_name in os.listdir(INACTIVE_SESSIONS_DIR):
        base_name = os.path.splitext(file_name)[0]
        parts = base_name.split('_', 1)

        device_id, session_name = parts
        key = (device_id, session_name)
        
        if key not in inactive and key not in sessions:
            file_path = os.path.join(INACTIVE_SESSIONS_DIR, file_name)
            try:
                with open(file_path, 'r') as f:
                    session = json.load(f)
                inactive[key] = session
                sessions[key] = session
            except Exception as e:
                app.logger.error(f"Error loading session file {file_name}: {e}")

    return inactive

def get_inactive_sessions():
    # Return the inactive sessions
    inactive_sessions = get_inactive_sessions_internal()
    sessions = {}
    for (device_id, session_name), session in inactive_sessions.items():
        key = json.dumps([device_id, session_name])
        sessions[key] = session
    return sessions

# This function returns the available memory percentage
def get_available_memory_percentage():
    memory_info = psutil.virtual_memory()
    available_percentage = 100 - memory_info.percent 
    app.logger.info(f"Memory available: {available_percentage}%")
    return available_percentage

# This function cleans up inactive sessions if memory is low
def cleanup_inactive_sessions():
    available_percentage = get_available_memory_percentage()
    min_free_memory_percentage = config.get('min_free_memory_percentage', 30)

    if available_percentage < min_free_memory_percentage:
        app.logger.info(f"Low memory detected: {available_percentage}% available. Cleaning up sessions...")

        # Remove inactive sessions until memory is above the threshold
        inactive_sessions = sorted(
            ((k, s) for k, s in sessions.items() if not s['is_connected']),
            key=lambda item: item[1].get('last_ping', 0)
        )

        for device_id, session in inactive_sessions:
            sessions.pop(device_id, None)
            app.logger.info(f"Removed inactive session for device ID: {device_id}")

            gc.collect()
            available_percentage = get_available_memory_percentage()
            if available_percentage >= min_free_memory_percentage:
                break

# This function saves the session to disk
def save_session_to_disk(device_id, session_name, session):
    filename = f"{device_id}_{session_name}.json"
    file_path = os.path.join(INACTIVE_SESSIONS_DIR, filename)
    try:
        with open(file_path, 'w') as f:
            json.dump(session, f, default=str)
        app.logger.info(f"Saved inactive session to disk: {file_path}")
    except Exception as e:
        app.logger.error(f"Error saving session to disk: {e}")

# This function loads the session from disk
def load_session_from_disk(device_id, session_name):
    filename = f"{device_id}_{session_name}.json"
    file_path = os.path.join(INACTIVE_SESSIONS_DIR, filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
            app.logger.info(f"Loaded session from disk: {file_path}")
        except Exception as e:
            app.logger.error(f"Error loading session from disk: {e}")
    return None

# Run the app
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=4000)