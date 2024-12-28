# 📄 Documentation for `ActiveSessions.vue`

---

## Table of Contents

1. [Overview](#overview)
2. [Template Structure](#template-structure)
   - [Banner Section](#banner-section)
   - [Active Sessions List](#active-sessions-list)
   - [No Active Sessions Message](#no-active-sessions-message)
3. [Script Section](#script-section)
   - [Data Properties](#data-properties)
   - [Methods](#methods)
     - [`goToInactiveSessions`](#goToInactiveSessions)
     - [`handleActiveSessionsUpdate`](#handleActiveSessionsUpdate)
   - [Lifecycle Hooks](#lifecycle-hooks)
     - [`mounted`](#mounted)
     - [`beforeUnmount`](#beforeUnmount)

---

## Overview

The **`ActiveSessions.vue`** file is a Vue.js component that displays a list of active sessions in a user-friendly interface. It allows users to view details of each active session and navigate to inactive sessions. This component utilizes Socket.IO for real-time communication with the backend server to fetch and update active session data.

---

## Template Structure

The template of the component is structured to display:

- A **banner** with a title and a button to view inactive sessions.
- A **list of active sessions**, each displaying session details and a link to view more details.
- A **message** when there are no active sessions available.

Let's break down each part.

### Banner Section

```vue
<div class="banner">
  <h1>Active Sessions</h1>
  <button class="banner-button" @click="goToInactiveSessions">
    VIEW INACTIVE SESSIONS
  </button>
</div>
```

- **Banner Title**: Displays the heading **"Active Sessions"**.
- **Button**: A button labeled **"VIEW INACTIVE SESSIONS"**.
  - **Event Handler**: On click, it calls the method `goToInactiveSessions` to navigate to the inactive sessions page.

### Active Sessions List

```vue
<div v-if="activeSessions && Object.keys(activeSessions).length > 0">
  <ul class="session-list">
    <li
      v-for="(session, deviceId) in activeSessions"
      :key="deviceId"
      class="session-item"
    >
      <router-link
        :to="{ name: 'activesessiondetail', params: { deviceId: deviceId } }"
        class="session-link"
      >
        <!-- Session Details -->
      </router-link>
    </li>
  </ul>
</div>
```

- **Conditional Rendering**: The list is displayed only if there are active sessions (`v-if` directive).
- **Session Items**: Iterates over `activeSessions` using `v-for`, generating a list item for each session.
- **Router Link**: Each session item is wrapped in a `router-link` to enable navigation to the session's detail page.
  - **Route Parameters**: Passes `deviceId` as a route parameter to the `ActiveSessionDetail` component.

#### Session Details

Inside the `router-link`:

```vue
<div class="session-link-title">
  <h5>{{ session.session_name }}</h5>
  <small class="session-link-device">DEVICE ID: {{ deviceId }}</small>
</div>
<div class="session-link-time">
  <small>
    Start Time: {{ new Date(session.start_time * 1000).toLocaleString() }}
  </small>
  <small class="session-link-last-ping">
    Last Ping: {{ new Date(session.last_ping * 1000).toLocaleString() }}
  </small>
</div>
<p class="view-detail">VIEW DETAIL →</p>
```

- **Session Name**: Displays the name of the session.
- **Device ID**: Shows the device ID associated with the session.
- **Start Time**: Converts the Unix timestamp `start_time` to a readable date and time.
- **Last Ping**: Converts the Unix timestamp `last_ping` to a readable date and time, indicating the last activity.
- **View Detail**: A prompt to view more details about the session.

### No Active Sessions Message

```vue
<div v-else>
  <p class="no-sessions-text">NO ACTIVE SESSIONS AVAILABLE</p>
</div>
```

- **Conditional Rendering**: Displayed when there are no active sessions.
- **Message**: Informs the user that no active sessions are available.

---

## Script Section

The script section defines the component's logic.

```javascript
export default {
  name: 'activesessions',
  data() {
    return {
      activeSessions: { }
    };
  },
  methods: {
    goToInactiveSessions() { /* ... */ },
    handleActiveSessionsUpdate(activeSessions) { /* ... */ },
  },
  mounted() { /* ... */ },
  beforeUnmount() { /* ... */ }
};
```

### Data Properties

- **`activeSessions`**: An object that holds the active sessions data received from the server.

### Methods

#### `goToInactiveSessions`

```javascript
goToInactiveSessions() {
  // Redirect to the InactiveSessions component
  this.$router.push('/inactivesessions');
},
```

- **Purpose**: Navigates the user to the inactive sessions view when the button is clicked.
- **Functionality**: Uses Vue Router to change the route to `/inactivesessions`.

#### `handleActiveSessionsUpdate`

```javascript
handleActiveSessionsUpdate(activeSessions) {
  // Update the activeSessions data when the 'active_sessions_update' event is received
  this.activeSessions = activeSessions;
},
```

- **Purpose**: Updates the `activeSessions` data property with the latest data from the server.
- **Parameters**:
  - **`activeSessions`**: The active sessions data received from the server via Socket.IO.

### Lifecycle Hooks

#### `mounted`

```javascript
mounted() {
  // Emit the 'get_active_sessions' event to request the active sessions data
  this.$socket.emit('get_active_sessions');
  this.$socket.on('active_sessions_update', this.handleActiveSessionsUpdate);
},
```

- **Purpose**: Executes when the component is mounted onto the DOM.
- **Functionality**:
  - **Request Active Sessions**: Emits a `'get_active_sessions'` event through the `Socket.IO` connection to request the current active sessions from the server.
  - **Set Up Listener**: Listens for the `'active_sessions_update'` event to receive updates from the server.
  - **Event Binding**: The `handleActiveSessionsUpdate` method is set as the callback for handling incoming data.

#### `beforeUnmount`

```javascript
beforeUnmount() {
  // Remove the event listener when the component is destroyed
  this.$socket.off('active_sessions_update', this.handleActiveSessionsUpdate);
}
```

- **Purpose**: Executes right before the component is destroyed.
- **Functionality**:
  - **Cleanup**: Removes the `'active_sessions_update'` event listener to prevent memory leaks and unintended behavior.
