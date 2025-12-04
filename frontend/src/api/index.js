import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api', // 使用相对路径，通过 Vite 代理转发到后端
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 健康检查
export const healthCheck = () => {
  return api.get('/')
}

// LLM健康检查
export const llmHealthCheck = () => {
  return api.get('/llm/health')
}

// 获取当前配置
export const getCurrentConfig = () => {
  return api.get('/config/current')
}

// VAD相关API
export const vadStatus = () => {
  return api.get('/vad/status')
}

export const vadRestart = () => {
  return api.post('/vad/restart')
}

// RAG相关API
export const ragStatus = () => {
  return api.get('/rag/status')
}

export const refreshRag = () => {
  return api.post('/rag/refresh')
}

export const queryRag = (query) => {
  return api.post('/rag/query', { query })
}

export const uploadDevicesBatch = (items) => {
  return api.post('/data/devices/batch', items)
}

export const uploadAreasBatch = (items) => {
  return api.post('/data/areas/batch', items)
}

export const uploadVideosBatch = (items) => {
  return api.post('/data/videos/batch', items)
}

export const uploadDoorsBatch = (items) => {
  return api.post('/data/doors/batch', items)
}

export const getDoors = () => {
  return api.get('/data/doors')
}

export const clearDoors = () => {
  return api.delete('/data/doors')
}

// 默认导出axios实例，便于其他模块直接使用
export default api