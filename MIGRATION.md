# Migration Guide — Socket.IO ➜ Native WebSocket

The WebController backend was rewritten from **Python (Flask + Socket.IO)** to a
single **Node.js** app using **native WebSockets** (the `ws` library on the
server, the browser `WebSocket` API on the client). This removes the Docker /
nginx / Python stack — the whole thing now runs with `npm start`.

This document is for whoever maintains the **client** packages
(`cyberframe-webcontroller-unitypackage`, the Unreal plugin, or any other
client). It describes the new wire protocol and how to port a Socket.IO client
to it.

---

## 1. What changed

| Before (Socket.IO)                          | After (native WebSocket)                         |
| ------------------------------------------- | ------------------------------------------------ |
| Socket.IO client library required          | Any plain WebSocket client (built into most engines) |
| `socket.Emit("event", payload)`            | Send a JSON text frame `{"event": "...", "data": ...}` |
| `socket.On("event", handler)`              | Parse incoming frames; switch on `msg.event`     |
| Server URL `http://host:4000` (Socket.IO handshake) | WebSocket URL `ws://host:4000/ws` (or `wss://` over TLS) |
| Server identifies clients by `request.sid` | Server sends each client a `sid` in a `welcome` message on connect |
| Multiple framing/transport layers (polling, upgrade) | One persistent WebSocket, one frame = one JSON message |

**The event names and payload shapes are unchanged.** Only the *transport* and
*framing* changed. If your old code emitted `register` with
`{device_id, session_name}`, it still does — you just wrap it in the envelope.

---

## 2. The wire protocol

### Connection

Open a WebSocket to:

```
ws://<host>:<port>/ws        # plain
wss://<host>:<port>/ws       # behind TLS (production)
```

Immediately after connecting, the server sends:

```json
{ "event": "welcome", "data": { "sid": "<uuid>" } }
```

You generally don't need the `sid` on a Unity/Unreal client — it's used by the
dashboard to target commands at a specific client. Store it if you want, ignore
it otherwise.

### Message envelope

**Every** message in **both** directions is a single JSON text frame:

```json
{ "event": "<string>", "data": <any JSON value> }
```

- `event` — the event name (same names as the old Socket.IO events).
- `data` — the payload. May be an object, string, number, array, or omitted.

There is no acknowledgement/callback mechanism (Socket.IO "acks" are not used by
this app, so nothing is lost).

> **Compatibility note:** the server accepts `data` either as a JSON object *or*
> as a JSON-encoded string (the original Unity package sent some payloads as
> strings). New clients should send objects.

---

## 3. Events a client sends (client ➜ server)

These are the events a Unity/Unreal client emits. Wrap each payload in the
envelope shown above.

### `register` — announce a session

```json
{ "event": "register", "data": { "device_id": "headset-01", "session_name": "MoveDifferent" } }
```

Send this once after connecting. The server creates (or restores from disk) a
session keyed by `(device_id, session_name)` and replies with
`{ "event": "registered" }`. It also broadcasts `unity_connected` to dashboards.

### `update_data` — push telemetry

```json
{
  "event": "update_data",
  "data": {
    "device_id": "headset-01",
    "session_name": "MoveDifferent",
    "key": "position",
    "value": "[{\"x\":1.2,\"y\":0,\"z\":3.4,\"levelID\":\"1\"}]"
  }
}
```

- `key` must be one of the receiver keys configured for that `session_name` in
  `vue-frontend/src/config.json` (e.g. `position`, `currentScene`, `location`).
- `value` is whatever you want stored — the dashboard `JSON.parse`s some keys
  (`position`, `context`), so for those send a JSON **string**.
- The server keeps a bounded history per key (`maxHistory` from config) and
  pushes each update to dashboards in real time.

### `ping`

```json
{ "event": "ping" }
```

Server replies `{ "event": "pong" }`. Optional keep-alive.

> A client does **not** send `register_vue`, `get_*`, `send_command`,
> `save_config`, `load_config`, or `delete_session` — those are dashboard-only
> events, listed here only so you know the full surface.

---

## 4. Events a client receives (server ➜ client)

