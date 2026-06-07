<template>
  <div>
    <div class="page-head">
      <div>
        <span class="eyebrow">Administration</span>
        <h1>Configuration</h1>
      </div>
    </div>

    <div class="config-layout">
      <textarea
        class="config-textarea"
        v-model="configContent"
        spellcheck="false"
        placeholder="Load the configuration to begin editing, or paste JSON here…"
      ></textarea>

      <div class="config-bar">
        <button class="btn cyan" @click="loadConfig">Load</button>
        <button class="btn violet" @click="saveConfig">Save</button>
        <input
          class="field"
          placeholder="Password"
          type="password"
          v-model="password"
        />
        <span class="config-hint">Validated as JSON before saving</span>
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
        // Validate configuration before saving
        if (!this.validateConfig()) return;

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
      },
      validateConfig() {
        try {
          // Parse JSON
          const config = JSON.parse(this.configContent);

          // Ensure required fields exist
          if (!config.applications || typeof config.applications !== "object") {
            alert("Invalid configuration: 'applications' field is missing or incorrect.");
            return false;
          }

          // Validate each application
          for (const appKey in config.applications) {
            const app = config.applications[appKey];

            if (!Array.isArray(app.controlButtons)) {
              alert(`Invalid configuration: 'controlButtons' should be an array in '${appKey}'.`);
              return false;
            }

            if (!Array.isArray(app.receivers)) {
              alert(`Invalid configuration: 'receivers' should be an array in '${appKey}'.`);
              return false;
            }

            if (!Array.isArray(app.levels)) {
              alert(`Invalid configuration: 'levels' should be an array in '${appKey}'.`);
              return false;
            }

            // Validate controlButtons
            for (const button of app.controlButtons) {
              if (!button.title || typeof button.title !== "string") {
                alert(`Invalid control button title in '${appKey}'.`);
                return false;
              }
              if (!button.payload || !button.payload.eventName) {
                alert(`Invalid payload in control button '${button.title}' in '${appKey}'.`);
                return false;
              }
            }

            // Validate levels
            for (const level of app.levels) {
              for (const levelKey in level) {
                const levelData = level[levelKey];
                if (!levelData.url || typeof levelData.url !== "string") {
                  alert(`Invalid URL for level '${levelKey}' in '${appKey}'.`);
                  return false;
                }
                if (typeof levelData.realWidth !== "number" || levelData.realWidth <= 0) {
                  alert(`Invalid 'realWidth' for level '${levelKey}' in '${appKey}'.`);
                  return false;
                }
                if (typeof levelData.realHeight !== "number" || levelData.realHeight <= 0) {
                  alert(`Invalid 'realHeight' for level '${levelKey}' in '${appKey}'.`);
                  return false;
                }
              }
            }
          }

          // Check memory percentage limit
          if (typeof config.min_free_memory_percentage !== "number" || config.min_free_memory_percentage < 0 || config.min_free_memory_percentage > 100) {
            alert("Invalid 'min_free_memory_percentage'. It must be a number between 0 and 100.");
            return false;
          }

          return true;
        } catch (error) {
          alert("Invalid JSON format! Please check your configuration.");
          return false;
        }
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