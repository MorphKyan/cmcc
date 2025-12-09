<template>
  <div id="app">
    <!-- Header -->
    <header class="app-header">
      <div class="header-content">
        <h1 class="app-title">
          <span class="title-icon">🎛️</span>
          智能控制系统
        </h1>
        <nav class="nav-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            :class="['nav-tab', { active: activeTab === tab.id }]" 
            @click="activeTab = tab.id"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </nav>
      </div>
    </header>
    
    <main class="app-main">
      <div class="container">
        <!-- 主页内容 -->
        <div v-show="activeTab === 'home'" class="page-content">
          <!-- 音频录制组件 -->
          <section class="section">
            <AudioRecorder />
          </section>
          
          <!-- 系统状态卡片 -->
          <section class="section">
            <h2 class="section-title">
              <span class="section-icon">📊</span>
              系统状态
            </h2>
            <div class="status-grid">
              <div class="status-card">
                <div class="status-label">健康检查</div>
                <div :class="['status-value', getStatusClass(healthStatus)]">{{ healthStatus }}</div>
              </div>
              <div class="status-card">
                <div class="status-label">VAD 状态</div>
                <div :class="['status-value', getStatusClass(vadStatusInfo)]">{{ vadStatusInfo }}</div>
              </div>
              <div class="status-card">
                <div class="status-label">RAG 状态</div>
                <div :class="['status-value', getStatusClass(ragStatusInfo)]">{{ ragStatusInfo }}</div>
              </div>
              <div class="status-card">
                <div class="status-label">LLM 健康</div>
                <div :class="['status-value', getStatusClass(llmHealthStatus)]">{{ llmHealthStatus }}</div>
              </div>
            </div>
            <div class="action-buttons">
              <button class="btn btn-primary" @click="checkHealth">检查健康</button>
              <button class="btn btn-secondary" @click="getVadStatus">获取 VAD 状态</button>
              <button class="btn btn-secondary" @click="reinitializeVad">重启 VAD</button>
              <button class="btn btn-secondary" @click="getRagStatus">获取 RAG 状态</button>
              <button class="btn btn-secondary" @click="refreshRag">刷新 RAG</button>
              <button class="btn btn-secondary" @click="checkLLMHealth">检查 LLM 健康</button>
            </div>
          </section>
          
          <!-- 查询功能 -->
          <section class="section">
            <h2 class="section-title">
              <span class="section-icon">🔍</span>
              RAG 查询
            </h2>
            <div class="query-container">
              <div class="query-input-wrapper">
                <input 
                  v-model="queryText" 
                  class="input query-input" 
                  placeholder="请输入查询内容..." 
                  @keyup.enter="performQuery"
                />
                <button class="btn btn-primary" @click="performQuery">查询</button>
              </div>
              <div v-if="queryResult" class="query-result">
                <h3>查询结果</h3>
                <pre class="result-code">{{ queryResult }}</pre>
              </div>
            </div>
          </section>

          <!-- 配置显示 -->
          <section class="section">
            <h2 class="section-title">
              <span class="section-icon">⚙️</span>
              当前配置
            </h2>
            <div class="config-container">
              <button class="btn btn-primary" @click="loadConfig" :disabled="configLoading">
                <span v-if="configLoading" class="spinner"></span>
                {{ configLoading ? '加载中...' : '加载配置' }}
              </button>
              <div v-if="currentConfig" class="config-grid">
                <div v-for="(category, categoryName) in currentConfig" :key="categoryName" class="config-category">
                  <h3 class="config-category-title">{{ categoryName.toUpperCase() }}</h3>
                  <div class="config-items">
                    <div v-for="(value, key) in category" :key="key" class="config-item">
                      <span class="config-key">{{ key }}</span>
                      <span class="config-value">{{ value }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- 设备管理 -->
        <div v-if="activeTab === 'devices'" class="page-content">
          <DeviceManager />
        </div>

        <!-- 资源管理 -->
        <div v-if="activeTab === 'resources'" class="page-content">
          <ResourceManager />
        </div>

        <!-- 区域管理 -->
        <div v-if="activeTab === 'areas'" class="page-content">
          <AreaManager />
        </div>

        <!-- 门资源管理 -->
        <div v-if="activeTab === 'doors'" class="page-content">
          <DoorManager />
        </div>

        <!-- 队列监控 -->
        <div v-if="activeTab === 'monitoring'" class="page-content">
          <section class="section">
            <QueueMonitor />
          </section>
        </div>

        <!-- 性能监控 -->
        <div v-if="activeTab === 'performance'" class="page-content">
          <section class="section">
            <PerformanceChart />
          </section>
        </div>

      </div>
    </main>
  </div>
</template>

<script>
import AudioRecorder from './components/AudioRecorder.vue'
import DeviceManager from './components/DeviceManager.vue'
import ResourceManager from './components/ResourceManager.vue'
import AreaManager from './components/AreaManager.vue'
import DoorManager from './components/DoorManager.vue'
import QueueMonitor from './components/QueueMonitor.vue'
import PerformanceChart from './components/PerformanceChart.vue'
import {
  getCurrentConfig,
  healthCheck,
  llmHealthCheck,
  queryRag,
  ragStatus,
  refreshRag,
  vadRestart,
  vadStatus
} from './api'

export default {
  name: 'App',
  components: {
    AudioRecorder,
    DeviceManager,
    ResourceManager,
    AreaManager,
    DoorManager,
    QueueMonitor,
    PerformanceChart
  },
  data() {
    return {
      activeTab: 'home',
      tabs: [
        { id: 'home', label: '主页', icon: '🏠' },
        { id: 'devices', label: '设备管理', icon: '📱' },
        { id: 'resources', label: '资源管理', icon: '🎬' },
        { id: 'areas', label: '区域管理', icon: '🗺️' },
        { id: 'doors', label: '门资源管理', icon: '🚪' },
        { id: 'monitoring', label: '队列监控', icon: '📈' },
        { id: 'performance', label: '性能监控', icon: '⏱️' }
      ],
      healthStatus: '未知',
      ragStatusInfo: '未知',
      vadStatusInfo: '未知',
      llmHealthStatus: '未知',
      currentConfig: null,
      configLoading: false,
      queryText: '',
      queryResult: null
    }
  },
  methods: {
    getStatusClass(status) {
      if (status.includes('错误') || status.includes('不健康')) return 'status-error'
      if (status === '未知') return 'status-unknown'
      return 'status-ok'
    },
    
    async checkHealth() {
      try {
        const response = await healthCheck()
        this.healthStatus = response.data.status
      } catch (error) {
        this.healthStatus = '错误: ' + error.message
      }
    },

    async loadConfig() {
      this.configLoading = true
      try {
        const response = await getCurrentConfig()
        this.currentConfig = response.data.data
      } catch (error) {
        alert('加载配置失败: ' + error.message)
      } finally {
        this.configLoading = false
      }
    },

    async checkLLMHealth() {
      try {
        const response = await llmHealthCheck()
        this.llmHealthStatus = `${response.data.status} (${response.data.provider})`
      } catch (error) {
        this.llmHealthStatus = '不健康: ' + error.message
      }
    },

    async getRagStatus() {
      try {
        const response = await ragStatus()
        const ragData = response.data.data
        this.ragStatusInfo = ragData.initialized
          ? `已初始化 (数据库存在: ${ragData.database_exists ? '是' : '否'})`
          : '未初始化'
      } catch (error) {
        this.ragStatusInfo = '错误: ' + error.message
      }
    },

    async getVadStatus() {
      try {
        const response = await vadStatus()
        this.vadStatusInfo = response.data.data.status
      } catch (error) {
        this.vadStatusInfo = '错误: ' + error.message
      }
    },

    async reinitializeVad() {
      try {
        const response = await vadRestart()
        this.vadStatusInfo = response.data.data.current_status
        alert('VAD处理器重启请求已提交，当前状态: ' + response.data.data.current_status)
      } catch (error) {
        alert('重启VAD处理器失败: ' + error.message)
      }
    },
    
    async refreshRag() {
      try {
        const response = await refreshRag()
        this.ragStatusInfo = response.data.message
      } catch (error) {
        this.ragStatusInfo = '错误: ' + error.message
      }
    },
    
    async performQuery() {
      if (!this.queryText) {
        alert('请输入查询内容')
        return
      }
      
      try {
        const response = await queryRag(this.queryText)
        this.queryResult = JSON.stringify(response.data, null, 2)
      } catch (error) {
        this.queryResult = '错误: ' + error.message
      }
    },

    async updateStatuses() {
      if (this.activeTab === 'home') {
        await this.checkHealth()
        await this.getVadStatus()
        await this.getRagStatus()
      }
    },

    async updateAllStatuses() {
      await this.checkHealth()
      await this.getVadStatus()
      await this.getRagStatus()
      await this.checkLLMHealth()
    },

    startAutoUpdate() {
      this.updateAllStatuses()
      this.autoUpdateInterval = setInterval(() => {
        this.updateStatuses()
      }, 5000)
    },

    stopAutoUpdate() {
      if (this.autoUpdateInterval) {
        clearInterval(this.autoUpdateInterval)
        this.autoUpdateInterval = null
      }
    }
  },

  mounted() {
    this.startAutoUpdate()
  },

  beforeUnmount() {
    this.stopAutoUpdate()
  }
}
</script>

<style>
/* ===== App Layout ===== */
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ===== Header ===== */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: linear-gradient(135deg, rgba(10, 15, 26, 0.95) 0%, rgba(17, 24, 39, 0.95) 100%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  padding: var(--space-md) 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.app-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 1.5rem;
  margin: 0;
}

.title-icon {
  font-size: 1.75rem;
}

/* ===== Navigation Tabs ===== */
.nav-tabs {
  display: flex;
  gap: var(--space-xs);
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding-bottom: var(--space-xs);
}

.nav-tabs::-webkit-scrollbar {
  display: none;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-fast);
}

