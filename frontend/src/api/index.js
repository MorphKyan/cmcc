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

export const vadReinitialize = () => {
  return api.post('/vad/reinitialize')
}

// RAG相关API
export const ragStatus = () => {
  return api.get('/rag/status')
}

export const refreshRag = () => {
  return api.post('/rag/refresh')
}

// RAG重新初始化
export const reinitializeRag = () => {
  return api.post('/rag/reinitialize')
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
  return api.post('/data/media/batch', items)
}

export const uploadDoorsBatch = (items) => {
  return api.post('/data/doors/batch', items)
}

export const getDevices = () => {
  return api.get('/data/devices')
}

export const clearDevices = () => {
  return api.delete('/data/devices')
}

export const getAreas = () => {
  return api.get('/data/areas')
}

export const clearAreas = () => {
  return api.delete('/data/areas')
}

export const getVideos = () => {
  return api.get('/data/media')
}

export const clearVideos = () => {
  return api.delete('/data/media')
}

export const getDoors = () => {
  return api.get('/data/doors')
}

export const clearDoors = () => {
  return api.delete('/data/doors')
}

// Dynamic Tools API
export const getDynamicTools = () => {
  return api.get('/tools')
}

export const addDynamicTool = (toolDef) => {
  return api.post('/tools', toolDef)
}

export const getDynamicTool = (name) => {
  return api.get(`/tools/${name}`)
}

export const deleteDynamicTool = (name) => {
  return api.delete(`/tools/${name}`)
}

// Text Pipeline API
export const sendTextCommand = (text) => {
  return api.post('/pipeline/text', { text })
}

// 默认导出axios实例，便于其他模块直接使用
export default api