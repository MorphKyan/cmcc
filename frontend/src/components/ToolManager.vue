<template>
  <div class="manager-section">
    <div class="manager-header">
      <h2 class="manager-title">
        <span class="manager-icon">🔧</span>
        动态工具管理
      </h2>
      <p class="manager-desc">管理 LLM 可调用的动态外部工具</p>
    </div>
    
    <!-- Existing Tools List -->
    <div class="list-card card">
      <div class="card-header">
        <h3>已注册工具</h3>
        <div class="header-actions">
          <button class="btn btn-secondary btn-sm" @click="fetchTools">
            🔄 刷新列表
          </button>
        </div>
      </div>
      
      <div v-if="loadingList" class="loading">
        <span class="spinner"></span>
        加载中...
      </div>
      
      <div v-else-if="tools.length === 0" class="no-data">
        <span class="empty-icon">🔧</span>
        <p>暂无动态工具</p>
      </div>
      
      <div v-else class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>工具名称</th>
              <th>描述</th>
              <th>API 端点</th>
              <th>方法</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tool in tools" :key="tool.name">
              <td>
                <span class="item-name">{{ tool.name }}</span>
              </td>
              <td>{{ tool.description }}</td>
              <td>
                <code class="endpoint-code">{{ tool.api_config.endpoint }}</code>
              </td>
              <td>
                <span class="method-badge">{{ tool.api_config.method }}</span>
              </td>
              <td>
                <button class="btn btn-danger btn-sm" @click="confirmDelete(tool.name)">
                  🗑️ 删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="list-footer">
        <span class="count-badge">共 {{ tools.length }} 个工具</span>
      </div>
    </div>

    <!-- Add Tool Section -->
    <div class="upload-card card">
      <div class="card-header">
        <h3>添加动态工具</h3>
      </div>
      
      <div class="hint-box">
        <span class="hint-icon">💡</span>
        <span>填写工具配置，LLM 将可以调用此工具。工具执行时会向指定 API 端点发送请求。</span>
      </div>

      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">工具名称 *</label>
          <input 
            v-model="newTool.name" 
            class="input" 
            placeholder="如: get_weather"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">工具描述 *</label>
          <input 
            v-model="newTool.description" 
            class="input" 
            placeholder="如: 获取指定城市的天气信息"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">API 端点 *</label>
          <input 
            v-model="newTool.api_config.endpoint" 
            class="input" 
            placeholder="如: https://api.example.com/weather"
          />
        </div>
        
        <div class="form-group">
          <label class="form-label">HTTP 方法</label>
          <select v-model="newTool.api_config.method" class="input">
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>
        
        <div class="form-group">
          <label class="form-label">超时时间 (秒)</label>
          <input 
            v-model.number="newTool.api_config.timeout" 
            class="input" 
            type="number"
            min="1"
            max="60"
          />
        </div>
      </div>

      <!-- Parameters Section -->
      <div class="params-section">
        <div class="params-header">
          <h4>参数定义</h4>
          <button class="btn btn-secondary btn-sm" @click="addParameter">
            ➕ 添加参数
          </button>
        </div>
        
        <div v-if="parameters.length === 0" class="no-params">
          暂无参数，点击上方按钮添加
        </div>
        
        <div v-else class="params-list">
          <div v-for="(param, index) in parameters" :key="index" class="param-item">
            <input 
              v-model="param.name" 
              class="input param-input" 
              placeholder="参数名"
            />
            <select v-model="param.type" class="input param-select">
              <option value="str">字符串</option>
              <option value="int">整数</option>
              <option value="float">浮点数</option>
              <option value="bool">布尔值</option>
            </select>
            <input 
              v-model="param.description" 
              class="input param-desc" 
              placeholder="参数描述"
            />
            <label class="param-required">
              <input type="checkbox" v-model="param.required" />
              必填
            </label>
            <button class="btn btn-danger btn-sm" @click="removeParameter(index)">
              ✕
            </button>
          </div>
        </div>
      </div>
      
      <div class="card-actions">
        <button 
          class="btn btn-primary" 
          @click="addTool" 
          :disabled="adding || !isFormValid"
        >
          <span v-if="adding" class="spinner"></span>
          {{ adding ? '添加中...' : '添加工具' }}
        </button>
        <button class="btn btn-secondary" @click="resetForm">
          重置表单
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
      title="删除工具"
      :message="`确定要删除工具 '${toolToDelete}' 吗？`"
      @confirm="executeDelete"
      @cancel="showConfirmModal = false"
    />
  </div>
</template>