.nav-tab:hover {
  color: var(--text-primary);
  background: var(--glass-bg);
}

.nav-tab.active {
  color: var(--primary);
  background: rgba(20, 184, 166, 0.1);
  border-color: var(--primary);
}

.tab-icon {
  font-size: 1.125rem;
}

/* ===== Main Content ===== */
.app-main {
  flex: 1;
  padding: var(--space-xl) 0;
}

.page-content {
  animation: fadeIn 0.3s ease;
}

/* ===== Sections ===== */
.section {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
}

.section-icon {
  font-size: 1.25rem;
}

/* ===== Status Grid ===== */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.status-card {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  transition: all var(--transition-fast);
}

.status-card:hover {
  border-color: var(--border-color-hover);
  transform: translateY(-2px);
}

.status-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-xs);
}

.status-value {
  font-size: 0.9375rem;
  font-weight: 500;
  word-break: break-word;
}

.status-ok {
  color: var(--success);
}

.status-error {
  color: var(--error);
}

.status-unknown {
  color: var(--text-muted);
}

/* ===== Action Buttons ===== */
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

/* ===== Query Section ===== */
.query-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.query-input-wrapper {
  display: flex;
  gap: var(--space-sm);
}

.query-input {
  flex: 1;
}

.query-result {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
}

