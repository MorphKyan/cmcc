<template>
  <div class="manager-section">
    <div class="manager-header">
      <h2 class="manager-title">
        <span class="manager-icon">🏷️</span>
        热词管理
      </h2>
      <p class="manager-desc">管理和动态维护ASR识别热词，提升专有名词识别准确率。</p>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3>全量热词</h3>
        <div class="header-actions">
          <button class="btn btn-secondary btn-sm" @click="fetchHotwords" :disabled="loading">
            🔄 {{ loading ? '刷新中...' : '刷新列表' }}
          </button>
          <button class="btn btn-danger btn-sm" @click="askClearAll" :disabled="loading || hotwords.length === 0">
            🗑️ 清空所有自定义
          </button>
        </div>
      </div>
      
      <!-- 添加热词区域 -->
      <div class="add-hotword-area">
        <input 
          v-model="newHotwordInput" 
          @keyup.enter="handleAddHotwords"
          type="text" 
          class="form-input" 
          placeholder="输入新热词（支持空格或逗号分隔批量添加）"
          :disabled="loading"
        >
        <button class="btn btn-primary" @click="handleAddHotwords" :disabled="loading || !newHotwordInput.trim()">
          添加热词
        </button>
      </div>

      <div v-if="loading" class="loading mt-4">
        <span class="spinner"></span>
        加载中...
      </div>
      
      <div v-else-if="hotwords.length === 0" class="no-data mt-4">
        <span class="empty-icon">📭</span>
        <p>暂无自定义热词数据。注意：部分热词是由系统从设备、资源、区域名称中自动提取的，此处仅显示您手动添加的词汇。</p>
      </div>
      
      <!-- 热词标签展示区 -->
      <div v-else class="hotword-tags mt-4">
        <transition-group name="list">
          <div v-for="word in hotwords" :key="word" class="hotword-tag">
            <span class="tag-text">{{ word }}</span>
            <button class="tag-remove" @click="handleRemoveHotword(word)" title="删除">&times;</button>
          </div>
        </transition-group>
      </div>
      
      <div class="list-footer mt-4">
        <span class="count-badge">当前自定义热词: {{ hotwords.length }} 条</span>
      </div>
      
      <transition name="fade">
        <div v-if="message" :class="['message', 'mt-4', messageClass]">
          <span class="message-icon">{{ status === 'success' ? '✅' : '❌' }}</span>
          {{ message }}
        </div>
      </transition>
    </div>

    <!-- Confirmation Modal -->
    <ConfirmationModal
      :isOpen="showConfirmModal"
      title="清空热词"
      message="确定要清空所有自定义热词吗？此操作不可恢复！"
      @confirm="executeClearAll"
      @cancel="showConfirmModal = false"
    />
  </div>
</template>

<script>
import { getHotwords, addHotwords, deleteHotwords, clearHotwords } from '../api'
import ConfirmationModal from './ConfirmationModal.vue'

export default {
  name: 'HotwordManager',
  components: {
    ConfirmationModal
  },
  data() {
    return {
      hotwords: [],
      loading: false,
      newHotwordInput: '',
      message: '',
      status: '',
      showConfirmModal: false
    }
  },
  computed: {
    messageClass() {
      return this.status === 'success' ? 'message-success' : 'message-error'
    }
  },
  mounted() {
    this.fetchHotwords()
  },
  methods: {
    async fetchHotwords() {
      this.loading = true
      this.message = ''
      try {
        const response = await getHotwords()
        this.hotwords = response.data || []
      } catch (error) {
        console.error('Failed to fetch hotwords:', error)
        this.showMessage('获取热词失败: ' + error.message, 'error')
      } finally {
        this.loading = false
      }
    },
    async handleAddHotwords() {
      if (!this.newHotwordInput.trim()) return
      
      // 解析输入：按中英文逗号、空格分割
      const rawWords = this.newHotwordInput.split(/[,，\s]+/)
      const wordsToAdd = rawWords.map(w => w.trim()).filter(w => w.length > 0)
      
      if (wordsToAdd.length === 0) return
      
      this.loading = true
      try {
        await addHotwords(wordsToAdd)
        this.showMessage(`成功添加 ${wordsToAdd.length} 个热词。注意：要使热词生效，需要在系统状态面板点击“重启ASR”。`, 'success')
        this.newHotwordInput = ''
        await this.fetchHotwords()
      } catch (error) {
        this.showMessage('添加热词失败: ' + error.message, 'error')
      } finally {
        this.loading = false
      }
    },
    async handleRemoveHotword(word) {
      if (!word) return
      this.loading = true
      try {
        await deleteHotwords([word])
        this.showMessage(`热词 "${word}" 已删除。注意：要使改动生效，请重启ASR。`, 'success')
        await this.fetchHotwords()
      } catch (error) {
        this.showMessage('删除热词失败: ' + error.message, 'error')
      } finally {
        this.loading = false
      }
    },
    askClearAll() {
      this.showConfirmModal = true
    },
    async executeClearAll() {
      this.showConfirmModal = false
      this.loading = true
      try {
        await clearHotwords()
        this.showMessage('所有自定义热词已清空。别忘记重启ASR以应用更改。', 'success')
        await this.fetchHotwords()
      } catch (error) {
        this.showMessage('清空热词失败: ' + error.message, 'error')
      } finally {
        this.loading = false
      }
    },
    showMessage(msg, stat) {
      this.message = msg
      this.status = stat
      
      if(stat === 'success') {
          setTimeout(() => {
              if (this.message === msg) this.message = ''
          }, 5000)
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

.card {
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

.add-hotword-area {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-md);
}

.add-hotword-area .form-input {
  flex: 1;
}

/* Hotword Tags */
.hotword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  min-height: 100px;
  align-items: flex-start;
}

.hotword-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  background: var(--primary-glow);
  color: var(--primary);
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.hotword-tag:hover {
  background: rgba(59, 130, 246, 0.2);
  transform: translateY(-2px);
}

.tag-remove {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.1rem;
  line-height: 1;
  padding: 0;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-remove:hover {
  opacity: 1;
  color: #ef4444;
}

.mt-4 {
  margin-top: 1rem;
}

/* List Transitions */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from {
  opacity: 0;
  transform: translateY(10px) scale(0.9);
}
.list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
.list-leave-active {
  position: absolute;
}

/* Empty State */
.no-data {
  padding: var(--space-xl);
  text-align: center;
  background: rgba(0, 0, 0, 0.2);
  border: 1px dashed var(--border-color);
  border-radius: var(--radius-md);
}

.empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: var(--space-md);
}

.no-data p {
  color: var(--text-muted);
  margin: 0;
  line-height: 1.5;
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

.message {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.message-icon {
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .add-hotword-area {
    flex-direction: column;
  }
}
</style>
