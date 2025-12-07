<template>
  <div 
    class="ai-assistant-widget"
    :class="{ 
      'is-recording': isRecording, 
      'is-connecting': isConnecting,
      'is-expanded': showResultPanel,
      'theme-dark': theme === 'dark'
    }"
    :style="widgetStyle"
    ref="widgetRef"
  >
    <!-- Floating AI Assistant Button -->
    <button 
      class="ai-btn"
      @mousedown="startDrag"
      @touchstart.passive="startDrag"
      @click="handleClick"
      :disabled="isConnecting"
      :title="buttonTitle"
    >
      <div class="ai-icon">
        <svg v-if="!isRecording && !isConnecting" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-4h2v2h-2zm1.61-9.96c-2.06-.3-3.88.97-4.43 2.79-.18.58.26 1.17.87 1.17h.2c.41 0 .74-.29.88-.67.32-.89 1.27-1.5 2.3-1.28.95.2 1.65 1.13 1.57 2.1-.1 1.34-1.62 1.63-2.45 2.88 0 .01-.01.01-.01.02-.01.02-.02.03-.03.05-.09.15-.18.32-.25.5-.01.03-.03.05-.04.08-.01.02-.01.04-.02.07-.12.34-.2.75-.2 1.25h2c0-.42.11-.77.28-1.07.02-.03.03-.06.05-.09.08-.14.18-.27.28-.39.01-.01.02-.03.03-.04.1-.12.21-.23.33-.34.96-.91 2.26-1.65 1.99-3.56-.24-1.74-1.61-3.21-3.35-3.47z"/>
        </svg>
        <svg v-else-if="isConnecting" class="spin" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5z"/>
          <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
      </div>
      <div v-if="isRecording" class="pulse-ring"></div>
    </button>

    <!-- Status Indicator -->
    <div v-if="statusText" class="status-indicator">
      {{ statusText }}
    </div>

    <!-- Result Feedback Panel -->
    <transition name="slide-up">
      <div v-if="showResultPanel" class="result-panel">
        <div class="result-header">
          <span>AI 响应</span>
          <button class="close-btn" @click="showResultPanel = false">×</button>
        </div>
        <div class="result-content">
          <div v-if="llmResult" class="result-text">{{ llmResult }}</div>
          <div v-else class="result-placeholder">等待响应...</div>
        </div>
      </div>
    </transition>

    <!-- Reconnecting Overlay -->
    <div v-if="isReconnecting" class="reconnect-overlay">
      <div class="reconnect-content">
        <span class="reconnect-spinner"></span>
        <span>重新连接中... ({{ reconnectAttempt }}/{{ maxReconnectAttempts }})</span>
      </div>
    </div>
  </div>
</template>

<script>
import Recorder from 'recorder-core';
import 'recorder-core/src/engine/pcm';

const STORAGE_KEY = 'ai-assistant-user-id';
const DEFAULT_RECONNECT_DELAY = 1000;
const MAX_RECONNECT_DELAY = 30000;
const MAX_RECONNECT_ATTEMPTS = 10;

