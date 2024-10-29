<template>
  <div v-if="application">

    <div class="left">

      <div class="sessionDetail">
        <h1 class="title">Session Detail</h1>
        <template v-if="session">
          <p>Device ID: {{ deviceId }}</p>
          <p>Session Name: {{ session.session_name }}</p>
          <p>Start Time: {{ new Date(session.start_time * 1000).toLocaleString() }}</p>
          <p>Last Ping: {{ new Date(session.last_ping * 1000).toLocaleString() }}</p>
        </template>
        <template v-else>
          <p>Session with device {{ this.deviceId }} not connected.</p>
        </template>
      </div>
      
      <div class="controlPanel">
        <h1>{{ application.name }} Control Panel</h1>
        <button v-for="(button, index) in application.controlButtons" :key="index" @click="handleButtonClick(button)">
          {{ button.title }}
        </button>
      </div>
    </div>

    <div class="sessionData">
      <h1>Session Data</h1>
      <div v-for="(values, key) in sessionData" :key="key" class="sessionDataItem">
        <div class="key-value-header" @click="toggleShowAllValues(key)">
          <h3>{{ key }}: </h3>
          <span>{{ values[0] }}</span>
        </div>
        <div v-if="showAllValuesToggle[key]" class="values-container">
          <div v-for="(value, index) in values.slice(1)" :key="index" class="value-item">{{ value }}</div>
        </div>
      </div>
    </div>
    <button class="save-button" @click="saveSessionAsJson">Save session as JSON</button>
  </div>

  <div v-else>
    <h1>Session Detail</h1>
    <p>No application selected or application not found.</p>
  </div>
</template>
  
<script>
  import config from '@/config.json';
  import { reactive } from 'vue';

  export default {
    name: 'activesessiondetail',
    props: ['deviceId'],
    data() {
      return {
        session: null,
        applications: config.applications,
        sessionData: {},
        showAllValuesToggle: reactive({})
      };
    },
    computed: {
      application() {
        if (this.session) {
          return this.applications[this.session.session_name] || null;
        }
        return null;
      },
    },
    methods: {
      handleButtonClick(button) {
        if (!this.session) {
          console.error("Session not found");
          return;
        }
        this.$socket.emit('send_command', { sid: this.session.sid, payload: button.payload });
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

<style>
  .left {
    width: 47%;
    float: left;
    padding: 0px;
    margin-bottom: 20px;
  }
  
  .sessionDetail {
    height: 25vh;
    padding: 0px;
  }

  .title {
    margin-top: 0px;
  }

  .controlPanel {
    height: 60vh;
    border-width: thin;
    border-style: solid;
    border-radius: 10px;
  }

  .sessionData {
    width: 47%;
    height: 85vh;
    float: right;
    border-width: thin;
    border-style: solid;
    border-radius: 10px;
    margin-bottom: 20px;
  }

  .sessionDataItem {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }

  .sessionDataItem h3 {
    margin: 0;
    margin-right: 5px;
  }

  .sessionDataItem span {
    flex: 1;
  }

  .sessionDataItem {
    margin-bottom: 15px;
  }

  .key-value-header {
    display: flex;
    align-items: center;
  }

  .key-value-header h3 {
    margin: 0;
    margin-right: 10px;
  }

  .key-value-header span {
    flex: 1;
  }

  .values-container {
    max-height: 100px; /* Adjust this height as needed */
    overflow-y: auto;
    margin-top: 5px;
    padding-left: 20px; /* Indent values slightly */
    border-left: 2px solid #ddd; /* Optional: visual separation */
  }

  .value-item {
    padding: 2px 0; /* Space between values */
  }

  .save-button {
    margin-top: 20px;
  }
</style>