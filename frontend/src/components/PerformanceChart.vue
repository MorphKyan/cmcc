<template>
  <div class="performance-chart">
    <div class="chart-header">
      <h2 class="section-title">
        <span class="section-icon">⏱️</span>
        处理性能监控
      </h2>
      <div class="header-controls">
        <div class="connection-status">
          <span :class="['status-dot', { connected: isConnected }]"></span>
          {{ isConnected ? '实时连接中' : '未连接' }}
        </div>
        <select v-model="timeRange" class="time-select">
          <option value="1">最近 1 分钟</option>
          <option value="5">最近 5 分钟</option>
        </select>
      </div>
    </div>

    <!-- 统计摘要卡片 -->
    <div class="stats-grid">
      <div v-for="(stat, key) in stats" :key="key" class="stat-card">
        <div class="stat-header">
          <span class="stat-label">{{ stat.label }}</span>
          <span class="stat-count">{{ stat.count }} 次调用</span>
        </div>
        <div class="stat-values">
          <div class="stat-item">
            <span class="stat-name">平均</span>
            <span class="stat-value">{{ formatDuration(stat.avg) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-name">最大</span>
            <span class="stat-value stat-max">{{ formatDuration(stat.max) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-name">最新</span>
            <span class="stat-value stat-latest">{{ formatDuration(stat.latest) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表容器 -->
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
    </div>

    <!-- 图例说明 -->
    <div class="chart-legend">
      <div v-for="(color, key) in metricColors" :key="key" class="legend-item">
        <span class="legend-color" :style="{ backgroundColor: color }"></span>
        <span class="legend-label">{{ metricLabels[key] || key }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import { config } from '../config'

Chart.register(...registerables)

export default {
  name: 'PerformanceChart',
  data() {
    return {
      isConnected: false,
      timeRange: '1',
      stats: {},
      metrics: {},
      metricLabels: {},
      chart: null,
      eventSource: null,
      metricColors: {
        audio_decode: '#06b6d4',      // cyan - 音频解码
        vad_input: '#14b8a6',         // teal - VAD输入
        vad_process: '#8b5cf6',       // purple - VAD处理
        asr_recognize: '#f59e0b',     // amber - ASR识别
        rag_retrieve: '#10b981',      // emerald - RAG检索
        llm_generate: '#ef4444',      // red - LLM生成
        cmd_execute: '#3b82f6'        // blue - 命令执行
      }
    }
  },
  methods: {
    connect() {
      const baseUrl = config.getBackendUrl()
      // 保持与 backendUrl 相同的协议，避免 HTTPS 页面下的混合内容问题
      const sseUrl = baseUrl + '/monitoring/metrics/stream'
      
      this.eventSource = new EventSource(sseUrl)
      
      this.eventSource.onopen = () => {
        this.isConnected = true
      }
      
      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.stats = data.stats || {}
          this.metrics = data.metrics || {}
          this.metricLabels = data.labels || {}
          this.isConnected = true
          this.updateChart()
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
    
    formatDuration(value) {
      if (value === null || value === undefined) return '-'
      if (value < 0.001) return '<1ms'
      if (value < 1) return `${(value * 1000).toFixed(0)}ms`
      return `${value.toFixed(2)}s`
    },
    
    initChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d')
      
      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [],
          datasets: []
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: 'rgba(17, 24, 39, 0.95)',
              titleColor: '#f3f4f6',
              bodyColor: '#d1d5db',
              borderColor: 'rgba(75, 85, 99, 0.3)',
              borderWidth: 1,
              padding: 12,
              callbacks: {
                label: (context) => {
                  const label = context.dataset.label || ''
                  const value = context.parsed.y
                  return `${label}: ${this.formatDuration(value)}`
                }
              }
            }
          },
          scales: {
            x: {
              grid: {
                color: 'rgba(75, 85, 99, 0.2)'
              },
              ticks: {
                color: '#9ca3af',
                maxTicksLimit: 10
              }
            },
            y: {
              grid: {
                color: 'rgba(75, 85, 99, 0.2)'
              },
              ticks: {
                color: '#9ca3af',
                callback: (value) => this.formatDuration(value)
              },
              title: {
                display: true,
                text: '耗时',
                color: '#9ca3af'
              }
            }
          }
        }
      })
    },
    
    updateChart() {
      if (!this.chart || !this.metrics) return
      
      const datasets = []
      const allTimestamps = new Set()
      
      // 收集所有时间戳
      for (const [metricType, points] of Object.entries(this.metrics)) {
        if (!points || !Array.isArray(points)) continue
        points.forEach(p => allTimestamps.add(p.timestamp))
      }
      
      // 排序时间戳
      const sortedTimestamps = Array.from(allTimestamps).sort()
      
      // 只保留最近 N 分钟的数据
      const cutoffTime = new Date(Date.now() - this.timeRange * 60 * 1000).toISOString()
      const filteredTimestamps = sortedTimestamps.filter(t => t >= cutoffTime)
      
      // 格式化时间标签
      const labels = filteredTimestamps.map(t => {
        const date = new Date(t)
        return date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit', 
          second: '2-digit' 
        })
      })
      
      // 为每个指标类型创建数据集
      for (const [metricType, points] of Object.entries(this.metrics)) {
        if (!points || !Array.isArray(points)) continue
        
        // 创建时间戳到值的映射
        const timestampToValue = {}
        points.forEach(p => {
          if (p.timestamp >= cutoffTime) {
            timestampToValue[p.timestamp] = p.duration
          }
        })
        
        // 生成数据数组（对于没有数据的时间点使用 null）
        const data = filteredTimestamps.map(t => timestampToValue[t] ?? null)
        
        datasets.push({
          label: this.metricLabels[metricType] || metricType,
          data: data,
          borderColor: this.metricColors[metricType] || '#6b7280',
          backgroundColor: (this.metricColors[metricType] || '#6b7280') + '20',
          borderWidth: 2,
          tension: 0.3,
          fill: false,
          pointRadius: 3,
          pointHoverRadius: 5,
          spanGaps: true
        })
      }
      
      this.chart.data.labels = labels
      this.chart.data.datasets = datasets
      this.chart.update('none')
    }
  },
  
  watch: {
    timeRange() {
      this.updateChart()
    }
  },
  
  mounted() {
    this.initChart()
    this.connect()
  },
  
  beforeUnmount() {
    this.disconnect()
    if (this.chart) {
      this.chart.destroy()
      this.chart = null
    }
  }
}
</script>

