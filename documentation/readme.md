## 📑 Table of Contents

1. [Introduction](#introduction)
2. [Application Architecture](#application-architecture)
3. [Installation and Setup](#installation-and-setup)
   - [Prerequisites](#prerequisites)
   - [Docker Setup](#docker-setup)
4. [Configuration File](#configuration-file)
5. [Application Components](#application-components)

---

## Introduction

This application allows you to monitor and interact with Unity game sessions in real-time via a web interface. You can view active and inactive sessions, send commands, and visualize player positions on a map. The WebController is a client-server application designed to enable real-time communication between Unity applications (clients) and a Vue.js frontend via a Flask backend using WebSockets (Socket.IO). The application is containerized using Docker for ease of deployment.

---

## Application Architecture

The Web Controller Application is built on a **client-server architecture**:

- **Frontend**: Implemented using **Vue.js** framework.
- **Backend**: Utilizes **Flask**, a Python web framework.
- **Communication**: Real-time, two-way communication using **WebSockets** via **Socket.IO**.
- **Reverse Proxy**: **Nginx** is used to proxy requests between clients and the server.
- **Unity Integration**: Unity game sessions act as clients communicating with the server.
- **Containerization**: The application is dockerized for easy deployment.

---

## Installation and Setup

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** and **Docker Compose**
- **Git** (to clone the repository)

### Docker Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/cyberspace-lab/cyberframe-webcontroller.git
   cd webcontroller
   ```

2. **Build and Run the Docker Containers**:

   ```bash
   docker-compose up --build
   ```

   This command will:

   - Build the Flask backend and Vue frontend images.
   - Start the Nginx reverse proxy.
   - Expose the necessary ports.

## Configuration File

### **`config.json`**

This file defines application-specific configurations and behaviors.

**Structure:**

- **`applications`**: A dictionary of applications with their configurations.
  - **Application Name** (e.g., `"Diplomovka"`):
    - **`controlButtons`**: Defines buttons that can send commands to Unity clients.
    - **`receivers`**: Specifies data keys and their history limits that the backend expects to receive from Unity clients.
    - **`levels`**: Contains information about different levels/scenes, including map images and real-world dimensions.

- **`min_free_memory_percentage`**: The minimum percentage of free memory required before the app starts cleaning up inactive sessions.

#### **Example Entry:**

```json
"Diplomovka": {
  "controlButtons": [
    {
      "title": "Send some data",
      "payload": {
        "eventName": "sendSomeData",
        "parameters": {
          "duration": 5,
          "message": "number five"
        }
      }
    }
  ],
  "receivers": [
    {
      "currentColor": { "maxHistory": 5 },
      "position": { "maxHistory": 10 }
    }
  ],
  "levels": [
    {
      "1": {
        "url": "https://example.com/map1.jpg",
        "realWidth": 20,
        "realHeight": 30
      }
    }
  ]
}
```

#### **Usage:**

- **Control Buttons:**
  - Appear in the frontend under the Control Panel section.
  - When clicked, send the specified `eventName` and `parameters` to the Unity client.

- **Receivers:**
  - Define the data keys that the backend expects from Unity clients.
  - `maxHistory` specifies how many past values to store.

- **Levels:**
  - Used to render maps in the frontend.
  - Provide URLs to map images and real-world dimensions for accurate position rendering.

---

## Application Components

### Frontend (Vue.js) Application

The Vue.js frontend provides a web interface to monitor active and inactive Unity sessions, view session details, and interact with Unity applications through control panels.

#### **Key Components:**

1. **`ActiveSessions.vue`**
   - Displays a list of all active Unity sessions.
   - Allows navigation to the details of a specific active session.

2. **`ActiveSessionDetail.vue`**
   - Shows detailed information about a selected active session.
   - Provides controls to send commands to the Unity client.
   - Displays real-time position data on maps.

3. **`InactiveSessions.vue`**
   - Displays a list of inactive (disconnected) Unity sessions.
   - Allows navigation to the details of a specific inactive session.

4. **`InactiveSessionDetail.vue`**
   - Shows detailed information about a selected inactive session.
   - Provides options to save session data or delete the session.

5. **`LatestPositions.vue`**
   - A component responsible for rendering the latest position data on a canvas overlaying a map image.
   - Used in session detail views to visualize positions sent from Unity clients.

6. **`App.vue`**
   - The root component that sets up routing using `<RouterView>`.

7. **`main.js`**
   - Entry point of the Vue.js application.
   - Initializes the app, sets up Socket.IO connection, and mounts the application.

8. **`index.js`** (Router)
   - Configures the routes for the application, mapping paths to components.

9. **`config.json`**
   - Holds application-specific configurations such as control buttons, receivers, levels, and other settings.

10. **`index.html`**
    - The main HTML template for the Vue.js application.

11. **`vite.config.js`**
    - Vite configuration file for setting up the development server, including proxy settings for WebSockets.

### Backend (Flask) Application

The Flask backend manages sessions and provides communication between Unity clients and the Vue.js frontend via Socket.IO.

#### **Key Files:**

1. **`app.py`**
   - The main Flask application.
   - Manages WebSocket events, session management, and data persistence.
   - Handles connections, disconnections, data updates, and cleanup of sessions.

2. **`requirements.txt`**
   - Lists the Python dependencies required by the Flask application.