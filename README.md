This application allows you to monitor and interact with Unity game sessions in real-time via a web interface. You can view active and inactive sessions, send commands, and visualize player positions on a map. The WebController is a client-server application designed to enable real-time communication between Unity applications (clients) and a Vue.js frontend via a Flask backend using WebSockets (Socket.IO). The application is containerized using Docker for ease of deployment.

The following package must be integrated into your Unity project for communication with the WebController application: <https://github.com/cyberspace-lab/cyberframe-webcontroller-unitypackage>

Documentation for the WebController and the Unity package: <https://rikib1999.github.io/WebControllerDocumentation/>