<template>
    <div>
      <h1>Inactive Session Detail</h1>

      <template v-if="session">

        <p>Device ID: {{ deviceId }}</p>
        <p>Session Name: {{ session.session_name }}</p>
        <p>Start Time: {{ new Date(session.start_time * 1000).toLocaleString() }}</p>
        <p>Last Ping: {{ new Date(session.last_ping * 1000).toLocaleString() }}</p>

        <div class="inactiveSessionData">
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

        <button @click="saveSessionAsJson">Save session as JSON</button>

      </template>

      <template v-else>
        <p>Session with device {{ this.deviceId }} not found.</p>
      </template>

    </div>
</template>

<script>
  import { reactive } from 'vue';
  
  export default {
    name: 'inactivesessiondetail',
    props: ['deviceId'],
    data() {
      return {
        session: null,
        sessionData: {},
        showAllValuesToggle: reactive({})
      };
    },
    methods: {
      handleInactiveSession(data) {
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

      toggleShowAllValues(key) {
        this.showAllValuesToggle[key] = !this.showAllValuesToggle[key];
      },

      handleUnityConnected() {
        if (this.deviceId != data.device_id) return;
        console.log('Unity app connected from server');
        this.session = null;
        this.sessionData = {};
        this.showAllValuesToggle = {};
        this.$router.push('/activesessiondetail/' + this.deviceId);
      },

      emitGetInactiveSession() {
        this.$socket.emit('get_inactive_session', { device_id: this.deviceId });
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
        this.emitGetInactiveSession();
      } else {
        this.$socket.on('connect', this.emitGetInactiveSession);
      };

      this.$socket.on('inactive_session', this.handleInactiveSession);
      this.$socket.on('unity_connected', this.handleUnityConnected);
    },
    beforeUnmount() {
      this.$socket.off('inactive_session', this.handleInactiveSession);
      this.$socket.off('unity_connected', this.handleUnityConnected);
      this.$socket.off('connect', this.emitGetInactiveSession);
    }
  };
</script>

<style>
  .inactiveSessionData {
    width: 60%;
    border-width: thin;
    border-style: solid;
    border-radius: 10px;
    margin: 0 auto;
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
</style>