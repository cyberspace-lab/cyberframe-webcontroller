# 📄 Documentation: `vite.config.js`

This configuration file is essential for setting up and customizing your Vue.js frontend application using Vite.

---

## 📑 **Table of Contents**

1. [Overview](#overview)
2. [Full Code Listing](#full-code-listing)
3. [Code Breakdown](#code-breakdown)
   - [Imports](#imports)
   - [Exported Configuration](#exported-configuration)
     - [Plugins](#plugins)
     - [Server Configuration](#server-configuration)
     - [Resolve Aliases](#resolve-aliases)

---

## 📖 **Overview**

The `vite.config.js` file is the configuration file for Vite when used with a Vue.js application. It defines how the development server behaves, how modules are resolved, and what plugins are used. In the context of our application, it is particularly important for setting up proxying to a Flask backend server and resolving module paths.

---

## 📝 **Full Code Listing**

```javascript
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    proxy: {
      '/socket.io': {
        target: 'http://flask_app:4000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

---

## 🔍 **Code Breakdown**

Let's break down the code into its constituent parts and understand each section.

### 📥 **Imports**

```javascript
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
```

- **`import { fileURLToPath, URL } from 'node:url'`**
  - Imports functions from Node.js URL module to assist in path resolution.
- **`import { defineConfig } from 'vite'`**
  - Imports the `defineConfig` helper from Vite to provide type assistance and IntelliSense.
- **`import vue from '@vitejs/plugin-vue'`**
  - Imports the official Vue plugin for Vite.

### 🚀 **Exported Configuration**

```javascript
export default defineConfig({
  // Configuration options
})
```

The `defineConfig` function helps in providing better typing support. The exported object contains several configuration options:

#### 🔌 **Plugins**

```javascript
plugins: [vue()],
```

- **`plugins: [vue()],`**
  - Registers the Vue plugin with Vite to handle `.vue` single-file components.

#### 🌐 **Server Configuration**

```javascript
server: {
  host: true,
  proxy: {
    '/socket.io': {
      target: 'http://flask_app:4000',
      ws: true,
      changeOrigin: true
    }
  }
},
```

- **`host: true`**
  - Allows the server to be accessed externally. Useful when running inside Docker or on a local network.
- **`proxy`**
  - Configures a proxy for API and WebSocket requests to avoid cross-origin issues.

**Proxy Details:**

| Option           | Description                                                                                 |
|------------------|---------------------------------------------------------------------------------------------|
| **`'/socket.io'`** | The path to proxy. All requests starting with `/socket.io` will be proxied.                |
| **`target`**     | The target server to proxy to. In this case, `http://flask_app:4000`, which is our Flask backend. |
| **`ws`**         | Enables WebSocket proxying. Set to `true` to proxy WebSocket connections.                    |
| **`changeOrigin`** | Modifies the origin of the host header to the target URL. Useful for virtual hosted sites. |

#### 📁 **Resolve Aliases**

```javascript
resolve: {
  alias: {
    '@': fileURLToPath(new URL('./src', import.meta.url))
  }
}
```

- **`alias`**
  - Creates a shortcut for importing modules, making the code cleaner and easier to maintain.
- **`'@': fileURLToPath(new URL('./src', import.meta.url))`**
  - Maps the `@` symbol to the `./src` directory, allowing imports like `import MyComponent from '@/components/MyComponent.vue'`.
