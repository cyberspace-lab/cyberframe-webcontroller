# 📄 Documentation for `ActiveSessionDetail.vue`

**Filename**: `ActiveSessionDetail.vue`

---

## 🌟 Overview

The `ActiveSessionDetail.vue` component is a **Vue.js** component designed to display detailed information about an **active session** within the application. This component provides a rich user interface that allows users to:

- View session details such as session name, device ID, start time, and last ping.
- Interact with a map displaying the latest positions using the `LatestPositions` component.
- Access a control panel with dynamic buttons to send commands to the server.
- View and interact with session data, including toggling the visibility of historical values.

---

## 📖 Table of Contents

1. [Template Structure](#template-structure)
2. [Script Details](#script-details)
   - [Imports](#imports)
   - [Props](#props)
   - [Components](#components)
   - [Data Properties](#data-properties)
   - [Computed Properties](#computed-properties)
   - [Methods](#methods)
   - [Lifecycle Hooks](#lifecycle-hooks)
3. [Component Functionality](#component-functionality)
4. [Socket Event Handling](#socket-event-handling)

---

## 📝 Template Structure

The template of `ActiveSessionDetail.vue` consists of several key parts:

1. **Session Details and Map Display**

   - Displays session information like session name and device ID.
   - Provides buttons to save session data and navigate back.
   - Renders a map using the `LatestPositions` component to show positions.

   ```html
   <div class="detail-container" v-if="application">
     <div class="left">
       <!-- Session Details -->
       <!-- Map Display using LatestPositions component -->
     </div>
     <!-- Control Panel and Session Data -->
   </div>
   ```

2. **Control Panel**

   - Dynamically generates buttons based on the `controlButtons` configuration from `config.json`.
   - Supports buttons that require user input.

   ```html
   <div class="control-panel">
     <h1 class="container-title">{{ application.name }} Control Panel</h1>
     <div class="command-buttons-container">
       <div class="command" v-for="(button, index) in filteredControlButtons" :key="index">
         <!-- Input for buttons requiring input -->
         <button class="command-button" @click="handleButtonClick(button, dynamicInputs[index])">
           {{ button.title }}
         </button>
       </div>
     </div>
   </div>
   ```

3. **Session Data Display**

   - Shows session data and allows toggling the display of historical values.

   ```html
   <div class="session-data">
     <h1 class="container-title">Session Data</h1>
     <div v-for="(values, key) in filteredSessionData" :key="key" class="session-data-item">
       <!-- Data Key and Latest Value -->
       <div v-if="showAllValuesToggle[key]" class="values-container">
         <!-- List of historical values -->
       </div>
     </div>
   </div>
   ```

4. **No Application Found Message**

   - Displays a message if no application is selected or found.

   ```html
   <div v-else>
     <p class="no-sessions-text">No application selected or application not found.</p>
   </div>
   ```

---

## 📜 Script Details

### 📥 Imports

- `config` from `@/config.json`: Contains application configurations.
- `reactive` from `vue`: Used for reactive data properties.
- `LatestPositions` component: Used to display positions on a map.

  ```javascript
  import config from '@/config.json';
  import { reactive } from 'vue';
  import LatestPositions from './LatestPositions.vue';
  ```

### 📋 Props

- `deviceId`: The device ID of the session to display details for.

  ```javascript
  props: ['deviceId'],
  ```

### 🧩 Components

- Registers `LatestPositions` for use within the template.

  ```javascript
  components: {
    LatestPositions,
  },
  ```

### 🔢 Data Properties

- **session**: Holds the session details fetched from the server.
- **applications**: Contains application configurations from `config.json`.
- **sessionData**: Stores data specific to the session, such as positions and context.
- **showAllValuesToggle**: Reactively manages the toggling of historical data display for each key.
- **dynamicInputs**: Stores user inputs for command buttons that require input.

  ```javascript
  data() {
    return {
      session: null,
      applications: config.applications,
      sessionData: {},
      showAllValuesToggle: reactive({}),
      dynamicInputs: [],
    };
  },
  ```

### 🧮 Computed Properties

1. **application**

   - Retrieves the current application configuration based on the session's `session_name`.
  
   ```javascript
   application() {
     if (this.session) {
       return this.applications[this.session.session_name] || null;
     }
     return null;
   },
   ```

2. **filteredControlButtons**

   - Filters the control buttons based on the current context.
   - Only displays buttons that are relevant to the current context.

   ```javascript
   filteredControlButtons() {
     // Filtering logic based on button.context and this.currentContext
   },
   ```

3. **currentContext**

   - Parses the context data from `sessionData`.
  
   ```javascript
   currentContext() {
     if (!this.sessionData.context) return [];
     return this.sessionData.context.map(context => JSON.parse(context));
   },
   ```

4. **parsedPositions**

   - Parses the position data from `sessionData`.
  
   ```javascript
   parsedPositions() {
     return this.sessionData.position.map(position => JSON.parse(position));
   },
   ```

5. **filteredPositionsByLevelID**

   - Filters positions to only include those matching the `currentLevelID`.

   ```javascript
   filteredPositionsByLevelID() {
     // Logic to filter positions by currentLevelID
   },
   ```

6. **filteredSessionData**

   - Filters out `position` and `context` from session data for display.
  
   ```javascript
   filteredSessionData() {
     return Object.fromEntries(
       Object.entries(this.sessionData).filter(([key]) => key !== 'position' && key !== 'context')
     );
   },
   ```

7. **currentLevelID**

   - Retrieves the current level ID from the parsed positions.
  
   ```javascript
   currentLevelID() {
     return this.parsedPositions.length > 0 ? this.parsedPositions[0][0].levelID : null;
   },
   ```

8. **Map Properties**

   - **currentMapUrl**, **realMapWidth**, **realMapHeight**
     - Retrieves map URL and dimensions based on the current level ID.
   - **mapOffsetX**, **mapOffsetY**, **mapOffsetRotation**
     - Retrieves map offsets and rotation if available.

   ```javascript
   currentMapUrl() {
     // Logic to retrieve map URL
   },
   realMapWidth() {
     // Logic to retrieve map width
   },
   // ... Similar for other map properties
   ```

9. **shouldRenderLatestPositions**

   - Determines whether to render the `LatestPositions` component.

   ```javascript
   shouldRenderLatestPositions() {
     // Returns true if positions should be rendered
   },
   ```

### 🔧 Methods

1. **goToActiveSessions**

   - Navigates back to the active sessions list.

   ```javascript
   goToActiveSessions() {
     this.$router.push('/activesessions');
   },
   ```

2. **handleButtonClick**

   - Handles clicks on control buttons.
   - Emits a command to the server with the button's payload and user input.

   ```javascript
   handleButtonClick(button, inputValue) {
     // Constructs the payload and emits 'send_command'
   },
   ```

3. **toggleShowAllValues**

   - Toggles the display of all historical values for a given key.

   ```javascript
   toggleShowAllValues(key) {
     this.showAllValuesToggle[key] = !this.showAllValuesToggle[key];
   },
   ```

4. **handleUnityDisconnected**

   - Handles the event when the Unity application disconnects.

   ```javascript
   handleUnityDisconnected(data) {
     if (this.deviceId != data.device_id) return;
     // Clears session data and redirects to inactive session detail
   },
   ```

5. **handleSession**

   - Handles the 'active_session' event from the server.
   - Updates session details and data.

   ```javascript
   handleSession(data) {
     if (this.deviceId != data.device_id) return;
     this.session = data.session;
     this.sessionData = data.session.data;
     // Initializes showAllValuesToggle for new data keys
   },
   ```

6. **handleSessionDataKeyUpdate**

   - Updates a specific session data key when receiving real-time updates.

   ```javascript
   handleSessionDataKeyUpdate(data) {
     if (this.deviceId != data.device_id) return;
     this.sessionData[data.key] = data.value;
   },
   ```

7. **emitGetActiveSession**

   - Requests the active session details from the server.

   ```javascript
   emitGetActiveSession() {
     this.$socket.emit('get_active_session', { device_id: this.deviceId });
   },
   ```

8. **saveSessionAsJson**

   - Saves the current session data as a JSON file.

   ```javascript
   saveSessionAsJson() {
     if (this.session) {
       // Creates a blob and triggers download
     } else {
       console.warn('No session data available to save.');
     }
   },
   ```

### 🔄 Lifecycle Hooks

1. **mounted**

   - Called when the component is mounted.
   - Sets up socket event listeners.

   ```javascript
   mounted() {
     if (this.$socket.connected) {
       this.emitGetActiveSession();
     } else {
       this.$socket.on('connect', this.emitGetActiveSession);
     };
     this.$socket.on('active_session', this.handleSession);
     this.$socket.on('session_data_key_update', this.handleSessionDataKeyUpdate);
     this.$socket.on('unity_disconnected', this.handleUnityDisconnected);
   },
   ```

2. **beforeUnmount**

   - Called before the component is destroyed.
   - Cleans up socket event listeners.

   ```javascript
   beforeUnmount() {
     this.$socket.off('active_session', this.handleSession);
     this.$socket.off('session_data_key_update', this.handleSessionDataKeyUpdate);
     this.$socket.off('unity_disconnected', this.handleUnityDisconnected);
     this.$socket.off('connect', this.emitGetActiveSession);
   },
   ```

---

## 🛠️ Component Functionality

- **Display Session Information**

  - Shows the session's name, device ID, start time, and last ping.
  
- **Map Visualization**

  - Uses the `LatestPositions` component to display positions on a map.
  - Dynamically adjusts based on the current level and map configuration.
  
- **Control Panel**

  - Generates control buttons from the `controlButtons` array in `config.json`.
  - Supports context-aware buttons and user input.
  - Sends commands to the server when buttons are clicked.

- **Session Data Display**

  - Displays session data keys and the latest value.
  - Allows users to toggle the display of historical values.

---

## 🔌 Socket Event Handling

- **Events Emitted**

  - `send_command`: Sent when a control button is clicked to send a command to the server.
  - `get_active_session`: Requests the session details for the given `deviceId`.

- **Events Listened**

  - `connect`: When the socket connects, requests the active session.
  - `active_session`: Receives the session details from the server.
  - `session_data_key_update`: Updates specific session data keys in real-time.
  - `unity_disconnected`: Handles the disconnection of the Unity application.
