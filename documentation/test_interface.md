# Documentation for `test_interface.html` 📄

## Overview 📝

**Filename**: `test_interface.html`

**Purpose**: This HTML file provides a **user interface** to simulate Unity client sessions and send fake data to the server using **Socket.IO**. It is primarily used for **testing** and **debugging** the backend server (`app.py`) and the **Socket.IO** communication without the need for an actual Unity client.

---

## Table of Contents 📚

1. [Introduction](#introduction)
2. [File Structure](#file-structure)
3. [Detailed Explanation](#detailed-explanation)
   - [Including Socket.IO Client Library](#including-socketio-client-library)
   - [Establishing Connection](#establishing-connection)
   - [Registering a Fake Session](#registering-a-fake-session)
   - [Updating Fake Data](#updating-fake-data)
   - [Error Handling](#error-handling)
4. [Usage Instructions](#usage-instructions)
5. [Integration with Backend](#integration-with-backend)

---

## Introduction 🎯

The `test_interface.html` file serves as a **testing tool** for developers to:

- Simulate Unity client sessions.
- Send custom data to the server.
- Test the server's event handling and data processing.
- Validate the communication between the client and server via **Socket.IO**.

---

## File Structure 🏗️

The file is composed of:

- **HTML**: Defines the structure of the web page.
- **JavaScript**: Contains scripts to handle events and communicate with the server.
- **Socket.IO Client Library**: Included via CDN for real-time communication.

---

## Detailed Explanation 📖

### Including Socket.IO Client Library 📥

```html
<script src="https://cdn.jsdelivr.net/npm/socket.io-client@4.5.1/dist/socket.io.min.js"></script>
```

- **Purpose**: To utilize the Socket.IO client for establishing a connection with the Socket.IO server.
- **Version**: 4.5.1 (Ensure compatibility with the server version).

### Establishing Connection 🔌

```javascript
const socket = io('http://localhost:4000');
```

- **Connection Endpoint**: `http://localhost:4000` (Adjust as per your server's address).
- **Function**: Initializes a new Socket.IO client instance and connects to the server.

### Registering a Fake Session 📝

#### HTML Elements

```html
<!-- Register Fake Session Section -->
<h2>Register Fake Session</h2>
<label for="device_id">Device ID: </label>
<input type="text" id="device_id" placeholder="Enter device ID" />
<br />
<label for="session_name">Session Name: </label>
<input type="text" id="session_name" placeholder="Enter session name" />
<br />
<button onclick="registerFakeSession()">Register Fake Session</button>
```

- **Device ID**: A unique identifier for the fake Unity client.
- **Session Name**: Name of the session (could represent different applications or contexts).
- **Button**: Triggers the `registerFakeSession` function to send registration data to the server.

#### JavaScript Function

```javascript
function registerFakeSession() {
  const deviceId = document.getElementById('device_id').value;
  const sessionName = document.getElementById('session_name').value;

  if (!deviceId || !sessionName) {
    alert('Both device ID and session name are required!');
    return;
  }

  const data = JSON.stringify({ device_id: deviceId, session_name: sessionName });
  socket.emit('register', data);
  console.log(`Fake session registered with ID: ${deviceId}, Name: ${sessionName}`);
}
```

- **Input Validation**: Checks if both fields are filled.
- **Data Preparation**: Formats the data into a JSON string.
- **Event Emission**: Sends a `'register'` event to the server with registration data.
- **Logging**: Outputs the action to the console.

### Updating Fake Data 📨

#### HTML Elements

```html
<!-- Update Fake Data Section -->
<h2>Update Fake Data</h2>
<label for="update_device_id">Device ID: </label>
<input type="text" id="update_device_id" placeholder="Enter device ID" />
<br />
<label for="key">Key: </label>
<input type="text" id="key" placeholder="Enter data key" />
<br />
<label for="value">Value: </label>
<input type="text" id="value" placeholder="Enter value" />
<br />
<button onclick="updateFakeData()">Update Fake Data</button>
```

- **Device ID**: Specifies which session the data update belongs to.
- **Key**: The name of the data field to update.
- **Value**: The new value for the specified key.
- **Button**: Triggers the `updateFakeData` function to send data to the server.

#### JavaScript Function

```javascript
function updateFakeData() {
  const deviceId = document.getElementById('update_device_id').value;
  const key = document.getElementById('key').value;
  const value = document.getElementById('value').value;

  if (!deviceId || !key || !value) {
    alert('Device ID, Key, and Value are required!');
    return;
  }

  const data = JSON.stringify({ device_id: deviceId, key: key, value: value });
  socket.emit('update_data', data);
  console.log(`Fake data updated for Device ID: ${deviceId}, Key: ${key}, Value: ${value}`);
}
```

- **Input Validation**: Ensures all fields are provided.
- **Data Preparation**: Encodes the data into a JSON string.
- **Event Emission**: Sends an `'update_data'` event with the data.
- **Logging**: Outputs the action to the console.

### Error Handling 🚨

```javascript
socket.on('error', (data) => {
  console.error('Error:', data);
});
```

- **Event Listener**: Listens for `'error'` events from the server.
- **Logging**: Outputs any errors received to the console for debugging purposes.

---

## Usage Instructions 🛠️

1. **Open the Interface**:
   - Open `test_interface.html` in a web browser.
   - Ensure the server is running and accessible at `http://localhost:4000`.

2. **Register a Fake Session**:
   - Navigate to the **"Register Fake Session"** section.
   - **Enter** a unique **Device ID** (e.g., `device123`).
   - **Enter** a **Session Name** (e.g., `TestSession`).
   - **Click** on **"Register Fake Session"**.
   - Upon success, a message is logged to the console.

3. **Update Fake Data**:
   - Navigate to the **"Update Fake Data"** section.
   - **Enter** the **Device ID** used during registration.
   - **Enter** a **Key** (e.g., `position`, `status`).
   - **Enter** a **Value** corresponding to the key.
   - **Click** on **"Update Fake Data"**.
   - The data is sent to the server, and a confirmation is logged.

4. **Monitor the Server**:
   - Check the server console or logs to see the received data and any processing.

5. **Handle Errors**:
   - Any errors emitted by the server are displayed in the browser's console.

---

## Integration with Backend 🔗

- **Event Handlers in `app.py`**:
  - **`'register'` Event**: Processes session registration.
  - **`'update_data'` Event**: Handles data updates for sessions.
- **Session Management**:
  - The server maintains session data, which can be viewed or manipulated further.
- **Testing Server Logic**:
  - This interface helps ensure that the server correctly handles client connections, data updates, and session management.
