# 📄 Documentation: `docker-compose.yml`

This file is essential for setting up our multi-container Docker application, which includes a Flask backend, a Vue.js frontend, and a reverse proxy.

---

## 📝 **Table of Contents**

1. [Overview](#overview)
2. [Services](#services)
   - [Flask App (`flask_app`)](#1-flask-app-flask_app)
   - [Vue Frontend (`vue_frontend`)](#2-vue-frontend-vue_frontend)
   - [Proxy (`proxy`)](#3-proxy-proxy)
3. [Ports Mapping](#ports-mapping)
4. [How to Run](#how-to-run)

---

## Overview

The `docker-compose.yml` file defines the **configuration** for our Docker application, allowing us to manage multiple containers as a single service. By using Docker Compose, we can easily build, run, and scale our application components.

This setup includes:

- 🐍 A **Flask** backend (`flask_app`)
- 🌐 A **Vue.js** frontend (`vue_frontend`)
- 🔀 A **reverse proxy** (`proxy`)

---

## Services

### 1. Flask App (`flask_app`)

This service runs our Flask application, which serves as the backend server.

**Configuration Details:**

- **container_name:** `flask_app`  
  📛 Sets the container name to `flask_app` for easy identification.

- **image:** `dockerhub-flask_live_app:1.0.0`  
  🐳 Specifies the Docker image to use. Here, it uses the `dockerhub-flask_live_app` image with the tag `1.0.0`.

- **build:** `.`  
  🔨 Instructs Docker to build the image from the Dockerfile in the current directory.

- **ports:**  
  - `"4000:4000"` 🔌  
    Maps port `4000` of the host to port `4000` of the container.

**Purpose:**

The Flask app serves as the backend API, handling requests from the frontend and communicating with other services as needed.

---

### 2. Vue Frontend (`vue_frontend`)

This service runs our Vue.js application, which serves as the frontend of our application.

**Configuration Details:**

- **container_name:** `vue_frontend`  
  📛 Sets the container name to `vue_frontend`.

- **image:** `node:latest`  
  🐳 Uses the latest Node.js image to build and run the Vue.js application.

- **working_dir:** `/app`  
  📂 Sets the working directory inside the container to `/app`.

- **volumes:**  
  - `./vue-frontend:/app` 🔄  
    Mounts the local `vue-frontend` directory into the container's `/app` directory. This allows for development changes to be reflected inside the container.

- **ports:**  
  - `"5173:5173"` 🔌  
    Maps port `5173` of the host to port `5173` of the container. Vue's development server runs on port `5173` by default.

- **depends_on:**  
  - `flask_app` ⏳  
    Specifies that the `vue_frontend` service depends on the `flask_app` service. Docker Compose will ensure `flask_app` starts first.

- **command:**  
  - `["/bin/sh", "-c", "npm install && npm run dev"]` 🏃‍♂️  
    Runs a shell command inside the container to install Node.js dependencies and start the development server.

**Purpose:**

The Vue frontend provides the user interface of our application. It communicates with the Flask backend via API calls.

---

### 3. Proxy (`proxy`)

This service runs a reverse proxy server, typically Nginx, to route requests to the appropriate service.

**Configuration Details:**

- **build:** `./proxy`  
  🔨 Builds the Docker image for the proxy from the `Dockerfile` located in the `./proxy` directory.

- **ports:**  
  - `'8000:80'` 🔌  
    Maps port `8000` of the host to port `80` of the container.

**Purpose:**

The proxy server acts as a reverse proxy, forwarding client requests to the backend services. This allows for better scalability and security.

---

## Ports Mapping

Here's a summary of the port mappings:

| Service       | Container Port | Host Port |
|---------------|----------------|-----------|
| Flask App     | 4000           | 4000      |
| Vue Frontend  | 5173           | 5173      |
| Proxy         | 80             | 8000      |

---

## How to Run

To start all the services defined in the `docker-compose.yml` file:

```bash
docker-compose up --build
```

- The `--build` flag ensures that Docker builds the images before starting the containers.
- To run the containers in the background, add the `-d` flag:

```bash
docker-compose up --build -d
```
