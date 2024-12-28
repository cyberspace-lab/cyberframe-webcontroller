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
        // Redirect to active sessions page
        this.$router.push('/activesessions');
      },
      handleInactiveSessionsUpdate(inactiveSessions) {
        // Update inactive sessions
        this.inactiveSessions = inactiveSessions;
      }
    },
    mounted() {
      // Get inactive sessions
      this.$socket.emit('get_inactive_sessions');
      // Listen for inactive sessions update
      this.$socket.on('inactive_sessions_update', this.handleInactiveSessionsUpdate);
    },
    beforeUnmount() {
      // Remove socket listener
      this.$socket.off('inactive_sessions_update', this.handleInactiveSessionsUpdate);
    }
  };
</script>