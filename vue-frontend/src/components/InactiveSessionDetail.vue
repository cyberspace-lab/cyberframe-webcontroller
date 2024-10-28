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

      </template>

      <template v-else>
        <p>Session with device {{ this.deviceId }} not found.</p>
      </template>

    </div>
</template>

<script>
  import { io } from 'socket.io-client';
  import { reactive } from 'vue';
  import config from '@/config.json';
  
  export default {
    name: 'inactivesessiondetail',
    props: ['deviceId'],
    data() {
      return {
        session: null,
        sessionData: {},
        showAllValuesToggle: reactive({}),
        socket: null,
      };
    },
    methods: {
      handleSessionUpdate(session) {
        this.session = session;
        this.handleSessionDataUpdate(session.data)
      },

      handleSessionDataUpdate(data) {
        this.sessionData = data;

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

      clearSessionData() {
        this.session = null;
        this.sessionData = {};
        this.showAllValuesToggle = {};
      }
    },
    mounted() {
      this.socket = io(config.urlServer);

      this.socket.emit('get_inactive_session', { device_id: this.deviceId });

      this.socket.on('connect', () => {
        console.log('Connected to server');
        this.socket.emit('register_vue');
      });

      this.socket.on('disconnect', () => {
        console.log('Vue disconnected from server');
      });

      //rozdelit metodu get_session na active a inactive

      this.socket.on('unity_connected', () => {
        console.log('Unity app connected from server');
        this.clearSessionData();
        this.$router.push('/activesessiondetail/' + this.deviceId);
      });
    },
    beforeDestroy() {
      if (this.socket) {
        this.socket.disconnect();
      }
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