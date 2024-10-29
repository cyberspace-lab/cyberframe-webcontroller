<template>
  <div>
    <h1>Active Sessions</h1>
    <div v-if="activeSessions && Object.keys(activeSessions).length > 0">
      <ul class="session-list">
        <li 
          v-for="(session, deviceId) in activeSessions" 
          :key="deviceId"
          class="session-item"
        >
          <router-link :to="{ name: 'activesessiondetail', params: { deviceId: deviceId } }" class="session-link">
            <div>
              <h5>{{ session.session_name }}</h5>
              <small>Device ID: {{ deviceId }}</small>
              <br>
              <small>Start Time: {{ new Date(session.start_time * 1000).toLocaleString() }}</small>
              <br>
              <small>Last Ping: {{ new Date(session.last_ping * 1000).toLocaleString() }}</small>
            </div>
          </router-link>
        </li>
      </ul>
    </div>
    <div v-else>
      <p>No active sessions available.</p>
    </div>

    <div>
      <button class="view-inactive-sessions-btn" @click="goToInactiveSessions">View inactive sessions</button>
    </div>
  </div>
</template>
  
<script>
  export default {
    name: 'activesessions',
    data() {
      return {
        activeSessions: {}
      };
    },
    methods: {
      goToInactiveSessions() {
       this.$router.push('/inactivesessions');
      },
      handleActiveSessionsUpdate(activeSessions) {
        this.activeSessions = activeSessions;
      },
    },
    mounted() {
      this.$socket.emit('get_active_sessions');

      this.$socket.on('active_sessions_update', this.handleActiveSessionsUpdate);
    },
    beforeUnmount() {
      this.$socket.off('active_sessions_update', this.handleActiveSessionsUpdate);
    }
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

  .view-inactive-sessions-btn {
    margin-top: 20px;
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .view-inactive-sessions-btn:hover {
    background-color: #0056b3;
  }
</style>