| Event         | When / payload |
| ------------- | -------------- |
| `welcome`     | On connect: `{ "sid": "<uuid>" }` |
| `registered`  | After a successful `register` (no data) |
| `pong`        | Reply to `ping` (no data) |
| `error`       | On a problem: `{ "message": "..." }` or a string |
| *command events* | Commands relayed from the dashboard via `send_command`. The **event name and parameters are defined by your config's `controlButtons`** (e.g. `startLevel`, `resetPosition`, `participantName`). The `data` is the button's `parameters` object, including a `userInput` field when the button required input. |

**Handling commands** is the important part: register listeners for each
`eventName` you declared in `controlButtons` in `config.json`. For example, if
config has a button with `"eventName": "startLevel"` and
`"parameters": { "settingsIndex": 0 }`, your client will receive:

```json
{ "event": "startLevel", "data": { "settingsIndex": 0, "userInput": null } }
```

---

## 5. Porting a client, step by step

1. **Drop the Socket.IO dependency.** Remove the Socket.IO library/plugin. Use
   the engine's built-in WebSocket:
   - Unity: `System.Net.WebSockets.ClientWebSocket`, or
     [`NativeWebSocket`](https://github.com/endel/NativeWebSocket) for WebGL.
   - Unreal: the built-in `IWebSocket` (module `WebSockets`,
     `FWebSocketsModule::Get().CreateWebSocket(Url)`).

2. **Connect** to `ws://<host>:<port>/ws` (or `wss://` in production).

3. **Replace every `Emit`** with: serialize `{ event, data }` to JSON and send
   it as a text frame. A tiny helper keeps call sites readable:

   ```csharp
   // Unity / C# sketch
   void Emit(string ev, object data) {
       var msg = JsonConvert.SerializeObject(new { @event = ev, data });
       websocket.Send(msg); // NativeWebSocket: await SendText(msg)
   }
   ```

4. **Replace `On(...)` handlers** with one receive loop that parses each frame
   and dispatches on `msg.event`:

   ```csharp
   void OnMessage(string raw) {
       var msg = JObject.Parse(raw);
       switch ((string)msg["event"]) {
           case "registered": /* ... */ break;
           case "startLevel": HandleStartLevel(msg["data"]); break;
           // ... one case per controlButton eventName
           case "error": Debug.LogError(msg["data"]); break;
       }
   }
   ```

5. **On connect**, send `register` with your `device_id` and `session_name`.

6. **Throughout the session**, send `update_data` frames for each receiver key.

7. **Reconnect logic**: if the socket drops, reconnect and `register` again. The
   server restores the session from disk, so history is preserved.

### Unreal (C++) sketch

```cpp
// In your module startup
FModuleManager::Get().LoadModuleChecked("WebSockets");
Socket = FWebSocketsModule::Get().CreateWebSocket("ws://host:4000/ws");

Socket->OnConnected().AddLambda([this]() {
    Emit(TEXT("register"), /* {device_id, session_name} as JSON */);
});
Socket->OnMessage().AddLambda([this](const FString& Msg) {
    // parse JSON, switch on "event"
});
Socket->Connect();
```

---

## 6. Local testing

- Start the server: `npm install` then `npm start` (serves on port `4000`).
- Open the test interface at `http://localhost:4000/test` — it now uses native
  WebSocket and can register fake sessions and push fake data, exactly mirroring
  what a ported Unity/Unreal client does.
- Open the dashboard at `http://localhost:4000/` to watch sessions live.

If a frame is malformed JSON, the server replies with an `error` event and keeps
the connection open, so you can iterate quickly.

---

## 7. Checklist

- [ ] Socket.IO library removed from the client project
- [ ] Connect to `/ws` (`ws://` dev, `wss://` prod)
- [ ] All sends wrapped as `{ "event", "data" }` JSON text frames
- [ ] Receive loop dispatches on `msg.event`
- [ ] `register` sent on (re)connect
- [ ] One handler per `controlButton` `eventName` from `config.json`
- [ ] `update_data` sends use the configured receiver keys
- [ ] Verified end-to-end against `http://localhost:4000/test` + dashboard
