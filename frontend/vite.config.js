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
  
  // VITE_BACKEND_URL 供前端运行时使用 (决定 axios 请求的基础路径, 例如 /api)
  const backendUrl = env.VITE_BACKEND_URL || '/api'
  // VITE_PROXY_TARGET 供 Vite 本地开发服务器使用 (决定本地开发时 /api 的真实转发目标)
  const proxyTarget = env.VITE_PROXY_TARGET || 'http://127.0.0.1:8000'
  
  console.log('[Vite Config] Backend Client URL:', backendUrl)
  console.log('[Vite Config] Proxy Target:', proxyTarget)

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
      allowedHosts: ['localhost'],
      proxy: {
        '/api': {
          // 如果 backendUrl 已经是绝对地址(跨域模式)，依然可以以它优先，否则走默认本地 8000 端口
          target: backendUrl.startsWith('http') ? backendUrl : proxyTarget,
          changeOrigin: true,
          secure: false,
          ws: true
        }
      }
    }
  }
})
