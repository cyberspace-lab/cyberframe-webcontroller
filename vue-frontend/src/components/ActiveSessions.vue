<template>
  <div>
    <div class="page-head">
      <div>
        <span class="eyebrow">Live Telemetry</span>
        <h1>Active Sessions</h1>
      </div>
      <span class="count">{{ parsedSessions.length }} connected</span>
    </div>

    <ul v-if="parsedSessions.length > 0" class="session-list">
      <li
        v-for="session in parsedSessions"
        :key="session.key"
        class="session-row"
        @click="openDetail(session)"
      >
        <div class="session-row-main">
          <p class="session-row-name">{{ session.session.session_name }}</p>
          <span class="session-row-device">DEVICE <b>{{ session.deviceId }}</b></span>
        </div>

        <div class="session-row-times">
          <div>
            <span class="session-time-label">Started </span>
            <span class="session-time-value">{{ formatTime(session.session.start_time) }}</span>
          </div>
          <div>
            <span class="session-time-label">Last ping </span>
            <span class="session-time-value">{{ formatTime(session.session.last_ping) }}</span>
          </div>
        </div>

        <div class="session-row-action">
          <span class="tag live"><span class="dot"></span> Live</span>
          <span class="session-row-chevron">View →</span>
        </div>
      </li>
    </ul>

    <div v-else class="empty-state">
      <span class="glyph">⊘</span>
      <p>No active sessions</p>
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
  computed: {
    parsedSessions() {
      return Object.entries(this.activeSessions).map(([key, session]) => {
        const [deviceId, sessionName] = JSON.parse(key);
        return { key, deviceId, sessionName, session };
      });
    }
  },
  methods: {
    formatTime(epochSeconds) {
      return new Date(epochSeconds * 1000).toLocaleString();
    },
    openDetail(session) {
      this.$router.push({
        name: 'activesessiondetail',
        params: { deviceId: session.deviceId, sessionName: session.sessionName }
      });
    },
    handleActiveSessionsUpdate(activeSessions) {
      this.activeSessions = activeSessions;
    }
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
