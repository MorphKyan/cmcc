<template>
  <div class="queue-monitor">
    <div class="monitor-header">
      <h2 class="section-title">
        <span class="section-icon">📊</span>
        队列监控
      </h2>
      <div class="connection-status">
        <span :class="['status-dot', { connected: isConnected }]"></span>
        {{ isConnected ? '实时连接中' : '未连接' }}
      </div>
    </div>

    <!-- 汇总信息 -->
    <div class="summary-bar">
      <div class="summary-item">
        <span class="summary-label">活跃连接</span>
        <span class="summary-value">{{ activeConnections }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">最后更新</span>
        <span class="summary-value">{{ lastUpdateTime }}</span>
      </div>
    </div>

    <!-- 无连接提示 -->
    <div v-if="contexts.length === 0" class="empty-state">
      <span class="empty-icon">📭</span>
      <p>暂无活跃的 WebSocket 连接</p>
    </div>

    <!-- 用户队列卡片 -->
    <div v-else class="contexts-grid">
      <div v-for="ctx in contexts" :key="ctx.context_id" class="context-card">
        <div class="context-header">
          <span class="context-id">{{ ctx.context_id }}</span>
        </div>
        <div class="queues-list">
          <div v-for="(queue, name) in getQueues(ctx)" :key="name" class="queue-item">
            <div class="queue-label">{{ getQueueLabel(name) }}</div>
            <div class="queue-bar-container">
              <div 
                class="queue-bar" 
                :style="{ width: getPercentage(queue) + '%' }"
                :class="getBarClass(queue)"
              ></div>
            </div>
            <div class="queue-value">
              {{ queue.current }} / {{ queue.max }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { config } from '../config'

export default {
  name: 'QueueMonitor',
  data() {
    return {
      isConnected: false,
      activeConnections: 0,
      lastUpdateTime: '-',
      contexts: [],
      eventSource: null
    }
  },
  methods: {
    connect() {
      const baseUrl = config.getBackendUrl()
      // 保持与 backendUrl 相同的协议，避免 HTTPS 页面下的混合内容问题
      const sseUrl = baseUrl + '/monitoring/queues/stream'
      
      this.eventSource = new EventSource(sseUrl)
      
      this.eventSource.onopen = () => {
        this.isConnected = true
      }
      
      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.activeConnections = data.active_connections
          this.contexts = data.contexts || []
          this.lastUpdateTime = new Date(data.timestamp).toLocaleTimeString()
          this.isConnected = true
        } catch (e) {
          console.error('解析 SSE 数据失败:', e)
        }
      }
      
      this.eventSource.onerror = () => {
        this.isConnected = false
        // 5 秒后重连
        setTimeout(() => {
          if (this.eventSource) {
            this.eventSource.close()
            this.connect()
          }
        }, 5000)
      }
    },
    
    disconnect() {
      if (this.eventSource) {
        this.eventSource.close()
        this.eventSource = null
        this.isConnected = false
      }
    },
    
    getQueues(ctx) {
      // 动态获取所有队列数据 (排除 context_id)
      const queues = {}
      for (const [key, value] of Object.entries(ctx)) {
        if (key !== 'context_id' && value && typeof value === 'object' && 'current' in value && 'max' in value) {
          queues[key] = value
        }
      }
      return queues
    },
    
    getQueueLabel(name) {
      const labels = {
        audio_input: '音频输入',
        audio_np: '音频解码',
        audio_segment: 'VAD 分段',
        asr_output: 'ASR 输出',
        command: '命令队列',
        vad_chunk: 'VAD 块'
      }
      return labels[name] || name
    },
    
    getPercentage(queue) {
      if (!queue || queue.max === 0) return 0
      return Math.min(100, (queue.current / queue.max) * 100)
    },
    
    getBarClass(queue) {
      const pct = this.getPercentage(queue)
      if (pct >= 80) return 'bar-danger'
      if (pct >= 50) return 'bar-warning'
      return 'bar-normal'
    }
  },
  
  mounted() {
    this.connect()
  },
  
  beforeUnmount() {
    this.disconnect()
  }
}
</script>

<style scoped>
.queue-monitor {
  animation: fadeIn 0.3s ease;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin: 0;
}

.section-icon {
  font-size: 1.25rem;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--error);
  animation: pulse 2s infinite;
}

.status-dot.connected {
  background-color: var(--success);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.summary-bar {
  display: flex;
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
  padding: var(--space-md);
  background: var(--bg-input);
  border-radius: var(--radius-lg);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.summary-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--primary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl);
  color: var(--text-muted);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--space-md);
}

.contexts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--space-md);
}

.context-card {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  transition: all var(--transition-fast);
}

.context-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
}

.context-header {
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
}

.context-id {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--primary);
  font-family: var(--font-mono);
}

.queues-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.queue-item {
  display: grid;
  grid-template-columns: 80px 1fr 60px;
  align-items: center;
  gap: var(--space-sm);
}

.queue-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.queue-bar-container {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.queue-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.bar-normal {
  background: linear-gradient(90deg, var(--success), var(--primary));
}

.bar-warning {
  background: linear-gradient(90deg, var(--warning), #f97316);
}

.bar-danger {
  background: linear-gradient(90deg, var(--error), #dc2626);
  animation: pulse 1s infinite;
}

.queue-value {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: right;
  font-family: var(--font-mono);
}

@media (max-width: 768px) {
  .summary-bar {
    flex-direction: column;
    gap: var(--space-sm);
  }
  
  .contexts-grid {
    grid-template-columns: 1fr;
  }
  
  .queue-item {
    grid-template-columns: 70px 1fr 50px;
  }
}
</style>
