import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import config from './src/config.json';

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    proxy: {
      '/socket.io': {
        target: config.urlServer,
        ws: true,
      }
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})