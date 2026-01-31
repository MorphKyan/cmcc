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
  console.log('[Vite Config] Backend URL:', backendUrl)
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
      open: false,  // 禁止自动打开浏览器（服务器环境）
      allowedHosts: ['web.cmcc.morphk.icu', 'localhost'],
      // HMR settings for Reverse Proxy (NPM -> Vite, 不经过 Cloudflare)
      // NPM 处理 SSL 终结，Vite 运行在 HTTP 模式
      // 客户端通过 WSS (HTTPS 默认端口 443) 连接 HMR
      hmr: {
        protocol: 'wss',        // 使用 WebSocket Secure
        host: 'web.cmcc.morphk.icu',
        clientPort: 8443,       // 使用非标准端口（运营商封锁443）
      },
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '')
        },
        '/vad': {
          target: backendUrl,
          changeOrigin: true,
          secure: false
        },
        '/rag': {
          target: backendUrl,
          changeOrigin: true,
          secure: false
        },
        '/llm': {
          target: backendUrl,
          changeOrigin: true,
          secure: false
        },
        '/config': {
          target: backendUrl,
          changeOrigin: true,
          secure: false
        }
      }
    }
  }
})
