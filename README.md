# CyberFrame WebController

Monitor and interact with Unity/Unreal sessions in real time from a web
dashboard. View active and inactive sessions, send commands, and visualize
player positions on a map.

The WebController is a client–server app for real-time communication between
engine clients (Unity/Unreal) and a Vue.js dashboard. It is built as a **single
Node.js application** — one process serves the dashboard and the realtime
WebSocket backend. No Docker, no separate proxy.

> **Architecture note.** Realtime runs over a **persistent native WebSocket**
> connection with server-resident session state. This means it must run as a
> long-lived process (Node), so it deploys on any Node host — Render, Railway,
> Fly, a VPS — with a single command. It is **not** deployable on Vercel's
> serverless functions, which cannot hold WebSocket connections or in-memory
> state. Use the one-click hosts below instead.

## Run locally

```bash
npm install        # also builds the Vue dashboard (postinstall)
npm start          # serves dashboard + WebSocket on http://localhost:4000
```

Then open:

- Dashboard: <http://localhost:4000/>
- Test interface (fake clients): <http://localhost:4000/test>

Set a password for config editing with the `PASSWORD` env var (default `0000`):

```bash
PASSWORD=aloha123 npm start
```

### Frontend dev with hot reload

To work on the Vue UI with HMR, run the Node server and the Vite dev server side
by side (Vite proxies `/ws` to the Node server):

```bash
npm start                                 # terminal 1 (backend, :4000)
npm --prefix vue-frontend run dev         # terminal 2 (Vite, :5173)
```

## Deploy

Any host that runs Node works. With Render (`render.yaml` included):

1. Push this repo to GitHub.
2. Create a new Render **Web Service** from the repo.
3. Build command `npm install`, start command `npm start`. Set `PASSWORD`.

Railway/Fly are equivalent — same build/start commands. The server reads
`process.env.PORT` (set automatically by these hosts).

> Inactive sessions are persisted to a local `inactive_sessions/` directory.
> On hosts with ephemeral disks this persists only for the life of the instance;
> attach a persistent volume if you need it to survive restarts.

## Connecting an engine client

Clients talk to the server over native WebSocket at `/ws` using a simple JSON
envelope `{ "event": ..., "data": ... }`. See **[MIGRATION.md](MIGRATION.md)**
for the full protocol and a step-by-step guide to porting the Unity/Unreal
packages off Socket.IO.

Unity package: <https://github.com/cyberspace-lab/cyberframe-webcontroller-unitypackage>
Documentation: <https://rikib1999.github.io/WebControllerDocumentation/>

## Project layout

```
server/            Node server (Express static + ws WebSocket) and session store
vue-frontend/      Vue 3 dashboard (built to vue-frontend/dist, served by the server)
static/            Test interface
MIGRATION.md       Socket.IO ➜ native WebSocket protocol & client porting guide
render.yaml        One-click deploy config
```
