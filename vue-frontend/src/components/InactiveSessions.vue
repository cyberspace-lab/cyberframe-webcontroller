<template>
  <div>
    <div class="banner">
      <h1>Inactive Sessions</h1>
      <button class="banner-button" @click="goToActiveSessions">VIEW ACTIVE SESSIONS</button>
    </div>
    <div v-if="inactiveSessions && Object.keys(inactiveSessions).length > 0">
      <ul class="session-list">
        <li 
          v-for="(session, deviceId) in inactiveSessions" 
          :key="deviceId" 
          class="session-item"
        >
          <router-link :to="{ name: 'inactivesessiondetail', params: { deviceId: deviceId } }" class="session-link">
            <div class="session-link-title">
              <h5>{{ session.session_name }}</h5>
              <small class="session-link-device">DEVICE ID: {{ deviceId }}</small>
            </div>
            <div class="session-link-time">
              <small>Start Time: {{ new Date(session.start_time * 1000).toLocaleString() }}</small>
              <small class="session-link-last-ping">Last Ping: {{ new Date(session.last_ping * 1000).toLocaleString() }}</small>
            </div>
            <p class="view-detail">VIEW DETAIL →</p>
          </router-link>
        </li>
      </ul>
    </div>
    <div v-else>
      <p class="no-sessions-text">NO INACTIVE SESSIONS AVAILABLE</p>
    </div>
  </div>
</template>

<script>  
  export default {
    name: 'inactivesessions',
    data() {
      return {
        inactiveSessions: {}
      };
    },
    methods: {
      goToActiveSessions() {
       this.$router.push('/activesessions');
      },
      handleInactiveSessionsUpdate(inactiveSessions) {
        this.inactiveSessions = inactiveSessions;
      }
    },
    mounted() {
      this.$socket.emit('get_inactive_sessions');

      this.$socket.on('inactive_sessions_update', this.handleInactiveSessionsUpdate);
    },
    beforeUnmount() {
      this.$socket.off('inactive_sessions_update', this.handleInactiveSessionsUpdate);
    }
  };
</script>

<style>
  .inactive-session-list {
    list-style-type: none;
    padding: 0;
    margin: 0;
  }

  .inactive-session-item {
    margin-bottom: 15px;
    border: 1px solid #ccc;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .inactive-session-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  }

  .inactive-session-link {
    display: block;
    text-decoration: none;
    color: inherit;
    padding: 15px;
  }

  .inactive-session-link h5 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }

  .inactive-session-link small {
    color: #666;
  }

  .view-active-sessions-btn {
    margin-top: 20px;
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .view-active-sessions-btn:hover {
    background-color: #0056b3;
  }
</style>