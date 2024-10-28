import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { io } from 'socket.io-client';

import './assets/main.css';

const socket = io('http://localhost:4000');

const app = createApp(App);

app.provide('socket', socket);
app.use(router);
app.mount('#app');