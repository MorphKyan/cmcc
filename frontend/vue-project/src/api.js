// src/api.js
import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:5000', // FastAPI 服务的地址
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 健康检查
export const healthCheck = () => {
  return api.get('/')
}

// 刷新 RAG 数据库
export const refreshRag = () => {
  return api.post('/rag/refresh')
}

// 获取 RAG 状态
export const ragStatus = () => {
  return api.get('/rag/status')
}

// 查询 RAG 数据库
export const queryRag = (query) => {
  return api.post('/rag/query', { query })
}

// 上传 videos.csv 文件
export const uploadVideos = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return api.post('/rag/upload-videos', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export default api