<style scoped>
.performance-chart {
  animation: fadeIn 0.3s ease;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
  flex-wrap: wrap;
  gap: var(--space-md);
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

.header-controls {
  display: flex;
  align-items: center;
  gap: var(--space-md);
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

.time-select {
  padding: var(--space-xs) var(--space-sm);
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
}

.time-select:hover {
  border-color: var(--border-color-hover);
}

.time-select:focus {
  outline: none;
  border-color: var(--primary);
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.stat-card {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  transition: all var(--transition-fast);
}

.stat-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
  padding-bottom: var(--space-xs);
  border-bottom: 1px solid var(--border-color);
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--primary);
}

.stat-count {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stat-values {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-name {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stat-value {
  font-size: 0.875rem;
  font-weight: 500;
  font-family: var(--font-mono);
  color: var(--text-primary);
}

.stat-max {
  color: var(--warning);
}

.stat-latest {
  color: var(--success);
}

/* 图表容器 */
.chart-container {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  height: 350px;
  margin-bottom: var(--space-md);
}

/* 图例 */
.chart-legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-md);
  padding: var(--space-sm);
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-label {
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

/* 响应式 */
@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-container {
    height: 280px;
  }
  
  .chart-legend {
    gap: var(--space-sm);
  }
  
  .legend-label {
    font-size: 0.75rem;
  }
}
</style>
