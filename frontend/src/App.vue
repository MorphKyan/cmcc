<template>
  <div id="app" class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="app-logo">
          <span class="logo-icon">🎛️</span>
          <h1 class="logo-text">智能控制</h1>
        </div>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['nav-item', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          <span class="nav-icon">{{ tab.icon }}</span>
          <span class="nav-label">{{ tab.label }}</span>
        </button>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Top Bar (Optional, for mobile trigger or global actions) -->
      <header class="top-bar">
        <h2 class="page-title">{{ activeTabName }}</h2>
        <div class="top-actions">
           <!-- Placeholder for global actions -->
        </div>
      </header>

      <div class="content-scrollable">
        <div class="container">
          <!-- 主页内容 -->
          <Transition name="fade" mode="out-in">
            <div v-show="activeTab === 'home'" class="page-view" key="home">
              <!-- 音频录制组件 -->
              <section class="section glass-card">
                <h2 class="section-title">
                  <span class="section-icon">🎤</span>
                  语音指令
                </h2>
                <AudioRecorder />
              </section>

              <!-- 文本指令输入 -->
              <section class="section glass-card">
                <h2 class="section-title">
                  <span class="section-icon">⌨️</span>
                  文本指令
                </h2>
                <div class="query-container">
                  <div class="query-input-wrapper">
                    <input 
                      v-model="textCommandInput" 
                      @keyup.enter="handleTextCommand"
                      type="text" 
                      class="form-input query-input" 
                      placeholder="输入控制指令，例如：打开前厅的灯..."
                    >
                    <button class="btn btn-primary" @click="handleTextCommand" :disabled="isTextCommandRunning">
                      {{ isTextCommandRunning ? '执行中...' : '发送指令' }}
                    </button>
                  </div>
                  <div v-if="textCommandResult" class="query-result">
                    <h3>执行结果</h3>
                    <pre class="result-code">{{ textCommandResult }}</pre>
                  </div>
                </div>
              </section>
              
              <!-- 系统状态卡片 -->
              <section class="section glass-card">
                <div class="section-header">
                  <h2 class="section-title">
                    <span class="section-icon">📊</span>
                    系统状态
                  </h2>
                  <div class="header-actions">
                     <button class="btn btn-sm btn-primary" @click="checkHealth">刷新</button>
                  </div>
                </div>
                
                <div class="status-grid">
                  <div class="status-card">
                    <div class="status-label">LLM 健康</div>
                    <div :class="['status-value', getStatusClass(llmHealthStatus)]">{{ llmHealthStatus }}</div>
                  </div>
                  <div class="status-card">
                    <div class="status-label">RAG 状态</div>
                    <div :class="['status-value', getStatusClass(ragStatus)]">{{ ragStatus }}</div>
                  </div>
                  <div class="status-card">
                    <div class="status-label">VAD 状态</div>
                    <div :class="['status-value', getStatusClass(vadStatusText)]">{{ vadStatusText }}</div>
                  </div>
                </div>
                
                <div class="action-buttons">
                  <button class="btn btn-secondary" @click="getVadStatus">VAD 状态</button>
                  <button class="btn btn-secondary" @click="reinitializeVad">重置 VAD</button>
                  <button class="btn btn-secondary" @click="refreshRag">刷新 RAG</button>
                  <button class="btn btn-secondary" @click="reinitializeRagHandler" :disabled="isReinitializing">
                    {{ isReinitializing ? '初始化中...' : '初始化 RAG' }}
                  </button>
                  <button class="btn btn-secondary" @click="checkLLMHealth">检查 LLM</button>
                </div>
              </section>
              
              <!-- 查询功能 -->
              <section class="section glass-card">
                <h2 class="section-title">
                  <span class="section-icon">🔍</span>
                  RAG 查询
                </h2>
                <div class="query-container">
                  <div class="query-input-wrapper">
                    <input 
                      v-model="queryInput" 
                      @keyup.enter="performQuery"
                      type="text" 
                      class="form-input query-input" 
                      placeholder="输入查询内容..."
                    >
                    <button class="btn btn-primary" @click="performQuery" :disabled="isQuerying">
                      {{ isQuerying ? '查询中...' : '查询' }}
                    </button>
                  </div>
                  <div v-if="queryResult" class="query-result">
                    <h3>查询结果</h3>
                    <pre class="result-code">{{ queryResult }}</pre>
                  </div>
                </div>
              </section>

              <!-- 配置显示 -->
              <section class="section glass-card">
                <h2 class="section-title">
                  <span class="section-icon">⚙️</span>
                  当前配置
                </h2>
                <div class="config-container">
                  <div v-for="(category, catName) in config" :key="catName" class="config-category">
                    <h3 class="config-category-title">{{ catName }}</h3>
                    <div class="config-items">
                      <div v-for="(value, key) in category" :key="key" class="config-item">
                        <span class="config-key">{{ key }}</span>
                        <span class="config-value">{{ value }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </Transition>

          <!-- 设备管理 -->
          <Transition name="fade" mode="out-in">
            <div v-if="activeTab === 'devices'" class="page-view" key="devices">
              <DeviceManager />
            </div>
          </Transition>

          <!-- 资源管理 -->
          <Transition name="fade" mode="out-in">
            <div v-if="activeTab === 'resources'" class="page-view" key="resources">
              <ResourceManager />
            </div>
          </Transition>

          <!-- 区域管理 -->
          <Transition name="fade" mode="out-in">
            <div v-if="activeTab === 'areas'" class="page-view" key="areas">
              <AreaManager />
            </div>
          </Transition>

          <!-- 门禁资源管理 -->
           <Transition name="fade" mode="out-in">
            <div v-if="activeTab === 'door_resources'" class="page-view" key="doors">
              <DoorManager />
            </div>
          </Transition>

          <!-- 队列监控 -->
          <Transition name="fade" mode="out-in">
            <div v-if="activeTab === 'queue'" class="page-view" key="queue">
              <section class="section glass-card">
                <QueueMonitor />
              </section>
            </div>
          </Transition>

            <!-- 性能监控 -->
          <Transition name="fade" mode="out-in">
            <div v-if="activeTab === 'performance'" class="page-view" key="performance">
               <section class="section glass-card">
                <PerformanceChart />
              </section>
            </div>
          </Transition>

           <!-- 工具管理 -->
          <Transition name="fade" mode="out-in">
            <div v-if="activeTab === 'tools'" class="page-view" key="tools">
               <ToolManager />
            </div>
          </Transition>
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
import ToolManager from './components/ToolManager.vue'
import {
  getCurrentConfig,
  healthCheck,
  llmHealthCheck,
  queryRag,
  ragStatus,
  refreshRag,
  reinitializeRag,
  vadReinitialize,
  vadStatus,
  sendTextCommand
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
    PerformanceChart,
    ToolManager
  },
  data() {
    return {
      activeTab: 'home',
      tabs: [
        { id: 'home', label: '主页', icon: '🏠' },
        { id: 'devices', label: '设备管理', icon: '📱' },
        { id: 'resources', label: '资源管理', icon: '🎬' },
        { id: 'areas', label: '区域管理', icon: '🗺️' },
        { id: 'door_resources', label: '门禁资源管理', icon: '🚪' },
        { id: 'queue', label: '队列监控', icon: '📈' },
        { id: 'performance', label: '性能监控', icon: '⏱️' },
        { id: 'tools', label: '工具管理', icon: '🔧' }
      ],
      healthStatus: '未知',
      ragStatus: '未知',
      vadStatusText: '未知',
      llmHealthStatus: '未知',
      config: null,
      configLoading: false,
      queryInput: '',
      queryResult: null,
      isQuerying: false,
      isReinitializing: false,
      textCommandInput: '',
      textCommandResult: null,
      isTextCommandRunning: false
    }
  },
  computed: {
    activeTabName() {
      const tab = this.tabs.find(t => t.id === this.activeTab)
      return tab ? tab.label : ''
    }
  },
  methods: {
    getStatusClass(status) {
      if (!status) return 'status-unknown'
      if (status.includes('错误') || status.includes('不健康') || status.includes('失败')) return 'status-error'
      if (status === '未知' || status === '未初始化') return 'status-unknown'
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
        this.config = response.data.data
      } catch (error) {
        console.error('加载配置失败: ' + error.message)
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
        this.ragStatus = ragData.initialized
          ? `已初始化 (数据库存在: ${ragData.database_exists ? '是' : '否'})`
          : '未初始化'
      } catch (error) {
        this.ragStatus = '错误: ' + error.message
      }
    },

    async getVadStatus() {
      try {
        const response = await vadStatus()
        this.vadStatusText = response.data.data.status
      } catch (error) {
        this.vadStatusText = '错误: ' + error.message
      }
    },

    async reinitializeVad() {
      try {
        const response = await vadReinitialize()
        this.vadStatusText = response.data.data.current_status
        alert('VAD重新初始化完成: ' + response.data.data.current_status)
      } catch (error) {
        alert('重新初始化VAD失败: ' + error.message)
      }
    },
    
    async refreshRag() {
      try {
        const response = await refreshRag()
        this.ragStatus = response.data.message
      } catch (error) {
        this.ragStatus = '错误: ' + error.message
      }
    },

    async reinitializeRagHandler() {
      this.isReinitializing = true
      try {
        await reinitializeRag()
        this.ragStatus = '初始化中...'
        alert('RAG 重新初始化请求已提交，将在后台进行')
      } catch (error) {
        alert('RAG 初始化失败: ' + error.message)
      } finally {
        this.isReinitializing = false
      }
    },
    
    async performQuery() {
      if (!this.queryInput) {
        alert('请输入查询内容')
        return
      }
      
      this.isQuerying = true
      try {
        const response = await queryRag(this.queryInput)
        this.queryResult = JSON.stringify(response.data, null, 2)
      } catch (error) {
        this.queryResult = '错误: ' + error.message
      } finally {
        this.isQuerying = false
      }
    },

    async handleTextCommand() {
      if (!this.textCommandInput) {
        alert('请输入指令内容')
        return
      }

      this.isTextCommandRunning = true
      try {
        const response = await sendTextCommand(this.textCommandInput)
        this.textCommandResult = JSON.stringify(response.data, null, 2)
      } catch (error) {
        this.textCommandResult = '错误: ' + error.message
      } finally {
        this.isTextCommandRunning = false
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
      await this.loadConfig()
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
:root {
  --primary-color: #646cff;
  --bg-color: #0f172a;
  --sidebar-bg: #1e1e1e;
  --text-color: #f1f5f9;
  --border-color: rgba(255, 255, 255, 0.1);
}

body {
  margin: 0;
  background-color: var(--bg-color);
  color: var(--text-color);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* App Layout */
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: var(--bg-color);
}

/* Sidebar */
.sidebar {
  width: 260px;
  background: rgba(15, 23, 42, 0.95);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  backdrop-filter: blur(10px);
  z-index: 100;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.app-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: bold;
  color: #fff;
  cursor: pointer;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.25rem;
  margin: 0;
  background: linear-gradient(to right, #60a5fa 0%, #22d3ee 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sidebar-nav {
  flex: 1;
  padding: 1.5rem 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  color: #94a3b8;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  background: transparent;
  border: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: 0.95rem;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  transform: translateX(4px);
}

.nav-item.active {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.15), rgba(37, 99, 235, 0.05));
  color: #60a5fa;
  border-left: 3px solid #60a5fa;
  /* box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1); */
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background: rgba(0, 0, 0, 0.2);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: #94a3b8;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #94a3b8;
  position: relative;
}

.status-dot.status-ok::after {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border-radius: 50%;
  background: #10b981;
  opacity: 0.4;
  animation: pulse 2s infinite;
}

.status-dot.status-ok { background-color: #10b981; }
.status-dot.status-error { background-color: #ef4444; }
.status-dot.status-unknown { background-color: #64748b; }

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.4; }
  70% { transform: scale(1.5); opacity: 0; }
  100% { transform: scale(1); opacity: 0; }
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: radial-gradient(circle at top right, #1e293b 0%, #0f172a 100%);
}

.top-bar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  border-bottom: 1px solid var(--border-color);
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(12px);
}

.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
  letter-spacing: 0.02em;
}

.content-scrollable {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  scroll-behavior: smooth;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

/* Glass Cards & Sections */
.glass-card {
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

/* .glass-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
} */

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: #e2e8f0;
}

.section-icon {
  font-size: 1.25rem;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Status Grid */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.status-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  padding: 1.25rem;
}

.status-label {
  color: #94a3b8;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.status-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
}

.status-value.status-ok { color: #34d399; }
.status-value.status-error { color: #f87171; }

/* Buttons */
.action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
}

.btn-primary:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
  box-shadow: 0 6px 8px rgba(37, 99, 235, 0.3);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: #e2e8f0;
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
}

/* Config & Query */
.config-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.config-category {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.config-category-title {
  color: #60a5fa;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.config-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.config-item:last-child { border-bottom: none; }

.config-key { color: #94a3b8; }
.config-value { color: #f1f5f9; font-family: 'Fira Code', monospace; }

.query-input-wrapper {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.form-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  color: #fff;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.form-input:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  background: rgba(0, 0, 0, 0.4);
}

.result-code {
  background: #0f172a; /* Darker bg for code */
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
  color: #a5f3fc;
  font-family: 'Fira Code', monospace;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
}

/* Responsive */
@media (max-width: 1024px) {
  .sidebar {
    width: 220px;
  }
}

@media (max-width: 768px) {
  .app-layout {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: 64px;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 0;
    position: relative;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }
  
  .sidebar-header {
    border-bottom: none;
    padding: 0 1rem;
  }

  /* Hide normal sidebar nav on mobile, use a different approach or simplified */
  .sidebar-nav {
    display: none; 
  }

  .sidebar-footer {
    display: none;
  }

  /* Reuse activeTabName in Top Bar for context */
  .top-bar {
    display: flex;
    height: 50px;
    padding: 0 1rem;
  }
  
  /* Mobile Bottom Nav (Optional, if we want to add it, but for now fallback to tabs maybe?) 
     Ideally we'd have a hamburger menu. 
     For this task, I won't implement full mobile hamburger, just ensure it doesn't break.
     The "Top Bar" in main-content will show the title.
  */
  .main-content {
    height: calc(100vh - 64px);
  }
}
</style>
  