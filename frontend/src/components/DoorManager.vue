<template>
  <div class="manager-section">
    <h2>门资源管理</h2>
    
    <!-- List Doors -->
    <div class="list-box">
      <h3>现有门资源</h3>
      <div v-if="loadingList" class="loading">加载中...</div>
      <div v-else-if="doors.length === 0" class="no-data">暂无数据</div>
      <table v-else class="data-table">
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
            <td>{{ door.name }}</td>
            <td>{{ door.type }}</td>
            <td>{{ door.area1 }}</td>
            <td>{{ door.area2 }}</td>
            <td>{{ door.location }}</td>
          </tr>
        </tbody>
      </table>
      <button @click="fetchDoors" class="refresh-btn">刷新列表</button>
      <button @click="clearAllDoors" class="delete-btn">清空所有数据</button>
    </div>

    <!-- Upload Doors -->
    <div class="upload-box">
      <h3>批量上传门资源 (JSON)</h3>
      <p class="hint">格式示例: [{"name": "门1", "type": "normal", "area1": "区域A", "area2": "区域B", "location": "位置描述"}]</p>
      <textarea v-model="jsonInput" placeholder="在此输入JSON数据..." rows="10"></textarea>
      <div class="actions">
        <button @click="upload" :disabled="uploading">{{ uploading ? '上传中...' : '上传' }}</button>
        <button @click="formatJson" class="secondary">格式化JSON</button>
      </div>
      <p v-if="message" :class="['message', status]">{{ message }}</p>
    </div>
  </div>
</template>

<script>
import { uploadDoorsBatch, getDoors, clearDoors } from '../api'

export default {
  name: 'DoorManager',
  data() {
    return {
      doors: [],
      loadingList: false,
      jsonInput: '',
      message: '',
      status: '',
      uploading: false
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
        this.jsonInput = '' // 清空输入
        this.fetchDoors() // 刷新列表
      } catch (error) {
        this.message = error.message || '上传失败'
        this.status = 'error'
      } finally {
        this.uploading = false
      }
    },
    async clearAllDoors() {
      if (!confirm('确定要清空所有门资源数据吗？此操作不可恢复！')) {
        return
      }
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

.list-box {
  margin-bottom: 30px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.data-table th, .data-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.data-table th {
  background-color: #f2f2f2;
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

button.delete-btn {
  background-color: #d32f2f;
}

button.delete-btn:hover {
  background-color: #b71c1c;
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