export default {
  name: 'AIAssistantWidget',
  props: {
    backendUrl: {
      type: String,
      default: ''
    },
    theme: {
      type: String,
      default: 'dark',
      validator: (value) => ['light', 'dark'].includes(value)
    },
    initialPosition: {
      type: Object,
      default: () => ({ bottom: '20px', right: '20px' })
    }
  },
  data() {
    return {
      // Position & Drag
      position: { ...this.initialPosition },
      isDragging: false,
      hasDragged: false,
      dragStartX: 0,
      dragStartY: 0,
      elementStartX: 0,
      elementStartY: 0,
      
      // Recording State
      isRecording: false,
      isConnecting: false,
      recorder: null,
      
      // WebSocket
      socket: null,
      userId: null,
      isReconnecting: false,
      reconnectAttempt: 0,
      maxReconnectAttempts: MAX_RECONNECT_ATTEMPTS,
      reconnectDelay: DEFAULT_RECONNECT_DELAY,
      reconnectTimer: null,
      
      // Result Display
      showResultPanel: false,
      llmResult: '',
      
      // Audio Processing
      clearBufferIdx: 0,
      processTime: 0,
      send_chunk: null,
      send_lastFrame: null,
      send_pcmSampleRate: 16000,
      
      // Status
      statusText: ''
    };
  },
  computed: {
    widgetStyle() {
      const style = {};
      if (this.position.top) style.top = this.position.top;
      if (this.position.bottom) style.bottom = this.position.bottom;
      if (this.position.left) style.left = this.position.left;
      if (this.position.right) style.right = this.position.right;
      return style;
    },
    buttonTitle() {
      if (this.isConnecting) return '连接中...';
      if (this.isRecording) return '点击停止录音';
      return '点击开始录音';
    },
    wsUrl() {
      const baseUrl = this.backendUrl || this.getDefaultBackendUrl();
      try {
        const url = new URL(baseUrl);
        const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
        return `${protocol}//${url.host}/audio/ws/${this.userId}`;
      } catch {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        return `${protocol}//${baseUrl}/audio/ws/${this.userId}`;
      }
    }
  },
  mounted() {
    this.initUserId();
    document.addEventListener('mousemove', this.onDrag);
    document.addEventListener('mouseup', this.stopDrag);
    document.addEventListener('touchmove', this.onDrag, { passive: false });
    document.addEventListener('touchend', this.stopDrag);
  },
  beforeUnmount() {
    this.cleanup();
    document.removeEventListener('mousemove', this.onDrag);
    document.removeEventListener('mouseup', this.stopDrag);
    document.removeEventListener('touchmove', this.onDrag);
    document.removeEventListener('touchend', this.stopDrag);
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
  },
  methods: {
    // ========== User ID Management ==========
    initUserId() {
      let storedId = localStorage.getItem(STORAGE_KEY);
      if (!storedId) {
        storedId = `user-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
        localStorage.setItem(STORAGE_KEY, storedId);
      }
      this.userId = storedId;
      console.log('[AIAssistant] User ID:', this.userId);
    },
    
    getDefaultBackendUrl() {
      if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_BACKEND_URL) {
        return import.meta.env.VITE_BACKEND_URL;
      }
      if (typeof import.meta !== 'undefined' && import.meta.env?.PROD) {
        return window.location.origin;
      }
      // Fallback for development - use env var or localhost
      const devDomain = import.meta.env?.VITE_DEV_DOMAIN || 'localhost';
      return `https://${devDomain}:5000`;
    },

    // ========== Drag Functionality ==========
    startDrag(e) {
      if (this.isConnecting) return;
      
      this.isDragging = true;
      this.hasDragged = false;
      
      const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
      const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;
      
      this.dragStartX = clientX;
      this.dragStartY = clientY;
      
      const rect = this.$refs.widgetRef.getBoundingClientRect();
      this.elementStartX = rect.left;
      this.elementStartY = rect.top;
      
      // Convert to left/top positioning for drag
      this.position = {
        left: `${rect.left}px`,
        top: `${rect.top}px`
      };
    },
    
    onDrag(e) {
      if (!this.isDragging) return;
      
      const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX;
      const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY;
      
      const deltaX = clientX - this.dragStartX;
      const deltaY = clientY - this.dragStartY;
      
      // Consider it a drag if moved more than 5px
      if (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5) {
        this.hasDragged = true;
      }
      
      const newLeft = this.elementStartX + deltaX;
      const newTop = this.elementStartY + deltaY;
      
      // Boundary checking
      const maxX = window.innerWidth - 60;
      const maxY = window.innerHeight - 60;
      
      this.position = {
        left: `${Math.max(0, Math.min(newLeft, maxX))}px`,
        top: `${Math.max(0, Math.min(newTop, maxY))}px`
      };
      
      if (e.type.includes('touch')) {
        e.preventDefault();
      }
    },
    
    stopDrag() {
      this.isDragging = false;
    },

    // ========== Click Handler ==========
    handleClick() {
      // Ignore click if we were dragging
      if (this.hasDragged) {
        this.hasDragged = false;
        return;
      }
      
      if (this.isRecording) {
        this.stopRecording();
      } else {
        this.startRecording();
      }
    },

    // ========== Recording ==========
    async startRecording() {
      if (this.isRecording || this.isConnecting) return;
      
      this.isConnecting = true;
      this.statusText = '正在连接...';
      
      try {
        // Initialize recorder
        this.recorder = Recorder({
          type: 'unknown',
          sampleRate: 16000,
          bitRate: 16,
          onProcess: (buffers, powerLevel, bufferDuration, bufferSampleRate, newBufferIdx) => {
            this.processTime = Date.now();
            
            // Memory cleanup for long recordings
            for (let i = this.clearBufferIdx; i < newBufferIdx; i++) {
              buffers[i] = null;
            }
            this.clearBufferIdx = newBufferIdx;
            
            this.realTimeSendTry(buffers, bufferSampleRate, false);
          }
        });
        
        // Open microphone
        await new Promise((resolve, reject) => {
          this.recorder.open(resolve, (msg, isUserNotAllow) => {
            reject(new Error((isUserNotAllow ? '用户拒绝授权: ' : '') + msg));
          });
        });
        
        // Connect WebSocket
        await this.connectWebSocket();
        
        // Start recording
        this.recorder.start();
        this.isRecording = true;
        this.isConnecting = false;
        this.showResultPanel = true;
        this.statusText = '';
        
        // Watchdog timer
        this.startWatchdog();
        
      } catch (error) {
        console.error('[AIAssistant] Recording error:', error);
        this.statusText = '错误: ' + error.message;
        this.isConnecting = false;
        this.cleanup();
        setTimeout(() => { this.statusText = ''; }, 3000);
      }
    },
    
    stopRecording() {
      if (!this.isRecording) return;
      
      this.statusText = '正在停止...';
      
      if (this.recorder) {
        this.recorder.watchDogTimer = 0;
        this.recorder.close();
      }
      
      // Send final frame
      this.realTimeSendTry([], 0, true);
      
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.close(1000, 'Recording stopped');
      }
      
      this.cleanupRecording();
      this.statusText = '';
    },
    
    startWatchdog() {
      const startTime = Date.now();
      const wdt = setInterval(() => {
        if (!this.recorder || this.recorder.watchDogTimer !== wdt) {
          clearInterval(wdt);
          return;
        }
        if (Date.now() - (this.processTime || startTime) > 1500) {
          clearInterval(wdt);
          console.error('[AIAssistant]', this.processTime ? '录音被中断' : '录音未能正常开始');
          this.statusText = this.processTime ? '录音中断' : '录音启动失败';
          this.stopRecording();
        }
      }, 1000);
      this.recorder.watchDogTimer = wdt;
    },

    // ========== WebSocket ==========
    connectWebSocket() {
      return new Promise((resolve, reject) => {
        const wsUrl = this.wsUrl;
        console.log('[AIAssistant] Connecting to:', wsUrl);
        
        this.socket = new WebSocket(wsUrl);
        
        const timeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
        }, 10000);
        
        this.socket.onopen = () => {
          clearTimeout(timeout);
          console.log('[AIAssistant] WebSocket connected');
          
          // Send config metadata
          const metadata = {
            type: 'config',
            format: 'pcm',
            sampleRate: 16000,
            sampleSize: 16,
            channelCount: 1
          };
          this.socket.send(JSON.stringify(metadata));
          
          // Reset reconnect state
          this.reconnectAttempt = 0;
          this.reconnectDelay = DEFAULT_RECONNECT_DELAY;
          this.isReconnecting = false;
          
          resolve();
        };
        
        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.text || data.result || data.response) {
              this.llmResult = data.text || data.result || data.response;
            } else {
              this.llmResult = JSON.stringify(data, null, 2);
            }
          } catch {
            this.llmResult = event.data;
          }
        };
        
        this.socket.onclose = (event) => {
          console.log('[AIAssistant] WebSocket closed:', event.code, event.reason);
          if (this.isRecording && event.code !== 1000) {
            this.handleReconnect();
          }
        };
        
        this.socket.onerror = (error) => {
          clearTimeout(timeout);
          console.error('[AIAssistant] WebSocket error:', error);
          reject(new Error('WebSocket连接失败'));
        };
      });
    },
    
    handleReconnect() {
      if (this.reconnectAttempt >= this.maxReconnectAttempts) {
        console.log('[AIAssistant] Max reconnect attempts reached');
        this.statusText = '连接失败，请重试';
        this.cleanupRecording();
        return;
      }
      
      this.isReconnecting = true;
      this.reconnectAttempt++;
      
      console.log(`[AIAssistant] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempt})`);
      
      this.reconnectTimer = setTimeout(async () => {
        try {
          await this.connectWebSocket();
          console.log('[AIAssistant] Reconnected successfully');
        } catch (error) {
          console.error('[AIAssistant] Reconnect failed:', error);
          // Exponential backoff
          this.reconnectDelay = Math.min(this.reconnectDelay * 2, MAX_RECONNECT_DELAY);
          this.handleReconnect();
        }
      }, this.reconnectDelay);
    },

    // ========== Audio Processing ==========
    realTimeSendTry(buffers, bufferSampleRate, isClose) {
      let pcm = new Int16Array(0);
      
      if (buffers.length > 0) {
        const chunk = Recorder.SampleData(buffers, bufferSampleRate, 16000, this.send_chunk);
        this.send_chunk = chunk;
        pcm = chunk.data;
        this.send_pcmSampleRate = chunk.sampleRate;
      }
      
      this.transferUpload(pcm, isClose);
    },
    
    transferUpload(pcmFrame, isClose) {
      if (isClose && pcmFrame.length === 0) {
        const len = this.send_lastFrame ? this.send_lastFrame.length : Math.round(this.send_pcmSampleRate / 1000 * 50);
        pcmFrame = new Int16Array(len);
      }
      this.send_lastFrame = pcmFrame;
      
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(pcmFrame.buffer);
      }
    },

    // ========== Cleanup ==========
    cleanupRecording() {
      this.recorder = null;
      this.socket = null;
      this.isRecording = false;
      this.isConnecting = false;
      this.clearBufferIdx = 0;
      this.processTime = 0;
      this.send_chunk = null;
      this.send_lastFrame = null;
    },
    
    cleanup() {
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
      }
      this.stopRecording();
    }
  }
};
</script>

