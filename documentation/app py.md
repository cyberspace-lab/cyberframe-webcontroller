# 📄 **Documentation for `app.py`**

Welcome to the documentation for **`app.py`**, a Python script that serves as the backend server for a client-server application using Flask and Socket.IO. This server facilitates real-time communication between Unity game clients and a Vue.js frontend, managing sessions, handling events, and ensuring efficient resource utilization.

---

## 📋 **Table of Contents**

1. [Introduction](#introduction)
2. [Setup and Configuration](#setup-and-configuration)
3. [Global Variables and Constants](#global-variables-and-constants)
4. [Flask Routes](#flask-routes)
   - [`/` Route](#-route)
   - [`/test` Route](#test-route)
5. [Socket.IO Events](#socketio-events)
   - [Connection Events](#connection-events)
   - [Registration Events](#registration-events)
   - [Data Handling Events](#data-handling-events)
   - [Session Management Events](#session-management-events)
6. [Helper Functions](#helper-functions)
   - [Session Utilities](#session-utilities)
   - [Memory Management](#memory-management)
   - [Session Persistence](#session-persistence)
7. [Session Data Structure](#session-data-structure)
8. [Error Handling](#error-handling)
9. [Running the Server](#running-the-server)

---

## 📝 **Introduction**

This application is part of a client-server architecture designed to enable real-time communication between Unity game clients and a Vue.js frontend. The **`app.py`** script establishes a Flask server with Socket.IO integration, handling various events such as client connections, data updates, and session management.

### Key Features

- Real-time communication using **WebSockets** via **Socket.IO**.
- Session management for Unity clients and Vue.js frontend clients.
- Data handling and broadcasting to connected clients.
- Memory management to handle inactive sessions.
- Persistent storage of inactive sessions.

---

## ⚙️ **Setup and Configuration**

Before diving into the code, it's essential to understand the setup and configuration necessary for the server to function correctly.

### Dependencies

- **Flask**: A web application framework.
- **Flask-SocketIO**: Enables WebSocket support in Flask applications.
- **Flask-CORS**: Handles Cross-Origin Resource Sharing (CORS), making cross-origin AJAX possible.
- **psutil**: Provides information on running processes and system utilization (CPU, memory, disks, network, sensors).
- **json**: For handling JSON data.
- **gc**: Provides an interface to the garbage collector.
- **os**: Provides a portable way of using operating system-dependent functionality.

### Configuration File

The server loads its configuration from **`config.json`**, located at **`vue-frontend/src/config.json`**. This configuration includes application-specific settings such as maximum history sizes and memory thresholds.

```python
# Load the configuration file
with open('vue-frontend/src/config.json') as config_file:
    config = json.load(config_file)
```

---

## 🌐 **Global Variables and Constants**

### Constants

#### `INACTIVE_SESSIONS_DIR`

- **Description**: Directory path where inactive sessions are stored on disk.
- **Value**: `'./inactive_sessions'`

```python
INACTIVE_SESSIONS_DIR = './inactive_sessions'
```

#### Initialize Inactive Sessions Directory

Ensures the directory exists to store inactive session data.

```python
if not os.path.exists(INACTIVE_SESSIONS_DIR):
    os.makedirs(INACTIVE_SESSIONS_DIR)
```

### Global Variables

#### `sessions`

- **Type**: `dict`
- **Description**: Stores session data for each connected Unity client, keyed by `device_id`.

```python
sessions = {}
```

#### `vue_sessions`

- **Type**: `set`
- **Description**: Stores the session IDs (`sid`) of connected Vue.js frontend clients.

```python
vue_sessions = set()
```

#### `max_history_cache`

- **Type**: `dict`
- **Description**: Caches the maximum history size for each session to avoid redundant configuration lookups.

```python
max_history_cache = {}
```

#### `config`

- **Type**: `dict`
- **Description**: Holds configuration data loaded from `config.json`.

```python
config = None
```

---

## 🚏 **Flask Routes**

The server defines two primary routes using Flask to handle basic HTTP requests.

### `/` Route

- **Path**: `/`
- **Method**: `GET`
- **Description**: Returns a simple message indicating the server is running.

```python
@app.route('/')
def index():
    return "Server is running."
```

### `/test` Route

- **Path**: `/test`
- **Method**: `GET`
- **Description**: Serves a static HTML file (`test_interface.html`) for testing commands to Unity clients.

```python
@app.route('/test')
def test_interface():
    return app.send_static_file('test_interface.html')
```

---

## 🔌 **Socket.IO Events**

Socket.IO enables real-time bidirectional communication between clients and the server. The server handles various events to manage sessions and data transmission.

### **Connection Events**

#### `'connect'` Event

- **Triggered When**: A client establishes a connection to the server.
- **Handler**: `handle_connect`
- **Actions**:
  - Logs the connection.
  - Stores the client's session ID (`sid`).

```python
@socketio.on('connect')
def handle_connect():
    app.logger.info('Client connected: ' + request.sid)
```

#### `'disconnect'` Event

- **Triggered When**: A client disconnects from the server.
- **Handler**: `handle_disconnect`
- **Actions**:
  - Logs the disconnection.
  - Determines if the disconnected client is a Vue.js frontend or a Unity client.
  - Updates the session status and saves inactive sessions to disk.
  - Emits updates to other clients.

```python
@socketio.on('disconnect')
def handle_disconnect():
    # Handle disconnection logic
```

### **Registration Events**

#### `'register_vue'` Event

- **Triggered When**: A Vue.js frontend client registers with the server.
- **Handler**: `handle_register_vue`
- **Actions**:
  - Adds the client's `sid` to `vue_sessions`.
  - Emits the current session states to the new Vue.js client.

```python
@socketio.on('register_vue')
def handle_register_vue():
    # Handle Vue.js client registration
```

#### `'register'` Event

- **Triggered When**: A Unity client registers with the server.
- **Handler**: `handle_register`
- **Actions**:
  - Parses registration data.
  - Checks for existing sessions.
  - Initializes or updates session data.
  - Emits events to notify other clients.

```python
@socketio.on('register')
def handle_register(data):
    # Handle Unity client registration
```

### **Data Handling Events**

#### `'ping'` and `'pong'` Events

- **Purpose**: Keeps the connection alive and monitors latency.
- **Handlers**:
  - `'ping'`: Not explicitly handled (clients send ping).
  - `'pong'`: Emitted in response to `'ping'`.

```python
@socketio.on('ping')
def ping():
    emit('pong', room=request.sid)
```

#### `'update_data'` Event

- **Triggered When**: A client sends data to be updated on the server.
- **Handler**: `handle_update_data`
- **Actions**:
  - Parses the incoming data.
  - Updates the session's data store.
  - Enforces maximum history sizes.
  - Emits updates to other clients.

```python
@socketio.on('update_data')
def handle_update_data(data):
    # Handle data updates from clients
```

#### `'send_command'` Event

- **Triggered When**: A command is sent to a Unity client.
- **Handler**: `handle_send_command`
- **Actions**:
  - Extracts the event name and parameters.
  - Emits the command to the specified Unity client.

```python
@socketio.on('send_command')
def handle_send_command(data):
    # Handle commands sent to Unity clients
```

### **Session Management Events**

#### `'get_active_sessions'` Event

- **Triggered When**: A client requests the list of active sessions.
- **Handler**: `handle_get_active_sessions`
- **Actions**:
  - Emits the list of active sessions to the requesting client.

```python
@socketio.on('get_active_sessions')
def handle_get_active_sessions():
    # Emit active sessions to the client
```

#### `'get_inactive_sessions'` Event

- **Triggered When**: A client requests the list of inactive sessions.
- **Handler**: `handle_get_inactive_sessions`
- **Actions**:
  - Emits the list of inactive sessions to the requesting client.

```python
@socketio.on('get_inactive_sessions')
def handle_get_inactive_sessions():
    # Emit inactive sessions to the client
```

#### `'get_active_session'` Event

- **Triggered When**: A client requests details of a specific active session.
- **Handler**: `handle_get_active_session`
- **Actions**:
  - Validates the `device_id`.
  - Emits the session details if it is active.

```python
@socketio.on('get_active_session')
def handle_get_active_session(data):
    # Fetch and emit details of an active session
```

#### `'get_inactive_session'` Event

- **Triggered When**: A client requests details of a specific inactive session.
- **Handler**: `handle_get_inactive_session`
- **Actions**:
  - Validates the `device_id`.
  - Emits the session details if it is inactive.

```python
@socketio.on('get_inactive_session')
def handle_get_inactive_session(data):
    # Fetch and emit details of an inactive session
```

#### `'delete_session'` Event

- **Triggered When**: A client requests deletion of a session.
- **Handler**: `handle_delete_session`
- **Actions**:
  - Removes the session from memory.
  - Deletes the session data from disk.
  - Emits session updates to other clients.

```python
@socketio.on('delete_session')
def handle_delete_session(data):
    # Handle deletion of a session
```

---

## 🛠️ **Helper Functions**

Several helper functions support the primary event handlers, managing sessions, memory, and data persistence.

### **Session Utilities**

#### `emit_session_data_key_update(data)`

- **Purpose**: Emits updates for a specific data key within a session to all connected Vue.js clients.

```python
def emit_session_data_key_update(data):
    # Emit data key updates to Vue.js clients
```

#### `emit_sessions_update()`

- **Purpose**: Emits the updated lists of active and inactive sessions to all connected Vue.js clients.

```python
def emit_sessions_update():
    # Emit session updates to Vue.js clients
```

#### `get_active_sessions()`

- **Returns**: A dictionary of active sessions.

```python
def get_active_sessions():
    return {device_id: session for device_id, session in sessions.items() if session.get('is_connected')}
```

#### `get_inactive_sessions()`

- **Returns**: A dictionary of inactive sessions, including those loaded from disk.

```python
def get_inactive_sessions():
    # Return and load inactive sessions
```

### **Memory Management**

#### `get_available_memory_percentage()`

- **Returns**: The percentage of available system memory.
- **Purpose**: Helps in decision-making for memory cleanup.

```python
def get_available_memory_percentage():
    # Calculate available memory percentage
```

#### `cleanup_inactive_sessions()`

- **Purpose**: Removes inactive sessions from memory if the available memory drops below a configured threshold.

```python
def cleanup_inactive_sessions():
    # Clean up sessions if memory is low
```

### **Session Persistence**

#### `save_session_to_disk(device_id, session)`

- **Purpose**: Saves an inactive session's data to disk for persistence.

```python
def save_session_to_disk(device_id, session):
    # Save session data to disk
```

#### `load_session_from_disk(device_id)`

- **Returns**: Session data if available on disk.
- **Purpose**: Loads a session's data from disk upon reconnection or server restart.

```python
def load_session_from_disk(device_id):
    # Load session data from disk
```

---

## 📊 **Session Data Structure**

Understanding how sessions are structured is vital for effectively interacting with the server.

### **Session Dictionary Structure**

Each session in the `sessions` dictionary follows this structure:

```python
{
    'session_name': str,     # Name of the session/application
    'start_time': float,     # Timestamp when the session started
    'last_ping': float,      # Timestamp of the last client data update
    'data': dict,            # Dictionary to store data updates
    'sid': str,              # Socket.IO session ID
    'is_connected': bool     # Connection status
}
```

---

## ❗ **Error Handling**

The server includes basic error handling to ensure clients are informed of issues.

- **Validation Errors**: When required fields are missing from client requests, the server emits an `'error'` event with a descriptive message.
- **Exception Handling**: Try-except blocks capture unexpected errors, emitting an `'error'` event to the client.

```python
try:
    # Code that may raise an exception
except Exception as e:
    emit('error', str(e), room=request.sid)
```

---

## 🚀 **Running the Server**

At the end of the script, the server is set to run when the script is executed directly.

```python
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=4000)
```

- **Host**: `'0.0.0.0'` allows the server to be accessible from any network interface.
- **Port**: `4000` is the port on which the server listens for incoming connections.