<script>
import { getDynamicTools, addDynamicTool, deleteDynamicTool } from '../api'
import ConfirmationModal from './ConfirmationModal.vue'

export default {
  name: 'ToolManager',
  components: {
    ConfirmationModal
  },
  data() {
    return {
      tools: [],
      loadingList: false,
      adding: false,
      message: '',
      status: '',
      showConfirmModal: false,
      toolToDelete: '',
      newTool: {
        name: '',
        description: '',
        api_config: {
          endpoint: '',
          method: 'POST',
          timeout: 10.0,
          headers: null
        }
      },
      parameters: []
    }
  },
  computed: {
    messageClass() {
      return this.status === 'success' ? 'message-success' : 'message-error'
    },
    isFormValid() {
      return this.newTool.name.trim() && 
             this.newTool.description.trim() && 
             this.newTool.api_config.endpoint.trim()
    }
  },
  mounted() {
    this.fetchTools()
  },
  methods: {
    async fetchTools() {
      this.loadingList = true
      try {
        const response = await getDynamicTools()
        this.tools = response.data.tools
      } catch (error) {
        console.error('Failed to fetch tools:', error)
        this.message = '获取工具列表失败: ' + error.message
        this.status = 'error'
      } finally {
        this.loadingList = false
      }
    },
    
    addParameter() {
      this.parameters.push({
        name: '',
        type: 'str',
        description: '',
        required: true
      })
    },
    
    removeParameter(index) {
      this.parameters.splice(index, 1)
    },
    
    async addTool() {
      if (!this.isFormValid) {
        this.message = '请填写必填项'
        this.status = 'error'
        return
      }

      this.adding = true
      this.message = ''
      
      try {
        // 构建参数对象
        const parametersObj = {}
        for (const param of this.parameters) {
          if (param.name.trim()) {
            parametersObj[param.name] = {
              type: param.type,
              description: param.description,
              required: param.required
            }
          }
        }
        
        const toolDef = {
          ...this.newTool,
          parameters: parametersObj
        }

        await addDynamicTool(toolDef)
        this.message = `工具 '${this.newTool.name}' 添加成功`
        this.status = 'success'
        this.resetForm()
        this.fetchTools()
      } catch (error) {
        const detail = error.response?.data?.detail || error.message
        this.message = '添加失败: ' + detail
        this.status = 'error'
      } finally {
        this.adding = false
      }
    },
    
    confirmDelete(toolName) {
      this.toolToDelete = toolName
      this.showConfirmModal = true
    },
    
    async executeDelete() {
      this.showConfirmModal = false
      try {
        await deleteDynamicTool(this.toolToDelete)
        this.message = `工具 '${this.toolToDelete}' 已删除`
        this.status = 'success'
        this.fetchTools()
      } catch (error) {
        const detail = error.response?.data?.detail || error.message
        this.message = '删除失败: ' + detail
        this.status = 'error'
      }
    },
    
    resetForm() {
      this.newTool = {
        name: '',
        description: '',
        api_config: {
          endpoint: '',
          method: 'POST',
          timeout: 10.0,
          headers: null
        }
      }
      this.parameters = []
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
  overflow-x: auto;
}

.item-name {
  font-weight: 500;
  color: var(--text-primary);
}

.endpoint-code {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--info);
  background: var(--info-bg);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  word-break: break-all;
}

.method-badge {
  display: inline-block;
  padding: var(--space-xs) var(--space-sm);
  background: var(--primary-glow);
  color: var(--primary);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
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
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.hint-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

/* Form */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

/* Parameters Section */
.params-section {
  margin-bottom: var(--space-lg);
  padding: var(--space-md);
  background: var(--bg-input);
  border-radius: var(--radius-lg);
}

.params-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.params-header h4 {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--text-primary);
}

.no-params {
  text-align: center;
  padding: var(--space-md);
  color: var(--text-muted);
  font-size: 0.875rem;
}

.params-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.param-item {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
  flex-wrap: wrap;
}

.param-input {
  flex: 1;
  min-width: 120px;
}

.param-select {
  width: 100px;
}

.param-desc {
  flex: 2;
  min-width: 180px;
}

.param-required {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.param-required input {
  margin: 0;
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

  .form-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    flex-direction: column;
  }
  
  .card-actions .btn {
    width: 100%;
  }

  .param-item {
    flex-direction: column;
    align-items: stretch;
  }

  .param-input,
  .param-select,
  .param-desc {
    width: 100%;
    min-width: unset;
  }

  .table-wrapper {
    margin: 0 calc(-1 * var(--space-lg));
    border-radius: 0;
    border-left: none;
    border-right: none;
  }
}
</style>