.query-result h3 {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-sm);
}

.result-code {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}

/* ===== Config Section ===== */
.config-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-md);
}

.config-category {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
}

.config-category-title {
  font-size: 0.75rem;
  color: var(--primary);
  letter-spacing: 0.1em;
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
}

.config-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.config-item {
  display: flex;
  justify-content: space-between;
  gap: var(--space-md);
  font-size: 0.8125rem;
  padding: var(--space-xs) 0;
}

.config-key {
  color: var(--text-secondary);
}

.config-value {
  color: var(--text-primary);
  font-weight: 500;
  text-align: right;
  word-break: break-all;
}

/* ===== Responsive Design ===== */
@media (max-width: 768px) {
  .header-content {
    padding: 0 var(--space-sm);
  }

  .app-title {
    font-size: 1.25rem;
  }

  .nav-tab {
    padding: var(--space-xs) var(--space-sm);
    font-size: 0.875rem;
  }

  .tab-label {
    display: none;
  }

  .tab-icon {
    font-size: 1.25rem;
  }

  .section {
    padding: var(--space-md);
    border-radius: var(--radius-lg);
  }

  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .btn {
    width: 100%;
  }

  .query-input-wrapper {
    flex-direction: column;
  }

  .config-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 1024px) {
  .header-content {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .nav-tabs {
    justify-content: flex-end;
  }
}
</style>