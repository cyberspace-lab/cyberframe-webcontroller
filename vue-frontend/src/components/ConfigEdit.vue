<template>
  <div>
    <div class="banner">
      <h1>Configuration File Editing</h1>
      <button class="banner-button" @click="goToActiveSessions">VIEW ACTIVE SESSIONS</button>
    </div>
    <div>
      <textarea class="config-textarea" v-model="configContent" rows="20"></textarea>
      <div class="config-buttons">
        <button class="config-button" @click="saveConfig">SAVE</button>
        <button class="config-button" @click="loadConfig">LOAD</button>
        <input class="config-password" placeholder="Enter password" type="password" v-model="password" />
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'configedit',
    data() {
      return {
        password: '',
        configContent: ''
      };
    },
    methods: {
      goToActiveSessions() {
        // Redirect to active sessions page
        this.$router.push('/activesessions');
      },
      saveConfig() {
        // Send password and config content to backend
        const data = {
          password: this.password,
          config_content: this.configContent
        };

        this.$socket.emit('save_config', data);
      },
      loadConfig() {
        // Send password to backend to load the config
        const data = {
          password: this.password
        };

        this.$socket.emit('load_config', data);
      },
      handleError(data) {
        alert(data.message);
      },
      handleSaved() {
        alert('Configuration saved successfully!');
      },
      handleLoaded(data) {
        this.configContent = data.config_content;
        alert('Configuration loaded successfully!');
      }
    },
    mounted() {
      this.$socket.on('error', this.handleError);
      this.$socket.on('config_saved', this.handleSaved);
      this.$socket.on('config_loaded', this.handleLoaded);
    },
    beforeUnmount() {
      this.$socket.off('error', this.handleError);
      this.$socket.off('config_saved', this.handleSaved);
      this.$socket.off('config_loaded', this.handleLoaded);
    }
  };
</script>