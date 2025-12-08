<template>
  <div class="manager-section">
    <div class="manager-header">
      <h2 class="manager-title">
        <span class="manager-icon">🚪</span>
        门资源管理
      </h2>
      <p class="manager-desc">管理和批量上传门资源信息</p>
    </div>
    
    <!-- Existing Doors List -->
    <div class="list-card card">
      <div class="card-header">
        <h3>现有门资源</h3>
        <div class="header-actions">
          <button class="btn btn-secondary btn-sm" @click="fetchDoors">
            🔄 刷新列表
          </button>
          <button class="btn btn-danger btn-sm" @click="clearAllDoors">
            🗑️ 清空所有
          </button>
        </div>
      </div>
      
      <div v-if="loadingList" class="loading">
        <span class="spinner"></span>
        加载中...
      </div>
      
      <div v-else-if="doors.length === 0" class="no-data">
        <span class="empty-icon">📭</span>
        <p>暂无门资源数据</p>
      </div>
      
      <div v-else class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>名称</th>
              <th>类型</th>
              <th>区域1</th>
              <th>区域2</th>
              <th>位置</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="door in doors" :key="door.name">
              <td>
                <span class="door-name">{{ door.name }}</span>
              </td>
              <td>
                <span class="door-type">{{ door.type }}</span>
              </td>
              <td>{{ door.area1 }}</td>
              <td>{{ door.area2 }}</td>
              <td>{{ door.location }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="list-footer">
        <span class="count-badge">共 {{ doors.length }} 条记录</span>
      </div>
    </div>

    <!-- Upload Section -->
    <div class="upload-card card">
      <div class="card-header">
        <h3>批量上传门资源 (JSON)</h3>
      </div>
      
      <div class="hint-box">
        <span class="hint-icon">💡</span>
        <code class="hint-code">[{"name": "门1", "type": "normal", "area1": "区域A", "area2": "区域B", "location": "位置描述"}]</code>
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
          :disabled="uploading"
        >
          <span v-if="uploading" class="spinner"></span>
          {{ uploading ? '上传中...' : '上传' }}
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

    <!-- Confirmation Modal -->
    <ConfirmationModal
      :isOpen="showConfirmModal"
      title="清空门资源"
      message="确定要清空所有门资源数据吗？此操作不可恢复！"
      @confirm="executeClearAll"
      @cancel="showConfirmModal = false"
    />
  </div>
</template>

<script>
import { uploadDoorsBatch, getDoors, clearDoors } from '../api'
import ConfirmationModal from './ConfirmationModal.vue'

export default {
  name: 'DoorManager',
  components: {
    ConfirmationModal
  },
  data() {
    return {
      doors: [],
      loadingList: false,
      jsonInput: '',
      message: '',
      status: '',
      uploading: false,
      showConfirmModal: false
    }
  },
  computed: {
    messageClass() {
      return this.status === 'success' ? 'message-success' : 'message-error'
    }
  },
  mounted() {
    this.fetchDoors()
  },
  methods: {
    async fetchDoors() {
      this.loadingList = true
      try {
        const response = await getDoors()
        this.doors = response.data
      } catch (error) {
        console.error('Failed to fetch doors:', error)
        this.message = '获取门资源列表失败: ' + error.message
        this.status = 'error'
      } finally {
        this.loadingList = false
      }
    },
    async upload() {
      if (!this.jsonInput.trim()) {
        this.message = '请输入JSON数据'
        this.status = 'error'
        return
      }

      this.uploading = true
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

        const response = await uploadDoorsBatch(items)
        this.message = response.data.message
        this.status = 'success'
        this.jsonInput = ''
        this.fetchDoors()
      } catch (error) {
        this.message = error.message || '上传失败'
        this.status = 'error'
      } finally {
        this.uploading = false
      }
    },
    clearAllDoors() {
      this.showConfirmModal = true
    },
    async executeClearAll() {
      this.showConfirmModal = false
      try {
        await clearDoors()
        this.message = '数据已清空'
        this.status = 'success'
        this.fetchDoors()
      } catch (error) {
        this.message = '清空失败: ' + error.message
        this.status = 'error'
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

/* List Card */
.list-card {
  margin-bottom: var(--space-lg);
  padding: var(--space-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.card-header h3 {
  font-size: 1rem;
  margin: 0;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
}

/* Table */
.table-wrapper {
  margin-bottom: var(--space-md);
}

.door-name {
  font-weight: 500;
  color: var(--text-primary);
}

.door-type {
  display: inline-block;
  padding: var(--space-xs) var(--space-sm);
  background: var(--primary-glow);
  color: var(--primary);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}

/* Empty State */
.no-data {
  padding: var(--space-xl);
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: var(--space-md);
}

.no-data p {
  color: var(--text-muted);
  margin: 0;
}

/* List Footer */
.list-footer {
  display: flex;
  justify-content: flex-end;
}

.count-badge {
  display: inline-block;
  padding: var(--space-xs) var(--space-sm);
  background: var(--bg-input);
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* Upload Card */
.upload-card {
  padding: var(--space-lg);
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
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
  }

  .card-actions {
    flex-direction: column;
  }
  
  .card-actions .btn {
    width: 100%;
  }

  .table-wrapper {
    margin: 0 calc(-1 * var(--space-lg));
    border-radius: 0;
    border-left: none;
    border-right: none;
  }
}
</style>
