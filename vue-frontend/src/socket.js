// Minimal native-WebSocket client that exposes a Socket.IO-compatible surface
// (`emit`, `on`, `off`, `connected`) so the existing dashboard components work
// unchanged. Messages use the envelope { event, data }.
//
// It auto-reconnects with backoff and replays the `connect` event each time the
// underlying socket (re)opens, matching how the components rely on `connect`.

class WsClient {
  constructor(url) {
    this.url = url;
    this.connected = false;
    this.sid = null;
    this._listeners = new Map(); // event -> Set<handler>
    this._queue = []; // messages buffered while disconnected
    this._reconnectDelay = 500;
    this._connect();
  }

  _connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      this.connected = true;
      this._reconnectDelay = 500;
      // Flush anything queued while we were offline.
      for (const msg of this._queue) this.ws.send(msg);
      this._queue = [];
      this._dispatch('connect');
    };

    this.ws.onmessage = (ev) => {
      let msg;
      try {
        msg = JSON.parse(ev.data);
      } catch {
        return;
      }
      // Capture the server-assigned sid for completeness; it is not required
      // by the dashboard but mirrors Socket.IO's socket.id.
      if (msg.event === 'welcome' && msg.data?.sid) this.sid = msg.data.sid;
      this._dispatch(msg.event, msg.data);
    };

    this.ws.onclose = () => {
      this.connected = false;
      this._dispatch('disconnect');
      setTimeout(() => this._connect(), this._reconnectDelay);
      this._reconnectDelay = Math.min(this._reconnectDelay * 2, 5000);
    };

    this.ws.onerror = () => this.ws.close();
  }

  _dispatch(event, data) {
    const handlers = this._listeners.get(event);
    if (handlers) for (const h of [...handlers]) h(data);
  }

  emit(event, data) {
    const msg = JSON.stringify({ event, data });
    if (this.connected) {
      this.ws.send(msg);
    } else {
      this._queue.push(msg);
    }
  }

  on(event, handler) {
    if (!this._listeners.has(event)) this._listeners.set(event, new Set());
    this._listeners.get(event).add(handler);
  }

  off(event, handler) {
    const handlers = this._listeners.get(event);
    if (handlers) handlers.delete(handler);
  }

  disconnect() {
    if (this.ws) {
      this.ws.onclose = null; // suppress auto-reconnect on intentional close
      this.ws.close();
    }
    this.connected = false;
  }
}

// Build the ws:// URL from the page origin. In dev, Vite proxies /ws to the
// Node server (see vite.config.js); in production the SPA and server share an
// origin, so this resolves correctly without configuration.
function resolveUrl() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${location.host}/ws`;
}

export function createSocket(url = resolveUrl()) {
  return new WsClient(url);
}
