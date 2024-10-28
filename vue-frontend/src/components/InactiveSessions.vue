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
          <router-link 
            :to="{ name: 'inactivesessiondetail', params: { deviceId: deviceId } }" 
            class="inactive-session-link"
          >
            {{ session.session_name }} <br>
            <small>(Device ID: {{ deviceId }})</small>
          </router-link>
        </li>
      </ul>
    </div>
    <div v-else>
      <p>No inactive sessions available.</p>
    </div>
  </div>
</template>

<script>
  import { io } from 'socket.io-client';
  import config from '@/config.json';
  
  export default {
    name: 'inactivesessions',
    data() {
      return {
        inactiveSessions: {},
        socket: null,
      };
    },
    methods: {
      handleInactiveSessionsUpdate(inactiveSessions) {
        this.inactiveSessions = inactiveSessions;
      }
    },
    mounted() {
      this.socket = io(config.urlServer);

      this.socket.on('connect', () => {
        console.log('Connected to server');
        this.socket.emit('register_vue');
      });

      this.socket.on('disconnect', () => {
        console.log('Vue disconnected from server');
      });

      this.socket.on('inactive_sessions_update', (data) => {
        this.handleInactiveSessionsUpdate(data);
      });
    },
    beforeDestroy() {
      if (this.socket) {
        this.socket.disconnect();
      }
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

  .inactive-session-link small {
    color: #666;
  }
</style>