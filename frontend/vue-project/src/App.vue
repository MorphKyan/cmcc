<template>
  <div id="app">
    <header>
      <h1>智能控制系统</h1>
    </header>
    
    <main>
      <div class="container">
        <!-- 健康检查和状态显示 -->
        <section class="status-section">
          <h2>系统状态</h2>
          <div class="status-content">
            <p>健康检查: {{ healthStatus }}</p>
            <p>RAG 状态: {{ ragStatusInfo }}</p>
            <button @click="checkHealth">检查健康</button>
            <button @click="getRagStatus">获取 RAG 状态</button>
            <button @click="refreshRag">刷新 RAG</button>
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
        
        <!-- 文件上传 -->
        <section class="upload-section">
          <h2>上传 videos.csv</h2>
          <div class="upload-content">
            <input type="file" ref="fileInput" accept=".csv" />
            <button @click="uploadFile">上传</button>
            <p v-if="uploadMessage">{{ uploadMessage }}</p>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script>
import { healthCheck, ragStatus, refreshRag, queryRag, uploadVideos } from './api'

export default {
  name: 'App',
  data() {
    return {
      healthStatus: '未知',
      ragStatusInfo: '未知',
      queryText: '',
      queryResult: null,
      uploadMessage: ''
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
    
    async getRagStatus() {
      try {
        const response = await ragStatus()
        this.ragStatusInfo = response.data.status
      } catch (error) {
        this.ragStatusInfo = '错误: ' + error.message
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
    
    async uploadFile() {
      const file = this.$refs.fileInput.files[0]
      if (!file) {
        alert('请选择一个文件')
        return
      }
      
      try {
        const response = await uploadVideos(file)
        this.uploadMessage = response.data.message
      } catch (error) {
        this.uploadMessage = '上传失败: ' + error.message
      }
    }
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
  margin-top: 60px;
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
</style>