# 📄 Documentation for `main.js`

---

**File Path**: `./src/main.js`

---

## Introduction

The `main.js` file serves as the entry point for the Vue.js frontend application. It is responsible for initializing the Vue app, setting up global configurations, establishing a WebSocket connection with the backend server using Socket.IO, and mounting the app to the DOM.

---

## Table of Contents

1. [Import Statements](#import-statements)
2. [Initialize Socket.IO Client](#initialize-socketio-client)
3. [Socket.IO Event Handling](#socketio-event-handling)
   - [On Connect](#on-connect)
   - [On Disconnect](#on-disconnect)
   - [Before Unload Event](#before-unload-event)
4. [Create Vue Application](#create-vue-application)
5. [Global Socket Provision](#global-socket-provision)
6. [Router Configuration](#router-configuration)
7. [Mounting the App](#mounting-the-app)
8. [Summary](#summary)

---

## Import Statements

```javascript
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { io } from 'socket.io-client';
import './assets/main.css';
```

- **`createApp`**: Function from Vue.js to create a new application instance.
- **`App`**: The root component of the Vue application (`App.vue`).
- **`router`**: Vue Router instance for handling navigation.
- **`io`**: Socket.IO client library for real-time communication.
- **`main.css`**: Main CSS file for global styles.

---

## Initialize Socket.IO Client

```javascript
const socket = io();
```

- Creates a new Socket.IO client instance.
- Connects to the backend server (defaults to the server that served the page).

---

## Socket.IO Event Handling

### On Connect

```javascript
socket.on('connect', () => {
  console.log('Vue connected to server');
  socket.emit('register_vue');
});
```

- **Event**: Listens for the `connect` event.
- **Action**:
  - Logs a message indicating a successful connection.
  - Emits a `register_vue` event to the server to register the Vue client.

### On Disconnect

```javascript
socket.on('disconnect', () => {
  console.log('Vue disconnected from server');
});
```

- **Event**: Listens for the `disconnect` event.
- **Action**:
  - Logs a message indicating that the client has disconnected.

### Before Unload Event

```javascript
window.addEventListener('beforeunload', () => {
  socket.disconnect();
});
```

- Ensures the Socket.IO connection is properly closed when the user leaves the page.
- Prevents potential issues with lingering connections.

---

## Create Vue Application

```javascript
const app = createApp(App);
```

- Initializes the Vue application with the root component `App`.

---

## Global Socket Provision

```javascript
app.config.globalProperties.$socket = socket;
app.provide('socket', socket);
```

- **`app.config.globalProperties.$socket`**:
  - Adds the socket instance to the global properties.
  - Accessible in components via `this.$socket`.
- **`app.provide('socket', socket)`**:
  - Provides the socket instance to the dependency injection system.
  - Components can inject it using the `inject('socket')` function.

---

## Router Configuration

```javascript
app.use(router);
```

- Integrates the Vue Router into the application.
- Enables navigation between different views and components.

---

## Mounting the App

```javascript
app.mount('#app');
```

- Mounts the Vue application to the DOM element with the ID `app`.

---

## Summary

- **Entry Point**: `main.js` bootstraps the Vue application.
- **Socket.IO**: Establishes a real-time WebSocket connection with the Flask backend (`app.py`).
- **Global Access**: Provides the Socket.IO client globally to all components.
- **Routing**: Configures the router for navigation.
- **Mounting**: Renders the application into the DOM.
