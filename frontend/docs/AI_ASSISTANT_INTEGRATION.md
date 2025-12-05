# AI Assistant Widget 集成指南

## 概述

AI Assistant Widget 是一个可嵌入任何H5页面的智能语音助手组件，支持语音录制、实时通信和LLM结果反馈。

---

## 快速开始

### 1. 获取构建文件

```bash
cd frontend
npm install
npm run build:widget
```

构建完成后，`dist-widget/` 目录包含：
- `ai-assistant.umd.js` - UMD格式（推荐）
- `ai-assistant.es.js` - ES Module格式
- `vue-project.css` - 样式文件

### 2. 部署到CDN

将 `dist-widget/` 目录中的文件上传到您的CDN或静态服务器。

---

## 嵌入方式

### 方式一：UMD模块（推荐）

适用于传统HTML页面，无需构建工具。

```html
<!DOCTYPE html>
<html>
<head>
  <!-- 引入样式 -->
  <link rel="stylesheet" href="https://your-cdn.com/vue-project.css">
</head>
<body>
  <!-- 您的页面内容 -->
  <h1>我的页面</h1>
  
  <!-- 在页面底部引入Widget -->
  <script src="https://your-cdn.com/ai-assistant.umd.js"></script>
  <script>
    // 初始化AI助手
    AIAssistant.init({
      backendUrl: 'https://your-backend.com',
      position: { bottom: '20px', right: '20px' },
      theme: 'dark'
    });
  </script>
</body>
</html>
```

### 方式二：ES Module

适用于使用模块化构建的现代Web应用。

```html
<script type="module">
  import { AIAssistant } from 'https://your-cdn.com/ai-assistant.es.js';
  
  AIAssistant.init({
    backendUrl: 'https://your-backend.com'
  });
</script>
```

### 方式三：在Vue/React项目中使用

```javascript
// 直接引入组件
import AIAssistantWidget from '@/components/AIAssistantWidget.vue';

// 在模板中使用
<AIAssistantWidget 
  backend-url="https://your-backend.com"
  theme="dark"
  :initial-position="{ bottom: '20px', right: '20px' }"
/>
```

---

## 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `backendUrl` | String | `''` | 后端WebSocket地址（必填） |
| `position` | Object | `{ bottom: '20px', right: '20px' }` | 初始位置 |
| `theme` | String | `'dark'` | 主题：`'light'` 或 `'dark'` |
| `containerId` | String | `'ai-assistant-container'` | 容器DOM ID |

---

## API方法

### `AIAssistant.init(config)`
初始化并显示组件。

```javascript
AIAssistant.init({
  backendUrl: 'https://api.example.com',
  theme: 'dark'
});
```

### `AIAssistant.destroy()`
销毁组件并清理资源。

```javascript
AIAssistant.destroy();
```

---

## 后端要求

Widget需要连接到WebSocket端点：

```
ws(s)://your-backend.com/audio/ws/{user_id}
```

### 通信协议

1. **建立连接后发送配置**：
```json
{
  "type": "config",
  "format": "pcm",
  "sampleRate": 16000,
  "sampleSize": 16,
  "channelCount": 1
}
```

2. **发送音频数据**：二进制PCM数据（Int16 ArrayBuffer）

3. **接收LLM响应**：JSON格式
```json
{
  "text": "LLM响应内容",
  "type": "response"
}
```

---

## CORS配置

如果Widget部署在不同域，需在后端配置CORS：

```python
# FastAPI示例
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 常见问题

### Q: 麦克风权限被拒绝
A: 确保页面使用HTTPS协议，浏览器只允许安全上下文访问麦克风。

### Q: WebSocket连接失败
A: 检查后端地址和CORS配置，确保WebSocket端点可访问。

### Q: 用户ID如何获取
A: Widget自动生成并存储于`localStorage`，键名为`ai-assistant-user-id`。
