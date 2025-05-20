<template>
  <div>
    <div class="banner">
      <h1>Inactive Sessions</h1>
      <button class="banner-button" @click="goToActiveSessions">VIEW ACTIVE SESSIONS</button>
      <img 
        src="@/assets/settings.png" 
        alt="Settings" 
        class="settings" 
        @click="goToSettings"
      />
    </div>
    <div v-if="parsedSessions.length > 0">
      <ul class="session-list">
        <li 
          v-for="session in parsedSessions" 
          :key="session.deviceId + '_' + session.sessionName"
          class="session-item"
        >
          <router-link :to="{ name: 'inactivesessiondetail', params: { deviceId: session.deviceId, sessionName: session.sessionName } }" class="session-link">
            <div class="session-link-title">
              <h5>{{ session.session.session_name }}</h5>
              <small class="session-link-device">DEVICE ID: {{ session.deviceId }}</small>
            </div>
            <div class="session-link-time">
              <small>Start Time: {{ new Date(session.session.start_time * 1000).toLocaleString() }}</small>
              <small class="session-link-last-ping">Last Ping: {{ new Date(session.session.last_ping * 1000).toLocaleString() }}</small>
            </div>
            <button class="delete-button-list" @click.stop.prevent="deleteSession(session.deviceId, session.sessionName)">DELETE</button>
            <p class="view-detail-list">VIEW DETAIL →</p>
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
    computed: {
      parsedSessions() {
        return Object.entries(this.inactiveSessions).map(([key, session]) => {
          let [deviceId, sessionName] = JSON.parse(key);
          return { deviceId, sessionName, session };
        });
      }
    },
    methods: {
      goToActiveSessions() {
        // Redirect to active sessions page
        this.$router.push('/activesessions');
      },
      goToSettings() {
        // Redirect to settings page
        this.$router.push('/configedit');
      },
      handleInactiveSessionsUpdate(inactiveSessions) {
        // Update inactive sessions
        this.inactiveSessions = inactiveSessions;
      },
      deleteSession(deviceId, sessionName) {
        if (confirm(`Are you sure you want to delete session "${sessionName}" for device "${deviceId}"?`)) {
          this.$socket.emit('delete_session', { device_id: deviceId, session_name: sessionName });
        }
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