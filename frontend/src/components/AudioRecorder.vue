<template>
  <div class="audio-recorder">
    <div class="recorder-header">
      <h2 class="recorder-title">
        <span class="recorder-icon">🎤</span>
        网页麦克风输入
      </h2>
    </div>
    
    <div v-if="isSupported" class="recorder-content">
      <!-- Recording Controls -->
      <div class="recorder-controls">
        <button 
          class="record-btn" 
          :class="{ recording: isRecording }"
          @click="isRecording ? stopRecording() : startRecording()"
        >
          <div class="record-btn-inner">
            <span class="record-icon">{{ isRecording ? '⏹️' : '🎙️' }}</span>
          </div>
          <div v-if="isRecording" class="pulse-ring"></div>
          <div v-if="isRecording" class="pulse-ring delay"></div>
        </button>
        <p class="record-hint">{{ isRecording ? '点击停止录音' : '点击开始录音' }}</p>
      </div>

      <!-- Status Display -->
      <div class="status-display">
        <div class="status-indicator" :class="statusClass">
          <span class="status-dot"></span>
          <span class="status-text">{{ status }}</span>
        </div>
      </div>

      <!-- Audio Configuration -->
      <div v-if="actualAudioConfig" class="audio-config card">
        <h3 class="config-title">
          <span>📊</span>
          音频配置
        </h3>
        <div class="config-grid">
          <div class="config-item">
            <span class="config-label">采样率</span>
            <span class="config-value">{{ actualAudioConfig.sampleRate }} Hz</span>
          </div>
          <div class="config-item">
            <span class="config-label">声道数</span>
            <span class="config-value">{{ actualAudioConfig.channelCount }}</span>
          </div>
          <div class="config-item">
            <span class="config-label">采样位数</span>
            <span class="config-value">{{ actualAudioConfig.sampleSize }} bit</span>
          </div>
          <div class="config-item">
            <span class="config-label">上下文采样率</span>
            <span class="config-value">{{ audioContextSampleRate }} Hz</span>
          </div>
        </div>
      </div>

      <!-- WebSocket Output -->
      <div v-if="websocketOutput" class="websocket-output card">
        <h3 class="output-title">
          <span>💬</span>
          处理结果
        </h3>
        <pre class="output-content">{{ websocketOutput }}</pre>
      </div>
    </div>

    <!-- Unsupported Browser -->
    <div v-else class="unsupported">
      <span class="warning-icon">⚠️</span>
      <p>抱歉，您的浏览器不支持所需功能。</p>
      <p class="hint">请使用最新版本的 Chrome、Firefox 或 Edge 浏览器。</p>
    </div>
  </div>
</template>

<script>
import { config } from '../config';

