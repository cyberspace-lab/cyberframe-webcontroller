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

  </div>

  <div v-else>
    <h1>Session Detail</h1>
    <p>No application selected or application not found.</p>
  </div>
</template>
  
  <script>
  import axios from 'axios';
  import config from '@/config.json';
  import { reactive } from 'vue';
  
  export default {
    name: 'controlpanel',
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
      fetchSession() {
        axios.get(`http://localhost:4000/sessions`)
          .then(response => {
            const sessions = response.data;
            this.session = sessions[this.deviceId] || null;
          })
          .catch(error => {
            console.error("There was an error fetching the session!", error);
          });
        this.fetchSessionData();
      },
      fetchSessionData() {
      axios.get(`http://localhost:4000/session_data/${this.deviceId}`)
        .then(response => {
          if (response.data) {
            this.sessionData = response.data;

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
          } else {
            this.sessionData = {};
            this.showAllValuesToggle = reactive({}); 
          }
        })
        .catch(error => {
          console.error("There was an error fetching the session data!", error);
        });
    },
      handleButtonClick(button) {
      if (!this.session || !this.session.endpoint) {
        console.error("Session or endpoint not found");
        return;
      }

      axios.post(this.session.endpoint, button.payload)
        .then(response => {
          console.log('Event sent to Unity:', response.data);
        })
        .catch(error => {
          console.error('Error sending event to Unity:', error);
        });
      },

      toggleShowAllValues(key) {
        this.showAllValuesToggle[key] = !this.showAllValuesToggle[key];
      }
    },
    mounted() {
      this.fetchSession();
      setInterval(this.fetchSessionData, 5000); 
    }
  };
  </script>

<style>
  .left {
    width: 47%;
    float: left;
    padding: 0px;
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