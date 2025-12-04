<template>
  <div id="app">
    <header>
      <h1>智能控制系统</h1>
      <nav class="tabs">
        <button 
          :class="{ active: activeTab === 'home' }" 
          @click="activeTab = 'home'"
        >主页</button>
        <button 
          :class="{ active: activeTab === 'devices' }" 
          @click="activeTab = 'devices'"
        >设备管理</button>
        <button 
          :class="{ active: activeTab === 'resources' }" 
          @click="activeTab = 'resources'"
        >资源管理</button>
        <button 
          :class="{ active: activeTab === 'areas' }" 
          @click="activeTab = 'areas'"
        >区域管理</button>
        <button 
          :class="{ active: activeTab === 'doors' }" 
          @click="activeTab = 'doors'"
        >门资源管理</button>
      </nav>
    </header>
    
    <main>
      <div class="container">
        <!-- 主页内容 -->
        <div v-show="activeTab === 'home'">
          <!-- 音频录制组件 -->
          <section class="audio-section">
            <AudioRecorder />
          </section>
          
          <!-- 健康检查和状态显示 -->
          <section class="status-section">
            <h2>系统状态</h2>
            <div class="status-content">
              <p>健康检查: {{ healthStatus }}</p>
              <p>VAD 状态: {{ vadStatusInfo }}</p>
              <p>RAG 状态: {{ ragStatusInfo }}</p>
              <p>LLM 健康: {{ llmHealthStatus }}</p>
              <button @click="checkHealth">检查健康</button>
              <button @click="getVadStatus">获取 VAD 状态</button>
              <button @click="reinitializeVad">重启 VAD</button>
              <button @click="getRagStatus">获取 RAG 状态</button>
              <button @click="refreshRag">刷新 RAG</button>
              <button @click="checkLLMHealth">检查 LLM 健康</button>
            </div>
          </section>
          
          <!-- 查询功能 -->
          <section class="query-section">
            <h2>RAG 查询</h2>
            <div class="query-content">
              <input v-model="queryText" placeholder="请输入查询内容" />
              <button @click="performQuery">查询</button>
              <div v-if="queryResult" class="query-result">
                <h3>查询结果:</h3>
                <pre>{{ queryResult }}</pre>
              </div>
            </div>
          </section>

          <!-- 配置显示 -->
          <section class="config-section">
            <h2>当前配置</h2>
            <div class="config-content">
              <button @click="loadConfig" :disabled="configLoading">
                {{ configLoading ? '加载中...' : '加载配置' }}
              </button>
              <div v-if="currentConfig" class="config-display">
                <div v-for="(category, categoryName) in currentConfig" :key="categoryName" class="config-category">
                  <h3>{{ categoryName.toUpperCase() }} 配置</h3>
                  <div v-for="(value, key) in category" :key="key" class="config-item">
                    <strong>{{ key }}:</strong> {{ value }}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- 设备管理 -->
        <div v-if="activeTab === 'devices'">
          <DeviceManager />
        </div>

        <!-- 资源管理 -->
        <div v-if="activeTab === 'resources'">
          <ResourceManager />
        </div>

        <!-- 区域管理 -->
        <div v-if="activeTab === 'areas'">
          <AreaManager />
        </div>

        <!-- 门资源管理 -->
        <div v-if="activeTab === 'doors'">
          <DoorManager />
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
    DoorManager
  },
  data() {
    return {
      activeTab: 'home',
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

    // 定期更新状态
    async updateStatuses() {
      if (this.activeTab === 'home') {
        await this.checkHealth()
        await this.getVadStatus()
        await this.getRagStatus()
      }
    },

    // 第一次更新所有状态
    async updateAllStatuses() {
      await this.checkHealth()
      await this.getVadStatus()
      await this.getRagStatus()
      await this.checkLLMHealth()
    },

    // 启动定时更新
    startAutoUpdate() {
      this.updateAllStatuses() // 立即更新一次
      this.autoUpdateInterval = setInterval(() => {
        this.updateStatuses()
      }, 5000) // 每5秒更新一次
    },

    // 停止定时更新
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
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
}

.tabs {
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.tabs button {
  background: none;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  border-bottom: 2px solid transparent;
  margin: 0 5px;
}

.tabs button.active {
  color: #42b983;
  border-bottom: 2px solid #42b983;
  font-weight: bold;
}

.tabs button:hover {
  color: #42b983;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 8px 16px;
  margin: 5px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #359c6d;
}

button:disabled {
  background-color: #a8d5c2;
  cursor: not-allowed;
}

input {
  padding: 8px;
  margin: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.query-result {
  margin-top: 20px;
  text-align: left;
}

.query-result pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.config-section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.config-category {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.config-item {
  margin: 5px 0;
  padding: 5px;
  background-color: #f9f9f9;
  border-radius: 3px;
}

.config-item strong {
  color: #333;
}
</style>