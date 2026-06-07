<template>
  <header class="app-header">
    <div class="app-header-inner">
      <div class="brand" @click="$router.push('/activesessions')">
        <img src="@/assets/logo-white.png" alt="CyberspaceLab" class="brand-logo" />
        <span class="brand-wordmark">Webcontroller</span>
      </div>

      <nav class="app-nav">
        <router-link to="/activesessions" class="nav-link">Active</router-link>
        <router-link to="/inactivesessions" class="nav-link">Inactive</router-link>
        <router-link to="/configedit" class="nav-link">Config</router-link>

        <div class="theme-toggle" role="group" aria-label="Theme">
          <button
            :class="{ active: theme === 'dark' }"
            title="Dark theme"
            @click="setTheme('dark')"
          >◐</button>
          <button
            :class="{ active: theme === 'light' }"
            title="Light theme"
            @click="setTheme('light')"
          >◑</button>
        </div>
      </nav>
    </div>
  </header>
</template>

<script>
export default {
  name: 'AppHeader',
  data() {
    return {
      theme: document.documentElement.getAttribute('data-theme') || 'dark'
    };
  },
  methods: {
    setTheme(theme) {
      this.theme = theme;
      document.documentElement.setAttribute('data-theme', theme);
      try {
        localStorage.setItem('csl-theme', theme);
      } catch (e) {
        /* ignore storage failures */
      }
    }
  }
};
</script>
