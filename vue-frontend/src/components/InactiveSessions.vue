<template>
  <div>
    <div class="page-head">
      <div>
        <span class="eyebrow">Archive</span>
        <h1>Inactive Sessions</h1>
      </div>
      <span class="count">{{ parsedSessions.length }} stored</span>
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
          <button
            class="row-delete"
            title="Delete session"
            @click.stop="deleteSession(session.deviceId, session.sessionName)"
          >🗑</button>
          <span class="session-row-chevron">View →</span>
        </div>
      </li>
    </ul>

    <div v-else class="empty-state">
      <span class="glyph">⊘</span>
      <p>No inactive sessions</p>
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
        name: 'inactivesessiondetail',
        params: { deviceId: session.deviceId, sessionName: session.sessionName }
      });
    },
    handleInactiveSessionsUpdate(inactiveSessions) {
      this.inactiveSessions = inactiveSessions;
    },
    deleteSession(deviceId, sessionName) {
      if (confirm(`Delete session "${sessionName}" for device "${deviceId}"?`)) {
        this.$socket.emit('delete_session', { device_id: deviceId, session_name: sessionName });
      }
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
