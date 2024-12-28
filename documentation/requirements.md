# 📄 Documentation for `requirements.txt`

---

## Overview

The `requirements.txt` file is a crucial component in Python projects, especially when working with virtual environments or deploying applications. It specifies all the Python packages and their versions that are needed to run the application. This ensures that anyone setting up the project has the exact dependencies required, leading to consistent behavior across different environments.

---

## Contents of `requirements.txt`

```plaintext
flask
flask-cors
flask-socketio
psutil
```

---

## Dependency Breakdown

Below is a detailed explanation of each of the dependencies listed in the `requirements.txt` file:

1. ### **Flask** 🌐
   - **Version:** Latest available at installation time.
   - **Description:** Flask is web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.
   - **Purpose in Project:** Acts as the core web framework for building the server-side of the application, handling routes, requests, and responses.

2. ### **Flask-CORS** 🌎
   - **Version:** Latest available at installation time.
   - **Description:** Flask-CORS is a Flask extension for handling Cross-Origin Resource Sharing (CORS), making cross-origin AJAX possible.
   - **Purpose in Project:** Allows the Flask server to accept requests from different origins, which is essential when the frontend is hosted on a different domain or port than the backend.

3. ### **Flask-SocketIO** 🔌
   - **Version:** Latest available at installation time.
   - **Description:** Flask-SocketIO enables low latency bi-directional communications between the clients and the server. It is based on Socket.IO and integrates seamlessly with Flask applications.
   - **Purpose in Project:** Facilitates real-time communication between the frontend clients and the backend server using WebSockets. Essential for features that require immediate data exchange, such as live data updates or interactive applications.

4. ### **psutil** 📊
   - **Version:** Latest available at installation time.
   - **Description:** Psutil (process and system utilities) is a cross-platform library for retrieving information on running processes and system utilization (CPU, memory, disks, network, sensors) in Python.
   - **Purpose in Project:** Used to monitor system resources like memory and CPU usage. In the context of this application, it might be used to manage sessions, cleanup resources, or log system statistics.
