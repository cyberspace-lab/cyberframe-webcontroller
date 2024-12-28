# Dockerfile Documentation 📦

This documentation focuses on the **Dockerfile** used to set up the **Nginx reverse proxy** for the application.

---

## Overview

The Dockerfile is designed to create a Docker image that:

- Utilizes the official **Nginx version 1.25** as the base image.
- Customizes Nginx configuration by copying a `default.conf` file into the container.

This setup ensures that Nginx acts as a **reverse proxy server**, directing incoming traffic to the appropriate backend services within the application, such as the Flask backend and the Vue.js frontend.

---

## Dockerfile Contents

```dockerfile
FROM nginx:1.25

COPY default.conf /etc/nginx/conf.d
```

### Breakdown

1. ### **FROM nginx:1.25**

   - **Purpose**: Sets the base image for the Docker build.
   - **Explanation**: Uses the official Nginx Docker image with the specific version **1.25**. This image includes Nginx pre-installed and ready to be configured.

2. ### **COPY default.conf /etc/nginx/conf.d**

   - **Purpose**: Copies the custom Nginx configuration file into the container.
   - **Explanation**: The `default.conf` file contains specific configurations that dictate how Nginx should handle incoming requests. By copying it into `/etc/nginx/conf.d`, we customize Nginx to serve our application's needs.
