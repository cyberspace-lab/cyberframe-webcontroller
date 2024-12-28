# 📄 Documentation: default.conf

---

**Filename**: `default.conf`

---

## Overview 🌐

The `default.conf` file is an **Nginx configuration file** used to set up a reverse proxy server for the application. In the context of this project, Nginx acts as a gateway that routes incoming HTTP requests to the appropriate backend services running in Docker containers.

By configuring Nginx, we ensure seamless interaction between the client (web browser) and the server components (Vue.js frontend and Flask backend) of the application.

---

## Contents 📜

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://vue_frontend:5173;
    }

    location /server {
        proxy_pass http://flask_app:4000;
    }
}
```

---

## Explanation 📝

### 1. Server Block

The configuration starts with the `server` block, which defines the settings for a virtual server handling HTTP requests.

```nginx
server {
    ...
}
```

### 2. Listen Directive

```nginx
listen 80;
```

- **Purpose**: Instructs Nginx to listen on port `80`, the default port for HTTP traffic.
- **Effect**: Allows the server to accept incoming HTTP requests on port 80.

### 3. Server Name

```nginx
server_name localhost;
```

- **Purpose**: Sets the server name to `localhost`.
- **Effect**: Nginx will respond to requests directed to `localhost`.

### 4. Location Blocks

#### a. Root Location `/`

```nginx
location / {
    proxy_pass http://vue_frontend:5173;
}
```

- **Purpose**: Captures all requests to the root path `/`.
- **Proxy Pass**: Forwards these requests to `http://vue_frontend:5173`.

  - `vue_frontend` is the name of the Docker service running the Vue.js frontend.
  - Port `5173` is the default port for Vite's development server (used by Vue.js).

- **Effect**: When a user accesses the root URL, Nginx forwards the request to the Vue.js frontend service.

#### b. API Location `/server`

```nginx
location /server {
    proxy_pass http://flask_app:4000;
}
```

- **Purpose**: Captures all requests starting with `/server`.
- **Proxy Pass**: Forwards these requests to `http://flask_app:4000`.

  - `flask_app` is the name of the Docker service running the Flask backend.
  - Port `4000` is where the Flask application is served.

- **Effect**: When the frontend makes requests to `/server`, Nginx routes them to the Flask backend.