<style scoped>
.ai-assistant-widget {
  position: fixed;
  z-index: 99999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

/* AI Button */
.ai-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.ai-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.ai-btn:active {
  transform: scale(0.98);
}

.ai-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.ai-icon {
  width: 28px;
  height: 28px;
  color: white;
}

.ai-icon svg {
  width: 100%;
  height: 100%;
}

/* Recording State */
.is-recording .ai-btn {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  box-shadow: 0 4px 15px rgba(245, 87, 108, 0.5);
}

/* Connecting State */
.is-connecting .ai-btn {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

/* Pulse Animation */
.pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid rgba(245, 87, 108, 0.6);
  animation: pulse 1.5s ease-out infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.8);
    opacity: 0;
  }
}

/* Spin Animation */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Status Indicator */
.status-indicator {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
}

/* Result Panel */
.result-panel {
  position: absolute;
  bottom: 70px;
  right: 0;
  width: 300px;
  max-height: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.theme-dark .result-panel {
  background: #1e1e2e;
  color: #cdd6f4;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  font-weight: 600;
}

.theme-dark .result-header {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: inherit;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}

.result-content {
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.result-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}

.result-placeholder {
  color: #888;
  text-align: center;
  padding: 20px;
}

/* Slide Animation */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Reconnect Overlay */
.reconnect-overlay {
  position: absolute;
  bottom: 70px;
  right: 0;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 12px;
}

.reconnect-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reconnect-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>
