<template>
    <div>
      <h1>Past Session Detail</h1>

      <template v-if="session">

        <p>Device ID: {{ deviceId }}</p>
        <p>Session Name: {{ session.session_name }}</p>
        <p>Start Time: {{ new Date(session.start_time * 1000).toLocaleString() }}</p>
        <p>Last Ping: {{ new Date(session.last_ping * 1000).toLocaleString() }}</p>

        <div class="pastSessionData">
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
  import axios from 'axios';
  import { reactive } from 'vue';
  
  export default {
    name: 'pastsessiondetail',
    props: ['deviceId'],
    data() {
      return {
        session: null,
        sessionData: {},
        showAllValuesToggle: reactive({})
      };
    },
    methods: {
      fetchSession() {
        axios.get(`http://localhost:4000/past-sessions`)
          .then(response => {
            const sessions = response.data;
            this.session = sessions[this.deviceId] || null;
          })
          .catch(error => {
            console.error("There was an error fetching the session!", error);
          });
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
    toggleShowAllValues(key) {
        this.showAllValuesToggle[key] = !this.showAllValuesToggle[key];
      }
    },
    mounted() {
      this.fetchSession();
      this.fetchSessionData();
    }
  };
  </script>

<style>

  .pastSessionData {
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