import { fileURLToPath, URL } from 'node:url'
import fs from 'fs'
import path from 'path'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load environment variables
  const env = loadEnv(mode, process.cwd(), 'VITE_')

  // Configuration from environment variables with fallbacks
  const sslCert = env.VITE_SSL_CERT || 'local_morphk_icu.pem'
  const sslKey = env.VITE_SSL_KEY || 'local_morphk_icu.key'
  const backendUrl = env.VITE_BACKEND_URL || 'http://localhost:8000'
  // Library build mode for AI Assistant widget
  if (mode === 'lib') {
    return {
      plugins: [vue()],
      build: {
        lib: {
          entry: path.resolve(__dirname, 'src/embed/ai-assistant-embed.js'),
          name: 'AIAssistant',
          fileName: (format) => `ai-assistant.${format}.js`
        },
        rollupOptions: {
          // Externalize deps that shouldn't be bundled
          external: [],
          output: {
            globals: {}
          }
        },
        outDir: 'dist-widget',
        emptyOutDir: true
      },
      resolve: {
        alias: {
          '@': fileURLToPath(new URL('./src', import.meta.url))
        }
      }
    }
  }

  // Default app build
  return {
    plugins: [
      vue(),
      vueDevTools(),
    ],
    build: {
      rollupOptions: {
        input: {
          main: 'index.html',
          recorder: 'recorder.html'
        }
      }
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      cors: true,
      open: true,
      // Server options
      host: '0.0.0.0',
      port: 5173,
      cors: true,
      open: true,
      // HMR settings for Reverse Proxy (Cloudflare/NPM -> Vite)
      // When accessed via HTTPS, the browser expects WSS. 
      // NPM handles SSL, so Vite runs in HTTP mode but tells the client to connect via port 443 (HTTPS default)
      hmr: {
        clientPort: 443,
      },
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  }
})
