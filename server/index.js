// CyberFrame WebController server.
//
// A single Node process that:
//   - serves the built Vue dashboard (static files from vue-frontend/dist)
//   - runs a native WebSocket server (no Socket.IO) for realtime communication
//     with Unity / Unreal clients and the dashboard
//   - keeps session state in memory and persists inactive sessions to disk
//
// Message protocol (both directions): a JSON envelope
//   { "event": "<name>", "data": <payload> }
// See MIGRATION.md for the full protocol and how to port native clients.

import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';

import express from 'express';
import { WebSocketServer } from 'ws';

import {
  cleanupInactiveSessions,
  deleteSession,
  findSessionBySid,
  getActiveSessions,
  getInactiveSessions,
  getMaxHistory,
  getSession,
  hasActiveSessions,
  loadSessionFromDisk,
  saveSessionToDisk,
  setSession,
} from './sessions.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

const PORT = process.env.PORT || 4000;
const PASSWORD = process.env.PASSWORD || '0000';
const CONFIG_PATH = path.join(ROOT, 'vue-frontend', 'src', 'config.json');
const DIST_DIR = path.join(ROOT, 'vue-frontend', 'dist');

// Load configuration once at startup, and keep it in memory.
let config = {};
try {
  config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
} catch (err) {
  console.error(`Could not read config at ${CONFIG_PATH}: ${err}`);
}

const minFreeMemory = () => config?.min_free_memory_percentage ?? 30;

// ---------------------------------------------------------------------------
// HTTP / static hosting
// ---------------------------------------------------------------------------
const app = express();

app.get('/health', (_req, res) => res.json({ status: 'ok' }));

// Test interface for sending fake data (served from /static).
app.use('/static', express.static(path.join(ROOT, 'static')));
app.get('/test', (_req, res) =>
  res.sendFile(path.join(ROOT, 'static', 'test_interface.html')),
);

// Serve the built Vue SPA. If it hasn't been built yet, show a hint.
if (fs.existsSync(DIST_DIR)) {
  app.use(express.static(DIST_DIR));
  app.get(/.*/, (_req, res) => res.sendFile(path.join(DIST_DIR, 'index.html')));
} else {
  app.get('/', (_req, res) =>
    res.send(
      'Dashboard not built. Run `npm run build` (builds vue-frontend), then restart. Server is running.',
    ),
  );
}

const server = http.createServer(app);

// ---------------------------------------------------------------------------
// WebSocket server
// ---------------------------------------------------------------------------
const wss = new WebSocketServer({ server, path: '/ws' });

// Connected dashboard clients (the Vue app). Keyed by sid.
const vueClients = new Map(); // sid -> ws
// Every connected socket, keyed by sid, so we can target a specific client.
const clients = new Map(); // sid -> ws

function send(ws, event, data) {
  if (ws && ws.readyState === ws.OPEN) {
    ws.send(JSON.stringify({ event, data }));
  }
}

function sendToSid(sid, event, data) {
  send(clients.get(sid), event, data);
}

function broadcast(event, data) {
  for (const ws of clients.values()) send(ws, event, data);
}

function emitToVue(event, data) {
  for (const ws of vueClients.values()) send(ws, event, data);
}

function emitSessionsUpdate() {
  const active = getActiveSessions();
  const inactive = getInactiveSessions();
  for (const ws of vueClients.values()) {
    send(ws, 'active_sessions_update', active);
    send(ws, 'inactive_sessions_update', inactive);
  }
}

function emitSessionDataKeyUpdate(deviceId, sessionName, keyName) {
  const session = getSession(deviceId, sessionName);
  if (!session) return;
  emitToVue('session_data_key_update', {
    device_id: deviceId,
    session_name: sessionName,
    key: keyName,
    value: session.data[keyName],
  });
}

// Some clients send payloads as a JSON string (the original Unity package did);
// others send an already-parsed object. Accept both.
function asObject(data) {
  if (typeof data === 'string') {
    try {
      return JSON.parse(data);
    } catch {
      return {};
    }
  }
  return data ?? {};
}

