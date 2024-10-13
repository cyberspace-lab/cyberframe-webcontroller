<template>
  <div>
    <h1>Ongoing Sessions</h1>
    <div v-if="sessions && Object.keys(sessions).length > 0">
      <ul class="session-list">
        <li 
          v-for="(session, deviceId) in sessions" 
          :key="deviceId"
          class="session-item"
        >
          <router-link :to="{ name: 'controlpanel', params: { deviceId: deviceId } }" class="session-link">
            <div>
              <h5>{{ session.session_name }}</h5>
              <small>Device ID: {{ deviceId }}</small>
            </div>
          </router-link>
        </li>
      </ul>
    </div>
    <div v-else>
      <p>No ongoing sessions available.</p>
    </div>

    <div>
      <button class="view-past-sessions-btn" @click="goToPastSessions">View Past Sessions</button>
    </div>
  </div>
</template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'ongoingsessions',
    data() {
      return {
        sessions: {},
      };
    },
    methods: {
      fetchSessions() {
        axios.get(`${import.meta.env.VITE_API_BASE_URL}/sessions`)
          .then(response => {
            this.sessions = response.data;
          })
          .catch(error => {
            console.error("There was an error fetching the sessions!", error);
          });
      },
      goToPastSessions() {
        this.$router.push('/past-sessions');
      }
    },
    mounted() {
      this.fetchSessions();
      setInterval(this.fetchSessions, 5000);
    },
  };
  </script>

<style>
  .session-list {
    list-style-type: none;
    padding: 0;
    margin: 0;
  }

  .session-item {
    margin-bottom: 15px;
    border: 1px solid #ccc;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .session-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  }

  .session-link {
    display: block;
    text-decoration: none;
    color: inherit;
    padding: 15px;
  }

  .session-link h5 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }

  .session-link small {
    color: #666;
  }

  .view-past-sessions-btn {
    margin-top: 20px;
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .view-past-sessions-btn:hover {
    background-color: #0056b3;
  }
</style>