from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy import func
from flask_cors import CORS
from os import environ
from time import time
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)

cors = CORS(app, origins="*")

sessions = {}
max_history_cache = {}
config = None

with open('vue-frontend/src/config.json') as config_file:
    config = json.load(config_file)

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    if device_id in sessions:
        sessions[device_id]['last_ping'] = time()
        return jsonify({'message': 'ping received', 'public_ip': sessions[device_id]['public_ip']}), 200
        
    session_name = data.get('session_name')
    endpoint = data.get('endpoint')
    public_ip = request.remote_addr
    
    sessions[device_id] = {
        'session_name': session_name,
        'start_time': time(),
        'last_ping': time(),
        'endpoint': endpoint,
        'data': {},
        'public_ip': public_ip
    }

    app_config = config.get('applications', {}).get(session_name, {})
    receivers = app_config.get('receivers', [{}])

    for receiver in receivers:
        for key in receiver.keys():
            sessions[device_id]['data'][key] = []
    
    return jsonify({'message': 'registered successfully', 'public_ip': public_ip}), 200

@app.route('/sessions', methods=['GET'])
def get_sessions():
    current_time = time()
    active_sessions = {k: v for k, v in sessions.items() if current_time - v['last_ping'] < 10}
    
    return jsonify(active_sessions), 200

@app.route('/past-sessions', methods=['GET'])
def get_past_sessions():
    current_time = time()
    past_sessions = {k: v for k, v in sessions.items() if current_time - v['last_ping'] >= 10}
    
    return jsonify(past_sessions), 200

@app.route('/update_data', methods=['POST'])
def update_data():
    try:
        data = request.get_json()
        
        if data is None:
            raise ValueError("No JSON data provided")

        device_id = data.get('device_id')
        key = data.get('key')
        value = data.get('value')

        if not device_id or not key or not value:
            return jsonify({'error': 'device_id, key, and value are required'}), 400

        if key not in sessions[device_id]['data']:
            sessions[device_id]['data'][key] = []

        sessions[device_id]['data'][key].insert(0, value)

        session_name = sessions[device_id]['session_name']

        max_history_size = max_history_cache.get((session_name, key))
        if max_history_size is None:
            app_config = config.get('applications', {}).get(session_name, {})
            receivers = app_config.get('receivers', [{}])
            max_history_size = receivers[0].get(key, {}).get('maxHistory', 10)
            max_history_cache[(session_name, key)] = max_history_size

        if len(sessions[device_id]['data'][key]) > max_history_size:
            sessions[device_id]['data'][key] = sessions[device_id]['data'][key][:max_history_size]

        return jsonify({'message': 'Data updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/session_data/<device_id>', methods=['GET'])
def get_session_data(device_id):
    if device_id in sessions:
        return jsonify(sessions[device_id]['data']), 200
    return jsonify({}), 404