// ---------------------------------------------------------------------------
// Event handlers (ported 1:1 from app.py)
// ---------------------------------------------------------------------------
const handlers = {
  ping(ws) {
    send(ws, 'pong');
  },

  register_vue(ws) {
    vueClients.set(ws.sid, ws);
    console.log(`Vue registered with session ID: ${ws.sid}`);
    emitSessionsUpdate();
  },

  register(ws, data) {
    cleanupInactiveSessions(minFreeMemory());

    const payload = asObject(data);
    const deviceId = payload.device_id;
    const sessionName = payload.session_name;

    if (!deviceId || !sessionName) {
      send(ws, 'error', { message: 'device_id and session_name are required' });
      return;
    }

    const existing = loadSessionFromDisk(deviceId, sessionName);
    if (existing) {
      Object.assign(existing, {
        sid: ws.sid,
        is_connected: true,
        last_ping: Date.now() / 1000,
      });
      setSession(deviceId, sessionName, existing);
    } else {
      const session = {
        session_name: sessionName,
        start_time: Date.now() / 1000,
        last_ping: Date.now() / 1000,
        data: {},
        sid: ws.sid,
        is_connected: true,
      };

      const appConfig = config?.applications?.[sessionName] ?? {};
      const receivers = appConfig.receivers ?? [{}];
      for (const receiver of receivers) {
        for (const k of Object.keys(receiver)) session.data[k] = [];
      }
      setSession(deviceId, sessionName, session);
    }

    send(ws, 'registered');
    broadcast('unity_connected', { device_id: deviceId, session_name: sessionName });
    emitSessionsUpdate();
  },

  send_command(_ws, data) {
    const eventName = data?.payload?.eventName;
    const parameters = data?.payload?.parameters;
    const sid = data?.sid;
    sendToSid(sid, eventName, parameters);
    console.log(`Command ${eventName} sent with parameters: ${JSON.stringify(parameters)}`);
  },

  update_data(ws, data) {
    cleanupInactiveSessions(minFreeMemory());

    try {
      const payload = asObject(data);
      const deviceId = payload.device_id;
      const sessionName = payload.session_name;
      const keyName = payload.key;
      const value = payload.value;

      if (!deviceId || !sessionName || !keyName || value === undefined || value === null) {
        send(ws, 'error', 'device_id, session_name, key, and value are required');
        return;
      }

      const session = getSession(deviceId, sessionName);
      if (!session) return;

      if (!session.data[keyName]) session.data[keyName] = [];
      session.data[keyName].unshift(value);
      session.last_ping = Date.now() / 1000;

      const maxHistory = getMaxHistory(config, sessionName, keyName);
      if (session.data[keyName].length > maxHistory) {
        session.data[keyName] = session.data[keyName].slice(0, maxHistory);
      }

      emitSessionDataKeyUpdate(deviceId, sessionName, keyName);
    } catch (err) {
      send(ws, 'error', String(err));
    }
  },

  get_active_sessions(ws) {
    send(ws, 'active_sessions_update', getActiveSessions());
  },

  get_inactive_sessions(ws) {
    send(ws, 'inactive_sessions_update', getInactiveSessions());
  },

  get_active_session(ws, data) {
    const deviceId = data?.device_id;
    const sessionName = data?.session_name;
    const session = getSession(deviceId, sessionName);
    if (session && session.is_connected) {
      send(ws, 'active_session', { device_id: deviceId, session_name: sessionName, session });
    }
  },

  get_inactive_session(ws, data) {
    const deviceId = data?.device_id;
    const sessionName = data?.session_name;
    const session = getSession(deviceId, sessionName);
    if (session && !session.is_connected) {
      send(ws, 'inactive_session', { device_id: deviceId, session_name: sessionName, session });
    }
  },

  delete_session(_ws, data) {
    const deviceId = data?.device_id;
    const sessionName = data?.session_name;
    const session = deleteSession(deviceId, sessionName);
    if (session) {
      console.log(`Deleted session for device ID: ${deviceId}`);
      emitSessionsUpdate();
    }
  },

  load_config(ws, data) {
    if (data?.password !== PASSWORD) {
      send(ws, 'error', { message: 'Incorrect password' });
      return;
    }
    try {
      const content = fs.readFileSync(CONFIG_PATH, 'utf8');
      send(ws, 'config_loaded', { config_content: content });
    } catch (err) {
      console.error(`Error loading config: ${err}`);
      send(ws, 'error', { message: 'Error loading config' });
    }
  },

  save_config(ws, data) {
    if (hasActiveSessions()) {
      send(ws, 'error', { message: 'Cannot save config due to active sessions.' });
      return;
    }
    if (data?.password !== PASSWORD) {
      send(ws, 'error', { message: 'Incorrect password' });
      return;
    }
    try {
      fs.writeFileSync(CONFIG_PATH, data.config_content);
      config = JSON.parse(data.config_content);
      send(ws, 'config_saved');
    } catch (err) {
      console.error(`Error saving config: ${err}`);
      send(ws, 'error', { message: 'Error saving config' });
    }
  },
};

wss.on('connection', (ws) => {
  ws.sid = randomUUID();
  clients.set(ws.sid, ws);
  console.log(`Client connected: ${ws.sid}`);

  // Hand the client its server-assigned sid (replaces Socket.IO's request.sid).
  send(ws, 'welcome', { sid: ws.sid });

  ws.on('message', (raw) => {
    let msg;
    try {
      msg = JSON.parse(raw.toString());
    } catch {
      send(ws, 'error', { message: 'Invalid JSON message' });
      return;
    }

    const handler = handlers[msg.event];
    if (handler) {
      handler(ws, msg.data);
    } else {
      console.warn(`Unknown event: ${msg.event}`);
    }
  });

  ws.on('close', () => {
    console.log(`Client disconnected: ${ws.sid}`);
    clients.delete(ws.sid);

    if (vueClients.has(ws.sid)) {
      vueClients.delete(ws.sid);
    } else {
      const found = findSessionBySid(ws.sid);
      if (found) {
        const { deviceId, sessionName, session } = found;
        session.last_ping = Date.now() / 1000;
        session.is_connected = false;
        saveSessionToDisk(deviceId, sessionName, session);
        broadcast('unity_disconnected', {
          device_id: deviceId,
          session_name: sessionName,
        });
      }
    }
    emitSessionsUpdate();
  });
});

server.listen(PORT, () => {
  console.log(`CyberFrame WebController listening on http://0.0.0.0:${PORT}`);
  console.log(`WebSocket endpoint: ws://0.0.0.0:${PORT}/ws`);
});
