<template>
  <div>
    <h1>Inactive Sessions</h1>
    <div v-if="inactiveSessions && Object.keys(inactiveSessions).length > 0">
      <ul class="inactive-session-list">
        <li 
          v-for="(session, deviceId) in inactiveSessions" 
          :key="deviceId" 
          class="inactive-session-item"
        >
          <router-link :to="{ name: 'inactivesessiondetail', params: { deviceId: deviceId } }" class="inactive-session-link">
            <div>
              <h5>{{ session.session_name }} </h5>
              <small>(Device ID: {{ deviceId }})</small>
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
      <p>No inactive sessions available.</p>
    </div>

    <div>
      <button class="view-active-sessions-btn" @click="goToActiveSessions">View active sessions</button>
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