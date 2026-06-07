<template>
  <div v-if="application" class="detail-grid">

    <!-- LEFT: session summary + map -->
    <div>
      <div class="panel">
        <template v-if="session">
          <div class="session-summary">
            <p class="session-summary-name">{{ session.session_name }}</p>
            <p class="session-summary-device">DEVICE <b>{{ deviceId }}</b></p>
            <div class="session-summary-meta">
              <div class="meta-cell">
                <span class="label">Start time</span>
                <span class="value">{{ formatTime(session.start_time) }}</span>
              </div>
              <div class="meta-cell">
                <span class="label">Last ping</span>
                <span class="value">{{ formatTime(session.last_ping) }}</span>
              </div>
            </div>
          </div>
          <div class="detail-actions">
            <button class="btn cyan" @click="saveSessionAsJson">Save as JSON</button>
            <button class="btn ghost" @click="goToActiveSessions">← Back</button>
          </div>
        </template>
        <template v-else>
          <p class="session-summary-device">Session with device {{ deviceId }} not connected.</p>
        </template>
      </div>

      <div v-if="shouldRenderLatestPositions" class="map-frame">
        <LatestPositions
          :positions="filteredPositionsByLevelID"
          :mapUrl="currentMapUrl"
          :realWidth="realMapWidth"
          :realHeight="realMapHeight"
          :maxWidth="520"
          :maxHeight="640"
          :offsetX="mapOffsetX"
          :offsetY="mapOffsetY"
          :offsetRot="mapOffsetRotation"
        />
      </div>
    </div>

    <!-- RIGHT: control panel + session data -->
    <div class="detail-grid-right">
      <div class="panel">
        <h2 class="panel-title">{{ application.name }} Control Panel</h2>
        <div class="command-grid">
          <div class="command" v-for="(button, index) in filteredControlButtons" :key="button.title + '_' + index">
            <input
              v-if="button.requiresInput"
              v-model="dynamicInputs[index]"
              :placeholder="button.inputPlaceholder || 'Enter value'"
              class="field"
            />
            <button class="command-button" @click="handleButtonClick(button, dynamicInputs[index])">
              {{ button.title }}
            </button>
          </div>
        </div>
      </div>

      <div class="panel">
        <h2 class="panel-title">Session Data</h2>
        <div class="session-data-list">
          <div v-for="(values, key) in filteredSessionData" :key="key" class="session-data-item">
            <div class="kv-header" @click="toggleShowAllValues(key)">
              <span class="kv-key">{{ key }}</span>
              <span class="kv-value">{{ values[0] }}</span>
              <span class="kv-caret" :class="{ open: showAllValuesToggle[key] }">▶</span>
            </div>
            <div v-if="showAllValuesToggle[key]" class="kv-history">
              <div
                v-for="(value, index) in values.slice(1)"
                :key="key + '_' + index"
                class="kv-history-item"
              >{{ value }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>

  <div v-else class="empty-state">
    <span class="glyph">⊘</span>
    <p>No application selected or application not found</p>
  </div>
</template>
  
<script>
  import config from '@/config.json';
  import { reactive } from 'vue';
  import LatestPositions from './LatestPositions.vue';

  export default {
    name: 'activesessiondetail',
    props: ['deviceId', 'sessionName'],
    components: {
      LatestPositions,
    },
    data() {
      return {
        session: null,
        applications: config.applications,
        sessionData: {},
        showAllValuesToggle: reactive({}),
        dynamicInputs: []
      };
    },
    computed: {
      application() {
        // Find the current application based on session name
        if (this.session) {
          return this.applications[this.session.session_name] || null;
        }
        return null;
      },
      filteredControlButtons() {
        // Filter buttons based on current context
        if (!this.application || !this.application.controlButtons) return [];
        if (!this.currentContext || this.currentContext.length === 0) return this.application.controlButtons;

        return this.application.controlButtons.filter(button => {
          if (!button.context || button.context.length === 0) return true;
          
          const buttonContexts = Array.isArray(button.context) ? button.context : button.context.split(',');
          const currentContexts = Array.isArray(this.currentContext[0]) ? this.currentContext[0] : this.currentContext[0].split(',');

          let found = false;

          for (let i = 0; i < buttonContexts.length; i++) {
            const ctx = buttonContexts[i];

            // Loop through the current context and compare each element with the button context
            for (let j = 0; j < currentContexts.length; j++) {
              const context = currentContexts[j];
    
              if (context == ctx) {
                found = true;
                break;
              }
            }

            if (found) {
              break;
            }
          }

          return found;
        });
      },
      currentContext() {
        if (!this.sessionData.context) return [];

        return this.sessionData.context.map(context => JSON.parse(context));
      },
      parsedPositions() {
        return this.sessionData.position.map(position => JSON.parse(position));
      },
      filteredPositionsByLevelID() {
        // Filter positions based on current level ID
        for (let i = 0; i < this.parsedPositions.length; i++) {
          const innerArray = this.parsedPositions[i];

          if (Array.isArray(innerArray)) {
            for (let j = innerArray.length - 1; j >= 0; j--) {
              const position = innerArray[j];
              // Remove positions that don't match currentLevelID
              if (position.levelID !== this.currentLevelID) {
                innerArray.splice(j, 1);
              }
            }
          }
        }
        return this.parsedPositions;
      },
      filteredSessionData() {
        // Filter session data, excluding position and context
        return Object.fromEntries(
          Object.entries(this.sessionData).filter(([key]) => key !== 'position' && key !== 'context')
        );
      },
      currentLevelID() {
        return this.parsedPositions.length > 0 ? this.parsedPositions[0][0].levelID : null;
      },
      currentMapUrl() {
        if (!this.application || !this.application.levels || !this.currentLevelID) return null;

        const levelMap = this.application.levels.find((level) => level[this.currentLevelID]);
        return levelMap ? levelMap[this.currentLevelID].url : '';
      },
      realMapWidth() {
        if (!this.application || !this.application.levels || !this.currentLevelID) return null;

        const levelMap = this.application.levels.find((level) => level[this.currentLevelID]);
        return levelMap && levelMap[this.currentLevelID] ? levelMap[this.currentLevelID].realWidth : null;
      },
      realMapHeight() {
        if (!this.application || !this.application.levels || !this.currentLevelID) return null;

        const levelMap = this.application.levels.find((level) => level[this.currentLevelID]);
        return levelMap && levelMap[this.currentLevelID] ? levelMap[this.currentLevelID].realHeight : null;
      },
      shouldRenderLatestPositions() {
        // Determine whether to render the LatestPositions component
        return (
          this.application && 
          this.application.levels && 
          Array.isArray(this.application.levels) &&
          this.application.receivers && 
          this.application.receivers.some(receiver => receiver.position)
        );
      },
      mapOffsetX() {
        if (!this.application || !this.application.levels || !this.currentLevelID) return null;

        const levelMap = this.application.levels.find((level) => level[this.currentLevelID]);
        return levelMap && levelMap[this.currentLevelID] ? levelMap[this.currentLevelID].mapOffsetX : null;
      },
      mapOffsetY() {
        if (!this.application || !this.application.levels || !this.currentLevelID) return null;

        const levelMap = this.application.levels.find((level) => level[this.currentLevelID]);
        return levelMap && levelMap[this.currentLevelID] ? levelMap[this.currentLevelID].mapOffsetY : null;
      },
      mapOffsetRotation() {
        if (!this.application || !this.application.levels || !this.currentLevelID) return null;

        const levelMap = this.application.levels.find((level) => level[this.currentLevelID]);
        return levelMap && levelMap[this.currentLevelID] ? levelMap[this.currentLevelID].mapOffsetRotation : null;
      }
    },
    methods: {
      formatTime(epochSeconds) {
        return new Date(epochSeconds * 1000).toLocaleString();
      },

      goToActiveSessions() {
        // Navigate back to the active sessions page
       this.$router.push('/activesessions');
      },

      handleButtonClick(button, inputValue) {
        // Emit a command to the server with the button's payload and user input
        if (!this.session) {
          console.error("Session not found");
          return;
        }

        const payload = {
          ...button.payload,
          parameters: {
            ...button.payload.parameters,
            userInput: inputValue
          }
        };

        this.$socket.emit('send_command', { sid: this.session.sid, payload });
      },

      toggleShowAllValues(key) {
        // Toggle the display of additional session data values
        this.showAllValuesToggle[key] = !this.showAllValuesToggle[key];
      },

      handleUnityDisconnected(data) {
        // Handle the Unity app disconnecting from the server
        if (this.deviceId != data.device_id) return;
        console.log('Unity app disconnected from server');
        this.session = null;
        this.sessionData = {};
        this.showAllValuesToggle = {};
        this.$router.push('/inactivesessiondetail/' + this.deviceId + "/" + this.sessionName);
      },
      
      handleSession(data) {
        // Handle receiving session data from the server
        if (this.deviceId != data.device_id) return;
        this.session = data.session;
        this.sessionData = data.session.data;

        // Initialize or cleanup toggles for session data display
        Object.keys(this.sessionData).forEach(key => {
          if (!(key in this.showAllValuesToggle)) {
            this.showAllValuesToggle[key] = false;
          }
        });

        Object.keys(this.showAllValuesToggle).forEach(key => {
          if (!(key in this.sessionData)) {
            delete this.showAllValuesToggle[key];
          }
        });
      },

      handleSessionDataKeyUpdate(data) {
        // Update specific session data key with real-time updates
        if (this.deviceId != data.device_id) return;
        console.log('Received session data:', data);
        this.sessionData[data.key] = data.value;
      },

      emitGetActiveSession() {
        // Request the active session details from the server
        this.$socket.emit('get_active_session', { device_id: this.deviceId, session_name: this.sessionName });
      },

      saveSessionAsJson() {
        // Save the current session data as a JSON file
        if (this.session) {
          const formattedSession = {
            ...this.session,
            start_time: new Date(this.session.start_time * 1000).toLocaleString(),
            last_ping: new Date(this.session.last_ping * 1000).toLocaleString()
          };

          const dataStr = JSON.stringify(formattedSession, null, 2);
          const blob = new Blob([dataStr], { type: 'application/json' });
          const url = URL.createObjectURL(blob);

          const link = document.createElement('a');
          link.href = url;
          link.download = `${this.session.session_name || 'session'}.json`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);

          URL.revokeObjectURL(url);
        } else {
          console.warn('No session data available to save.');
        }
      }
    },
    mounted() {
      // Register socket event listeners on component mount
      if (this.$socket.connected) {
        this.emitGetActiveSession();
      } else {
        this.$socket.on('connect', this.emitGetActiveSession);
      };

      this.$socket.on('active_session', this.handleSession);
      this.$socket.on('session_data_key_update', this.handleSessionDataKeyUpdate);
      this.$socket.on('unity_disconnected', this.handleUnityDisconnected);
    },
    beforeUnmount() {
      // Cleanup socket event listeners before the component is destroyed
      this.$socket.off('active_session', this.handleSession);
      this.$socket.off('session_data_key_update', this.handleSessionDataKeyUpdate);
      this.$socket.off('unity_disconnected', this.handleUnityDisconnected);
      this.$socket.off('connect', this.emitGetActiveSession);
    }
  };
</script>