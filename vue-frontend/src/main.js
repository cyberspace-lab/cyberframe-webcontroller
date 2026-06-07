import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createSocket } from './socket';

import './assets/main.css';

const socket = createSocket();

socket.on('connect', () => {
    console.log('Vue connected to server');
    socket.emit('register_vue');
});

socket.on('disconnect', () => {
    console.log('Vue disconnected from server');
});

window.addEventListener('beforeunload', () => {
    socket.disconnect();
});

const app = createApp(App);

app.config.globalProperties.$socket = socket;

app.provide('socket', socket);
app.use(router);
app.mount('#app');
