<template>
  <div class="manager-section">
    <h2>资源管理 (视频)</h2>
    <div class="upload-box">
      <h3>批量上传视频 (JSON)</h3>
      <p class="hint">格式示例: [{"name": "视频名", "aliases": "别名", "description": "描述", "filename": "file.mp4"}]</p>
      <textarea v-model="jsonInput" placeholder="在此输入JSON数据..." rows="10"></textarea>
      <div class="actions">
        <button @click="upload" :disabled="loading">{{ loading ? '上传中...' : '上传' }}</button>
        <button @click="formatJson" class="secondary">格式化JSON</button>
      </div>
      <p v-if="message" :class="['message', status]">{{ message }}</p>
    </div>
  </div>
</template>

<script>
import { uploadVideosBatch } from '../api'

export default {
  name: 'ResourceManager',
  data() {
    return {
      jsonInput: '',
      message: '',
      status: '',
      loading: false
    }
  },
  methods: {
    async upload() {
      if (!this.jsonInput.trim()) {
        this.message = '请输入JSON数据'
        this.status = 'error'
        return
      }

      this.loading = true
      this.message = ''
      
      try {
        let items
        try {
          items = JSON.parse(this.jsonInput)
        } catch (e) {
          throw new Error('JSON格式错误: ' + e.message)
        }

        if (!Array.isArray(items)) {
          throw new Error('数据必须是JSON数组')
        }

        const response = await uploadVideosBatch(items)
        this.message = response.data.message
        this.status = 'success'
        this.jsonInput = ''
      } catch (error) {
        this.message = error.message || '上传失败'
        this.status = 'error'
      } finally {
        this.loading = false
      }
    },
    formatJson() {
      try {
        const obj = JSON.parse(this.jsonInput)
        this.jsonInput = JSON.stringify(obj, null, 2)
      } catch (e) {
        this.message = '无法格式化: JSON无效'
        this.status = 'error'
      }
    }
  }
}
</script>

<style scoped>
.manager-section {
  padding: 20px;
  text-align: left;
}

.upload-box {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #eee;
}

textarea {
  width: 100%;
  font-family: monospace;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
}

.hint {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 10px;
}

.actions {
  margin-bottom: 15px;
}

button {
  margin-right: 10px;
}

button.secondary {
  background-color: #666;
}

.message {
  padding: 10px;
  border-radius: 4px;
}

.message.success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.message.error {
  background-color: #ffebee;
  color: #c62828;
}
</style>
