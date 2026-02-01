# H5 AI 语音助手组件使用说明

这是一个纯 JavaScript 编写的语音助手组件，可无缝集成到任何 HTML5 页面中。

## 核心特性
- **零依赖**：无需 Vue/React，纯原生 JS。
- **即插即用**：引入 JS 即可使用，自动处理音频流与 WebSocket。
- **智能交互**：支持长按说话 (PTT) 和双击拖动。
- **自动重连**：断线自动重连，确保连接稳定。
- **响应式布局**：自动适配窗口大小变化，防止组件移出屏幕可视区域。

## 快速集成

### 1. 引入文件
将 [ai-assistant-embed.js](frontend/src/embed/ai-assistant-embed.js) 放入你的项目中，并在 HTML 中引入：

```html
<script type="module">
  import { AIAssistant } from './path/to/ai-assistant-embed.js';

  // 初始化组件
  AIAssistant.init({
    // 后端 WebSocket 地址 (必填)
    backendUrl: 'ws://your-server-ip:8000/audio/ws',
    
    // 初始位置 (可选)
    position: { bottom: '30px', right: '30px' },
    
    // 主题: 'light' 或 'dark' (可选，默认 dark)
    theme: 'dark'
  });
</script>
```

### 2. 配置选项 (`config`)

| 参数名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `backendUrl` | String | (必填) | 后端 WebSocket 服务地址，例如 `ws://localhost:8000/audio/ws` |
| `position` | Object | `{ bottom: '20px', right: '20px' }` | 初始定位，支持 `top`, `bottom`, `left`, `right` |
| `theme` | String | `'dark'` | 界面主题，可选 `dark` (深色) 或 `light` (浅色) |
| `containerId` | String | `'ai-assistant-container'` | 组件容器的 DOM ID |

## 交互说明

- **长按说话 (Push-to-Talk)**
    - **操作**：按住悬浮图标超过 0.5 秒。
    - **反馈**：图标变红并带有脉冲动画，表示正在录音。
    - **发送**：松开手指/鼠标，停止录音并发送。（**注**：松开后会自动发送1秒静音包以确保 VAD 尾部检测，此时再次按下可立即恢复录音）
- **双击拖动**
    - **操作**：快速双击图标，且在第二次点击时不松手，移动鼠标/手指。
    - **反馈**：图标随光标移动，松手后固定在新位置。
- **结果面板**
    - 显示语音识别 (ASR) 实时结果和 AI 回复。
    - 点击右上角 `×` 可关闭面板。

## API 方法

如果你需要通过代码控制组件：

```javascript
// 销毁组件 (清理 DOM 和连接)
AIAssistant.destroy();

// 重新初始化
AIAssistant.init({ ... });
```
