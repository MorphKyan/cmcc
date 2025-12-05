<template>
  <div class="manager-section">
    <div class="manager-header">
      <h2 class="manager-title">
        <span class="manager-icon">📱</span>
        设备管理
      </h2>
      <p class="manager-desc">批量上传设备信息到系统</p>
    </div>
    
    <div class="upload-card card">
      <div class="card-header">
        <h3>批量上传设备 (JSON)</h3>
      </div>
      
      <div class="hint-box">
        <span class="hint-icon">💡</span>
        <code class="hint-code">[{"name": "设备名", "type": "screen", "area": "区域名", "aliases": "别名", "description": "描述"}]</code>
      </div>
      
      <textarea 
        v-model="jsonInput" 
        class="textarea json-input" 
        placeholder="在此输入JSON数据..."
        rows="10"
      ></textarea>
      
      <div class="card-actions">
        <button 
          class="btn btn-primary" 
          @click="upload" 
          :disabled="loading"
        >
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '上传中...' : '上传' }}
        </button>
        <button class="btn btn-secondary" @click="formatJson">
          格式化 JSON
        </button>
      </div>
      
      <transition name="fade">
        <div v-if="message" :class="['message', messageClass]">
          <span class="message-icon">{{ status === 'success' ? '✅' : '❌' }}</span>
          {{ message }}
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { uploadDevicesBatch } from '../api'

export default {
  name: 'DeviceManager',
  data() {
    return {
      jsonInput: '',
      message: '',
      status: '',
      loading: false
    }
  },
  computed: {
    messageClass() {
      return this.status === 'success' ? 'message-success' : 'message-error'
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

        const response = await uploadDevicesBatch(items)
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
        this.message = ''
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
  animation: fadeIn 0.3s ease;
}

.manager-header {
  margin-bottom: var(--space-lg);
}

.manager-title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-xs);
}

.manager-icon {
  font-size: 1.5rem;
}

.manager-desc {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0;
}

.upload-card {
  padding: var(--space-lg);
}

.card-header h3 {
  font-size: 1rem;
  margin-bottom: var(--space-md);
  color: var(--text-primary);
}

.hint-box {
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--info-bg);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-md);
}

.hint-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.hint-code {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--info);
  word-break: break-all;
}

.json-input {
  margin-bottom: var(--space-md);
}

.card-actions {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.message {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.message-icon {
  flex-shrink: 0;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 768px) {
  .card-actions {
    flex-direction: column;
  }
  
  .card-actions .btn {
    width: 100%;
  }
}
</style>
