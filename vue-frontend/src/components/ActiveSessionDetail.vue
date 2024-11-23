<template>
  <div class="detail-container" v-if="application">

    <div class="left">

      <div>
        <template v-if="session">
          <p class="session-name">{{ session.session_name }}</p>
          <p class="device-id">DEVICE ID: {{ deviceId }}</p>
          <div class="session-time-container">
            <p class="session-time">Start Time: {{ new Date(session.start_time * 1000).toLocaleString() }}</p>
            <p class="session-time2">Last Ping: {{ new Date(session.last_ping * 1000).toLocaleString() }}</p>
          </div>
          <div class="button-container">
            <button class="save-button" @click="saveSessionAsJson">SAVE SESSION AS JSON</button>
            <button class="back-button" @click="goToActiveSessions">BACK TO ACTIVE SESSIONS</button>
          </div>
        </template>
        <template v-else>
          <p>Session with device {{ this.deviceId }} not connected.</p>
        </template>
      </div>
      
      <div class="map">
      <LatestPositions
        v-if="shouldRenderLatestPositions"
        :positions="parsedPositions"
        :mapUrl="currentMapUrl"
        :realWidth="realMapWidth" 
        :realHeight="realMapHeight"
        :maxWidth="600"
        :maxHeight="800"
      />
      </div>

    </div>

    <div class="right">

    <div class="control-panel">
        <h1 class="container-title">{{ application.name }} Control Panel</h1>
        <div class="command-buttons-container">
          <div class="command" v-for="(button, index) in application.controlButtons" :key="index">
          <template v-if="button.requiresInput">
            <input 
              v-model="dynamicInputs[index]" 
              :placeholder="button.inputPlaceholder || 'ENTER VALUE'" 
              class="command-input"
            />
          </template>
          <button class="command-button" @click="handleButtonClick(button, dynamicInputs[index])">
            {{ button.title }}
          </button>
        </div>
        </div>
      </div>

    <div class="session-data">
      <h1 class="container-title">Session Data</h1>
      <div v-for="(values, key) in filteredSessionData" :key="key" class="session-data-item">
        <div class="key-value-header" @click="toggleShowAllValues(key)">
          <h3 class="key-value-header-name">{{ key }}: </h3>
          <span class="key-value-header-value">{{ values[0] }}</span>
        </div>
        <div v-if="showAllValuesToggle[key]" class="values-container">
          <div v-for="(value, index) in values.slice(1)" :key="index" class="value-item">{{ value }}</div>
        </div>
      </div>
    </div>

  </div>

  </div>

  <div v-else>
    <p>No application selected or application not found.</p>
  </div>
</template>
  
<script>
  import config from '@/config.json';
  import { reactive } from 'vue';
  import LatestPositions from './LatestPositions.vue';

  export default {
    name: 'activesessiondetail',
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
        dynamicInputs: []
      };
    },
    computed: {
      application() {
        if (this.session) {
          return this.applications[this.session.session_name] || null;
        }
        return null;
      },
      parsedPositions() {
        return this.sessionData.position.map(position => JSON.parse(position));
      },
      filteredSessionData() {
        return Object.fromEntries(
          Object.entries(this.sessionData).filter(([key]) => key !== 'position')
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
        return (
          this.application && 
          this.application.levels && 
          Array.isArray(this.application.levels) &&
          this.application.receivers && 
          this.application.receivers.some(receiver => receiver.position)
        );
      }
    },
    methods: {
      goToActiveSessions() {
       this.$router.push('/activesessions');
      },

      handleButtonClick(button, inputValue) {
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
        this.showAllValuesToggle[key] = !this.showAllValuesToggle[key];
      },

      handleUnityDisconnected(data) {
        if (this.deviceId != data.device_id) return;
        console.log('Unity app disconnected from server');
        this.session = null;
        this.sessionData = {};
        this.showAllValuesToggle = {};
        this.$router.push('/inactivesessiondetail/' + this.deviceId);
      },
      
      handleSession(data) {
        if (this.deviceId != data.device_id) return;
        this.session = data.session;
        this.sessionData = data.session.data;

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
        if (this.deviceId != data.device_id) return;
        console.log('Received session data:', data);
        this.sessionData[data.key] = data.value;
      },

      emitGetActiveSession() {
        this.$socket.emit('get_active_session', { device_id: this.deviceId });
      },

      saveSessionAsJson() {
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
      this.$socket.off('active_session', this.handleSession);
      this.$socket.off('session_data_key_update', this.handleSessionDataKeyUpdate);
      this.$socket.off('unity_disconnected', this.handleUnityDisconnected);
      this.$socket.off('connect', this.emitGetActiveSession);
    }
  };
</script>