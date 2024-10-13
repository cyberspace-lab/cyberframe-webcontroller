<template>
  <div>
    <h1>Past Sessions</h1>
    <div v-if="pastSessions && Object.keys(pastSessions).length > 0">
      <ul class="past-session-list">
        <li 
          v-for="(session, deviceId) in pastSessions" 
          :key="deviceId" 
          class="past-session-item"
        >
          <router-link 
            :to="{ name: 'pastsessiondetail', params: { deviceId: deviceId } }" 
            class="past-session-link"
          >
            {{ session.session_name }} <br>
            <small>(Device ID: {{ deviceId }})</small>
          </router-link>
        </li>
      </ul>
    </div>
    <div v-else>
      <p>No past sessions available.</p>
    </div>
  </div>
</template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'past-sessions',
    data() {
      return {
        pastSessions: {}
      };
    },
    methods: {
      fetchPastSessions() {
        axios.get(`${import.meta.env.VITE_API_BASE_URL}/past-sessions`)
          .then(response => {
            this.pastSessions = response.data;
          })
          .catch(error => {
            console.error("There was an error fetching the past sessions!", error);
          });
      }
    },
    mounted() {
      this.fetchPastSessions();
      setInterval(this.fetchPastSessions, 5000);
    }
  };
  </script>

<style>
  .past-session-list {
    list-style-type: none;
    padding: 0;
    margin: 0;
  }

  .past-session-item {
    margin-bottom: 15px;
    border: 1px solid #ccc;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .past-session-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  }

  .past-session-link {
    display: block;
    text-decoration: none;
    color: inherit;
    padding: 15px;
  }

  .past-session-link small {
    color: #666;
  }

</style>