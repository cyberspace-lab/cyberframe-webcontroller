# 📄 Documentation for `InactiveSessions.vue` 📝

## Table of Contents

1. [Introduction](#introduction)
2. [Template Structure](#template-structure)
   - [Header Section](#header-section)
   - [Sessions List](#sessions-list)
   - [No Sessions Message](#no-sessions-message)
3. [Script Section](#script-section)
   - [Imports](#imports)
   - [Component Definition](#component-definition)
     - [Name](#name)
     - [Data](#data)
     - [Methods](#methods)
       - [`goToActiveSessions`](#gottoactivesessions)
       - [`handleInactiveSessionsUpdate`](#handleinactivesessionsupdate)
     - [Lifecycle Hooks](#lifecycle-hooks)
       - [`mounted`](#mounted)
       - [`beforeUnmount`](#beforeunmount)

---

## Introduction

The `InactiveSessions.vue` component is a Vue.js single-file component responsible for displaying a list of inactive sessions in the web application. It provides an interface for users to view inactive sessions, each session's details, and navigate back to the active sessions view.

---

## Template Structure

The template is the visual part of the component defined within the `<template>` tags. It consists of HTML-like syntax enhanced with Vue directives.

### Header Section

```html
<div class="banner">
  <h1>Inactive Sessions</h1>
  <button class="banner-button" @click="goToActiveSessions">VIEW ACTIVE SESSIONS</button>
</div>
```

- **Banner**: Displays the title **"Inactive Sessions"**.
- **Button**: Navigates to the active sessions view when clicked.

### Sessions List

```html
<div v-if="inactiveSessions && Object.keys(inactiveSessions).length > 0">
  <ul class="session-list">
    <li v-for="(session, deviceId) in inactiveSessions" :key="deviceId" class="session-item">
      <router-link
        :to="{ name: 'inactivesessiondetail', params: { deviceId: deviceId } }"
        class="session-link"
      >
        <!-- Session Details -->
      </router-link>
    </li>
  </ul>
</div>
```

- **Conditional Rendering**: The list is displayed only if there are inactive sessions available.
- **`v-for` Directive**: Iterates over each session in `inactiveSessions`.
- **`router-link`**: Vue Router component used to navigate to the inactive session's detail page.

#### Session Details Inside `router-link`

```html
<div class="session-link-title">
  <h5>{{ session.session_name }}</h5>
  <small class="session-link-device">DEVICE ID: {{ deviceId }}</small>
</div>
<div class="session-link-time">
  <small>Start Time: {{ new Date(session.start_time * 1000).toLocaleString() }}</small>
  <small class="session-link-last-ping">
    Last Ping: {{ new Date(session.last_ping * 1000).toLocaleString() }}
  </small>
</div>
<p class="view-detail">VIEW DETAIL →</p>
```

- **Session Name**: Displayed in a heading.
- **Device ID**: Displayed under the session name.
- **Start Time and Last Ping**: Converted from UNIX timestamp to local string format.
- **View Detail**: A prompt to indicate that clicking will show more details.

### No Sessions Message

```html
<div v-else>
  <p class="no-sessions-text">NO INACTIVE SESSIONS AVAILABLE</p>
</div>
```

- **Conditional Rendering**: Displayed when there are no inactive sessions.
- **Message**: Informs the user that there are no inactive sessions to display.

---

## Script Section

The script section contains the logic of the component and is defined within `<script>` tags.

### Component Definition

#### Name

```javascript
name: 'inactivesessions',
```

- **Component Name**: Declared as `'inactivesessions'`.

#### Data

```javascript
data() {
  return {
    inactiveSessions: {}
  };
},
```

- **`inactiveSessions`**: An object that will hold the inactive sessions data fetched from the server.

#### Methods

Methods define the functions that can be used within the component.

##### `goToActiveSessions`

```javascript
goToActiveSessions() {
  // Redirect to active sessions page
  this.$router.push('/activesessions');
},
```

- **Purpose**: Navigates the user to the active sessions page.
- **Usage**: Triggered when the user clicks the **"VIEW ACTIVE SESSIONS"** button.

##### `handleInactiveSessionsUpdate`

```javascript
handleInactiveSessionsUpdate(inactiveSessions) {
  // Update inactive sessions
  this.inactiveSessions = inactiveSessions;
},
```

- **Purpose**: Updates the `inactiveSessions` data property with the latest data from the server.
- **Usage**: Called when the component receives an `inactive_sessions_update` event via WebSocket.

#### Lifecycle Hooks

Lifecycle hooks are special functions that run at specific points in a component's life.

##### `mounted`

```javascript
mounted() {
  // Get inactive sessions
  this.$socket.emit('get_inactive_sessions');

  // Listen for inactive sessions update
  this.$socket.on('inactive_sessions_update', this.handleInactiveSessionsUpdate);
},
```

- **Purpose**: Executes when the component is mounted to the DOM.
- **Actions**:
  - Emits a **`get_inactive_sessions`** event to request the current list of inactive sessions from the server.
  - Sets up a listener for the **`inactive_sessions_update`** event to receive updates.

##### `beforeUnmount`

```javascript
beforeUnmount() {
  // Remove socket listener
  this.$socket.off('inactive_sessions_update', this.handleInactiveSessionsUpdate);
}
```

- **Purpose**: Executes right before the component is destroyed.
- **Actions**:
  - Removes the WebSocket event listener to prevent memory leaks.
