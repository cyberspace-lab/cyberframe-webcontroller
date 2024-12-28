# InactiveSessionDetail.vue Documentation 📄

## Introduction

The `InactiveSessionDetail.vue` component is a Vue.js single-file component that displays the details of an **inactive session** in the application. This component allows users to:

- View session details such as session name, device ID, start time, and last ping time.
- Display session data excluding certain keys.
- Visualize the session's positions on a map using the `LatestPositions` component.
- Save the session data as a JSON file.
- Delete the inactive session.
  
This component interacts with a server via Socket.IO to fetch and handle session data.

---

## Table of Contents

1. [Template Structure](#template-structure)
2. [Script Explanation](#script-explanation)
   - [Props](#props)
   - [Components](#components)
   - [Data Properties](#data-properties)
   - [Computed Properties](#computed-properties)
   - [Methods](#methods)
   - [Lifecycle Hooks](#lifecycle-hooks)

---

## Template Structure

```html
<template>
  <div class="detail-container" v-if="application">
    <div class="left">
      <!-- Session Details -->
      <div>
        <template v-if="session">
          <p class="session-name">{{ session.session_name }}</p>
          <p class="device-id">DEVICE ID: {{ deviceId }}</p>
          <div class="session-time-container">
            <p class="session-time">
              Start Time: {{ new Date(session.start_time * 1000).toLocaleString() }}
            </p>
            <p class="session-time2">
              Last Ping: {{ new Date(session.last_ping * 1000).toLocaleString() }}
            </p>
          </div>
          <div class="button-container">
            <button class="save-button" @click="saveSessionAsJson">
              SAVE SESSION AS JSON 💾
            </button>
            <button class="back-button" @click="goToInactiveSessions">
              BACK TO INACTIVE SESSIONS
            </button>
          </div>
        </template>
        <template v-else>
          <p>Session with device {{ deviceId }} not connected.</p>
        </template>
      </div>

      <!-- Map Display -->
      <div class="map">
        <LatestPositions
          v-if="shouldRenderLatestPositions"
          :positions="parsedPositions"
          :mapUrl="currentMapUrl"
          :realWidth="realMapWidth"
          :realHeight="realMapHeight"
          :maxWidth="540"
          :maxHeight="680"
          :offsetX="mapOffsetX"
          :offsetY="mapOffsetY"
          :offsetRot="mapOffsetRotation"
        />
      </div>
    </div>

    <div class="right">
      <!-- Delete Session Button -->
      <button class="delete-button" @click="deleteSession">
        DELETE SESSION 🗑️
      </button>

      <!-- Session Data -->
      <div class="inactive-session-data">
        <h1 class="container-title">Session Data</h1>
        <div
          v-for="(values, key) in filteredSessionData"
          :key="key"
          class="session-data-item"
        >
          <div class="key-value-header" @click="toggleShowAllValues(key)">
            <h3 class="key-value-header-name">{{ key }}: </h3>
            <span class="key-value-header-value">{{ values[0] }}</span>
          </div>
          <div v-if="showAllValuesToggle[key]" class="values-container">
            <div
              v-for="(value, index) in values.slice(1)"
              :key="index"
              class="value-item"
            >
              {{ value }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else>
    <p class="no-sessions-text">No application selected or application not found.</p>
  </div>
</template>
```

### Explanation

- **Session Details**: Displays the session's name, device ID, start time, and last ping time.
- **Map Display**: Uses the `LatestPositions` component to visualize position data on a map.
- **Delete Session Button**: Provides an option to delete the inactive session.
- **Session Data**: Lists session data entries, allowing users to expand and view all values.

---

## Script Explanation

```javascript
<script>
import config from '@/config.json';
import { reactive } from 'vue';
import LatestPositions from './LatestPositions.vue';

export default {
  name: 'inactivesessiondetail',
  props: ['deviceId'],
  components: {
    LatestPositions,
  },
  data() {
    return {
      session: null,
      applications: config.applications,
      sessionData: {},
      showAllValuesToggle: reactive({}),
    };
  },
  computed: {
    // Computed properties
  },
  methods: {
    // Methods
  },
  mounted() {
    // Lifecycle hook
  },
  beforeUnmount() {
    // Lifecycle hook
  },
};
</script>
```

### Props

- `deviceId`: The unique identifier for the device/session. Passed as a prop.

### Components

- `LatestPositions`: Custom component used to display position data on a map.

### Data Properties

- `session`: Holds the session data retrieved from the server.
- `applications`: Application configurations imported from `config.json`.
- `sessionData`: Contains data entries related to the session.
- `showAllValuesToggle`: Reactive object to manage the visibility of additional data entries.

### Computed Properties

#### 1. `application`

Determines the current application's configuration based on the session's `session_name`.

```javascript
application() {
  if (this.session) {
    return this.applications[this.session.session_name] || null;
  }
  return null;
}
```

#### 2. `parsedPositions`

Parses the position data from `sessionData`.

```javascript
parsedPositions() {
  return this.sessionData.position.map(position => JSON.parse(position));
}
```

#### 3. `filteredSessionData`

Filters out `position` and `context` keys from `sessionData`.

```javascript
filteredSessionData() {
  return Object.fromEntries(
    Object.entries(this.sessionData).filter(([key]) => key !== 'position' && key !== 'context')
  );
}
```

#### 4. `currentLevelID`

Extracts the current level ID from the parsed positions.

```javascript
currentLevelID() {
  return this.parsedPositions.length > 0 ? this.parsedPositions[0][0].levelID : null;
}
```

#### 5. `currentMapUrl`

Gets the map URL for the current level ID from the application's configuration.

```javascript
currentMapUrl() {
  if (!this.application || !this.application.levels || !this.currentLevelID) return null;
  const levelMap = this.application.levels.find((level) => level[this.currentLevelID]);
  return levelMap ? levelMap[this.currentLevelID].url : '';
}
```

#### 6. `realMapWidth` & `realMapHeight`

Retrieve the real dimensions of the map for accurate scaling.

```javascript
realMapWidth() {
  // Similar logic for realMapHeight
}
```

#### 7. `shouldRenderLatestPositions`

Determines whether the `LatestPositions` component should be rendered.

```javascript
shouldRenderLatestPositions() {
  return (
    this.application &&
    this.application.levels &&
    Array.isArray(this.application.levels) &&
    this.application.receivers &&
    this.application.receivers.some(receiver => receiver.position)
  );
}
```

#### 8. `mapOffsetX`, `mapOffsetY`, `mapOffsetRotation`

Provide offset values for map positioning.

---

### Methods

#### 1. `goToInactiveSessions`

Navigates back to the inactive sessions list.

```javascript
goToInactiveSessions() {
  this.$router.push('/inactivesessions');
}
```

#### 2. `handleInactiveSession`

Handles the `inactive_session` event from the server and updates the session data.

```javascript
handleInactiveSession(data) {
  if (this.deviceId != data.device_id) return;
  this.session = data.session;
  this.sessionData = data.session.data;
  // Initialize showAllValuesToggle keys
}
```

#### 3. `toggleShowAllValues`

Toggles the visibility of all values for a specific session data key.

```javascript
toggleShowAllValues(key) {
  this.showAllValuesToggle[key] = !this.showAllValuesToggle[key];
}
```

#### 4. `handleUnityConnected`

When the Unity application connects (making the session active), redirects to the active session detail page.

```javascript
handleUnityConnected(data) {
  if (this.deviceId != data.device_id) return;
  console.log('Unity app connected from server');
  this.session = null;
  this.sessionData = {};
  this.showAllValuesToggle = {};
  this.$router.push('/activesessiondetail/' + this.deviceId);
}
```

#### 5. `emitGetInactiveSession`

Emits an event to fetch the inactive session data from the server.

```javascript
emitGetInactiveSession() {
  this.$socket.emit('get_inactive_session', { device_id: this.deviceId });
}
```

#### 6. `deleteSession`

Prompts the user for confirmation and emits a request to delete the session from the server.

```javascript
deleteSession() {
  if (confirm("Are you sure you want to delete this session?")) {
    this.$socket.emit('delete_session', { device_id: this.deviceId });
    this.$router.push({ name: 'inactivesessions' });
  }
}
```

#### 7. `saveSessionAsJson`

Allows the user to save the session data as a JSON file.

```javascript
saveSessionAsJson() {
  if (this.session) {
    const formattedSession = {
      ...this.session,
      start_time: new Date(this.session.start_time * 1000).toLocaleString(),
      last_ping: new Date(this.session.last_ping * 1000).toLocaleString()
    };
    // Create a Blob and trigger download
  } else {
    console.warn('No session data available to save.');
  }
}
```

---

### Lifecycle Hooks

#### 1. `mounted`

Executed when the component is mounted. Sets up socket listeners.

```javascript
mounted() {
  if (this.$socket.connected) {
    this.emitGetInactiveSession();
  } else {
    this.$socket.on('connect', this.emitGetInactiveSession);
  };
  this.$socket.on('inactive_session', this.handleInactiveSession);
  this.$socket.on('unity_connected', this.handleUnityConnected);
}
```

#### 2. `beforeUnmount`

Executed before the component is destroyed. Removes socket listeners.

```javascript
beforeUnmount() {
  this.$socket.off('inactive_session', this.handleInactiveSession);
  this.$socket.off('unity_connected', this.handleUnityConnected);
  this.$socket.off('connect', this.emitGetInactiveSession);
}
```
