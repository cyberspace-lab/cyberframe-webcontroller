<template>
  <div>
    <div class="banner">
      <h1>Active Sessions</h1>
      <button class="banner-button" @click="goToInactiveSessions">VIEW INACTIVE SESSIONS</button>
      <img 
        src="@/assets/settings.png" 
        alt="Settings" 
        class="settings" 
        @click="goToSettings"
      />
    </div>
    <div v-if="activeSessions && Object.keys(activeSessions).length > 0">
      <ul class="session-list">
        <li
          v-for="(session, deviceId) in activeSessions" 
          :key="deviceId"
          class="session-item"
        >
          <router-link :to="{ name: 'activesessiondetail', params: { deviceId: deviceId } }" class="session-link">
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
      <p class="no-sessions-text">NO ACTIVE SESSIONS AVAILABLE</p>
    </div>
  </div>
</template>
  
<script>
  export default {
    name: 'activesessions',
    data() {
      return {
        activeSessions: { }
      };
    },
    methods: {
      goToInactiveSessions() {
        // Redirect to the InactiveSessions component
        this.$router.push('/inactivesessions');
      },
      goToSettings() {
        // Redirect to settings page
        this.$router.push('/configedit');
      },
      handleActiveSessionsUpdate(activeSessions) {
        // Update the activeSessions data when the 'active_sessions_update' event is received
        this.activeSessions = activeSessions;
      },
    },
    mounted() {
      // Emit the 'get_active_sessions' event to request the active sessions data
      this.$socket.emit('get_active_sessions');

      this.$socket.on('active_sessions_update', this.handleActiveSessionsUpdate);
    },
    beforeUnmount() {
      // Remove the event listener when the component is destroyed
      this.$socket.off('active_sessions_update', this.handleActiveSessionsUpdate);
    }
  };
</script>