import { fileURLToPath, URL } from 'node:url'
import fs from 'fs'
import path from 'path'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
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
      https: {
        cert: fs.readFileSync(path.resolve(__dirname, 'local_morphk_icu.pem')),
        key: fs.readFileSync(path.resolve(__dirname, 'local_morphk_icu.key'))
      },
      proxy: {
        '/api': {
          target: 'https://local.morph.icu:5000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  }
})
