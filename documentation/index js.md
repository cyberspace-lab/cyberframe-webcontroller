# Documentation for `index.js`

Welcome to the documentation for the **`index.js`** file in our Vue.js frontend application! 📘✨

---

## Table of Contents

1. [Overview](#overview)
2. [Purpose](#purpose)
3. [Code Breakdown](#code-breakdown)
   - [Imports](#1-imports)
   - [Router Configuration](#2-router-configuration)
   - [Routes Definition](#3-routes-definition)
   - [Exporting the Router](#4-exporting-the-router)

---

## Overview

The `index.js` file is a core part of the Vue.js application's routing system. It sets up the routes and navigation for the frontend, allowing users to navigate between different views or components seamlessly.

---

## Purpose

The main purposes of the **`index.js`** file are:

- **Configure the Vue Router**: Initialize and set up the router for the application.
- **Define Routes**: Map URLs to components that should be rendered when a user navigates to a particular path.
- **Enable Navigation**: Allow users to navigate between different parts of the application using clean URLs without page reloads.

---

## Code Breakdown

Let's dive into the code and understand each part step by step. 🛠️🔍

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import ActiveSessions from '@/components/ActiveSessions.vue'
import ActiveSessionDetail from '@/components/ActiveSessionDetail.vue'
import InactiveSessions from '@/components/InactiveSessions.vue';
import InactiveSessionDetail from '@/components/InactiveSessionDetail.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [ /* routes array */ ]
})

export default router
```

---

### 1. Imports

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import ActiveSessions from '@/components/ActiveSessions.vue'
import ActiveSessionDetail from '@/components/ActiveSessionDetail.vue'
import InactiveSessions from '@/components/InactiveSessions.vue';
import InactiveSessionDetail from '@/components/InactiveSessionDetail.vue';
```

- **`createRouter`**: Function from **Vue Router** to create a new router instance.
- **`createWebHistory`**: Enables HTML5 History Mode, allowing cleaner URLs without the hash (`#`) symbol.
- **Components Imported**:
  - **`ActiveSessions`**: Component to display a list of active sessions.
  - **`ActiveSessionDetail`**: Component to display details of a specific active session.
  - **`InactiveSessions`**: Component to display a list of inactive sessions.
  - **`InactiveSessionDetail`**: Component to display details of a specific inactive session.

---

### 2. Router Configuration

```javascript
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [ /* routes array */ ]
})
```

- **`history`**: Configures the router to use the **HTML5 history mode** with the base URL of the application.
  - **`import.meta.env.BASE_URL`**: The base URL of the application, allowing for dynamic base paths.
- **`routes`**: An array of route definitions that map paths to components.

---

### 3. Routes Definition

```javascript
routes: [
  {
    path: '/activesessions',
    name: 'activesessions',
    component: ActiveSessions
  },
  {
    path: '/activesessiondetail/:deviceId',
    name: 'activesessiondetail',
    component: ActiveSessionDetail,
    props: true
  },
  {
    path: '/inactivesessions',
    name: 'inactivesessions',
    component: InactiveSessions
  },
  {
    path: '/inactivesessiondetail/:deviceId',
    name: 'inactivesessiondetail',
    component: InactiveSessionDetail,
    props: true
  }
]
```

Let's break down each route:

#### a. Active Sessions Route

- **Path**: `/activesessions`
- **Name**: `activesessions`
- **Component**: `ActiveSessions`

🟢 **Description**: Displays the list of active sessions in the application.

#### b. Active Session Detail Route

- **Path**: `/activesessiondetail/:deviceId`
- **Name**: `activesessiondetail`
- **Component**: `ActiveSessionDetail`
- **Props**: `true`

📄 **Description**: Shows detailed information for a specific active session identified by `deviceId`.

- **Dynamic Segment**: `:deviceId` is a dynamic parameter in the URL.
- **Props**: Setting `props: true` passes route parameters as props to the component.

#### c. Inactive Sessions Route

- **Path**: `/inactivesessions`
- **Name**: `inactivesessions`
- **Component**: `InactiveSessions`

🔴 **Description**: Displays the list of inactive (disconnected) sessions.

#### d. Inactive Session Detail Route

- **Path**: `/inactivesessiondetail/:deviceId`
- **Name**: `inactivesessiondetail`
- **Component**: `InactiveSessionDetail`
- **Props**: `true`

📄 **Description**: Shows detailed information for a specific inactive session identified by `deviceId`.

---

### 4. Exporting the Router

```javascript
export default router
```

- Exports the configured router instance so it can be imported and used in the main application instance (`main.js`).