export default {
  name: 'AudioRecorder',
  data() {
    return {
      isRecording: false,
      status: '未开始',
      isSupported: 'mediaDevices' in navigator && 'WebSocket' in window && 'AudioWorklet' in window,
      socket: null,
      audioContext: null,
      audioStream: null,
      actualAudioConfig: null,
      audioContextSampleRate: null,
      clientId: `web-client-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      websocketOutput: '',
      audioWorkletNode: null
    };
  },
  computed: {
    statusClass() {
      if (this.status.includes('错误')) return 'error';
      if (this.isRecording) return 'recording';
      if (this.status.includes('已连接') || this.status.includes('已获取')) return 'active';
      if (this.status === '已停止') return 'stopped';
      return 'idle';
    }
  },
  methods: {
    async startRecording() {
      if (this.isRecording) return;
      const audioConstraints = {
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          autoGainControl: true,
          echoCancellation: false,
          noiseSuppression: true
        }
      };
      try {
        this.audioStream = await navigator.mediaDevices.getUserMedia(audioConstraints);
        this.status = '已获取麦克风权限';

        const audioTrack = this.audioStream.getAudioTracks()[0];
        const settings = audioTrack.getSettings();
        console.log('实际应用的音频配置:', settings);

        this.actualAudioConfig = {
          sampleRate: settings.sampleRate,
          channelCount: settings.channelCount,
          sampleSize: settings.sampleSize || 16
        };

        this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
          sampleRate: 16000
        });
        this.audioContextSampleRate = this.audioContext.sampleRate;

        await this.audioContext.audioWorklet.addModule('/audio-processor.js');

        const source = this.audioContext.createMediaStreamSource(this.audioStream);

        this.audioWorkletNode = new AudioWorkletNode(this.audioContext, 'audio-processor');

        const wsUrl = config.getWebSocketUrl(this.clientId);
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = async () => {
          const metadata = {
            type: 'config',
            format: 'pcm',
            sampleRate: this.actualAudioConfig.sampleRate,
            sampleSize: this.actualAudioConfig.sampleSize,
            channelCount: this.actualAudioConfig.channelCount
          };
          this.socket.send(JSON.stringify(metadata));
          console.log('已连接到 WebSocket:', wsUrl);
          console.log('已发送元数据:', metadata);

          this.status = 'WebSocket 已连接，正在录音...';
          this.isRecording = true;

          source.connect(this.audioWorkletNode);
          this.audioWorkletNode.connect(this.audioContext.destination);

          this.audioWorkletNode.port.onmessage = (event) => {
            if (!this.isRecording || this.socket.readyState !== WebSocket.OPEN) {
              return;
            }
            this.socket.send(event.data);
          };

          if (this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
          }
        };

        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.websocketOutput = JSON.stringify(data, null, 2);
          } catch (e) {
            this.websocketOutput = event.data;
          }
        };

        this.socket.onclose = () => {
          this.status = 'WebSocket 连接已关闭';
          this.cleanup();
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket Error:', error);
          this.status = 'WebSocket 连接出错';
          this.cleanup();
        };

      } catch (error) {
        console.error('无法获取麦克风:', error);
        this.status = '错误：'+error;
      }
    },

    stopRecording() {
      if (!this.isRecording) return;
      this.status = '正在停止...';
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.close();
      }
      this.cleanup();
    },

    cleanup() {
      if (this.audioStream) {
        this.audioStream.getTracks().forEach(track => track.stop());
        this.audioStream = null;
      }

      if (this.audioContext) {
        this.audioContext.close();
        this.audioContext = null;
      }

      this.audioWorkletNode = null;
      this.socket = null;
      this.isRecording = false;
      if (this.status !== 'WebSocket 连接已关闭') {
          this.status = '已停止';
      }
    }
  },
  beforeUnmount() {
    this.stopRecording();
  }
};
</script>

<style scoped>
.audio-recorder {
  text-align: center;
}

.recorder-header {
  margin-bottom: var(--space-lg);
}

.recorder-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  font-size: 1.25rem;
  margin: 0;
}

.recorder-icon {
  font-size: 1.5rem;
}

/* Recording Controls */
.recorder-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--space-xl);
}

.record-btn {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  cursor: pointer;
  padding: 0;
  transition: all var(--transition-normal);
}

.record-btn:hover {
  transform: scale(1.05);
}

.record-btn-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-glow);
  transition: all var(--transition-normal);
}

.record-btn.recording .record-btn-inner {
  background: linear-gradient(135deg, var(--error) 0%, #dc2626 100%);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
}

.record-icon {
  font-size: 2rem;
}

/* Pulse Animation */
.pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 2px solid var(--error);
  transform: translate(-50%, -50%);
  animation: pulse-animation 1.5s ease-out infinite;
}

.pulse-ring.delay {
  animation-delay: 0.5s;
}

@keyframes pulse-animation {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(2);
    opacity: 0;
  }
}

.record-hint {
  margin-top: var(--space-md);
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* Status Display */
.status-display {
  margin-bottom: var(--space-lg);
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-input);
  border-radius: var(--radius-full);
  font-size: 0.875rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
}

.status-indicator.idle .status-dot {
  background: var(--text-muted);
}

.status-indicator.active .status-dot {
  background: var(--success);
}

.status-indicator.recording .status-dot {
  background: var(--error);
  animation: blink 1s ease-in-out infinite;
}

.status-indicator.stopped .status-dot {
  background: var(--warning);
}

.status-indicator.error .status-dot {
  background: var(--error);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.status-text {
  color: var(--text-primary);
}

/* Audio Config Card */
.audio-config {
  margin-bottom: var(--space-lg);
  text-align: left;
}

.config-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 0.9375rem;
  margin-bottom: var(--space-md);
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-sm);
}

.config-item {
  display: flex;
  justify-content: space-between;
  padding: var(--space-xs) var(--space-sm);
  background: var(--bg-input);
  border-radius: var(--radius-sm);
}

.config-label {
  color: var(--text-muted);
  font-size: 0.8125rem;
}

.config-value {
  color: var(--primary);
  font-weight: 500;
  font-size: 0.8125rem;
}

/* WebSocket Output */
.websocket-output {
  text-align: left;
}

.output-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 0.9375rem;
  margin-bottom: var(--space-md);
}

.output-content {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  color: var(--text-primary);
  background: var(--bg-input);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

/* Unsupported State */
.unsupported {
  padding: var(--space-xl);
  text-align: center;
}

.warning-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: var(--space-md);
}

.unsupported p {
  margin-bottom: var(--space-sm);
}

.unsupported .hint {
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* Responsive */
@media (max-width: 768px) {
  .config-grid {
    grid-template-columns: 1fr;
  }
}
</style>