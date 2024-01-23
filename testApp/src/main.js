import { createApp } from 'vue';
import App from './App.vue';
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');
const app = createApp(App);

app.config.globalProperties.$socket = socket;

app.mount('#app');