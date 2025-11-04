<template>
  <div class="audio-recorder">
    <h2>网页麦克风输入</h2>
    <div v-if="isSupported">
      <button @click="startRecording" :disabled="isRecording">开始录音</button>
      <button @click="stopRecording" :disabled="!isRecording">停止录音</button>
      <p>状态: {{ status }}</p>
      <div v-if="actualAudioConfig" class="audio-config">
        <h3>实际音频配置:</h3>
        <ul>
          <li>采样率: {{ actualAudioConfig.sampleRate }} Hz</li>
          <li>声道数: {{ actualAudioConfig.channelCount }}</li>
          <li>采样位数: {{ actualAudioConfig.sampleSize }} bit</li>
          <li>音频上下文采样率: {{ audioContextSampleRate }} Hz</li>
        </ul>
      </div>
      <div v-if="websocketOutput" class="websocket-output">
        <h3>处理结果:</h3>
        <pre>{{ websocketOutput }}</pre>
      </div>
    </div>
    <div v-else>
      <p>抱歉，您的浏览器不支持所需功能。</p>
      <p>请确保使用现代浏览器并允许麦克风访问。</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AudioRecorder',
  data() {
    return {
      isRecording: false,
      status: '未开始',
      isSupported: 'mediaDevices' in navigator && 'WebSocket' in window,
      socket: null,
      audioContext: null,
      audioStream: null,
      actualAudioConfig: null,
      audioContextSampleRate: null,
      // 为每个客户端生成一个唯一的ID
      clientId: `web-client-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      websocketOutput: '',
      audioWorkletNode: null,
      scriptProcessorNode: null,
      usesAudioWorklet: false
    };
  },
  methods: {
    async startRecording() {
      if (this.isRecording) return;
      
      try {
        // 先尝试获取麦克风权限，使用更宽松的约束
        const audioConstraints = {
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        };
        
        // 1. 获取用户麦克风权限和音频流
        this.audioStream = await navigator.mediaDevices.getUserMedia(audioConstraints);
        this.status = '已获取麦克风权限';

        // 打印实际应用的配置，用于调试
        const audioTrack = this.audioStream.getAudioTracks()[0];
        const settings = audioTrack.getSettings();
        console.log('实际应用的音频配置:', settings);
        
        // 保存实际配置到组件数据
        this.actualAudioConfig = {
          sampleRate: settings.sampleRate || 16000,
          channelCount: settings.channelCount || 1,
          sampleSize: settings.sampleSize || 16
        };

        // 2. 创建 AudioContext
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) {
          throw new Error('AudioContext not supported');
        }
        
        this.audioContext = new AudioContext();
        this.audioContextSampleRate = this.audioContext.sampleRate;
        
        // 3. 创建 MediaStreamAudioSourceNode
        const source = this.audioContext.createMediaStreamSource(this.audioStream);
        
        // 4. 建立 WebSocket 连接 - 使用相对URL支持局域网访问
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/audio/ws/${this.clientId}`;
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = async () => {
          // 发送元数据 - 使用实际获取的音频配置
          const metadata = {
            type: 'config',
            format: 'pcm',
            sampleRate: this.actualAudioConfig.sampleRate,
            sampleSize: this.actualAudioConfig.sampleSize,
            channelCount: this.actualAudioConfig.channelCount
          };
          this.socket.send(JSON.stringify(metadata));
          console.log('已发送元数据:', metadata);

          this.status = 'WebSocket 已连接，正在录音...';
          this.isRecording = true;
          
          // 5. 设置音频处理节点（优先使用 AudioWorklet，降级到 ScriptProcessorNode）
          await this.setupAudioProcessing(source);
          
          // 开始音频上下文
          if (this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
          }
        };

        // 接收后端通过WebSocket发送的处理结果
        this.socket.onmessage = (event) => {
          try {
            // 尝试解析JSON数据
            const data = JSON.parse(event.data);
            this.websocketOutput = JSON.stringify(data, null, 2);
          } catch (e) {
            // 如果不是JSON，则直接显示文本
            this.websocketOutput = event.data;
          }
        };

        this.socket.onclose = () => {
          this.status = 'WebSocket 连接已关闭';
          this.cleanup();
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket Error:', error);
          this.status = 'WebSocket 连接出错';
          this.cleanup();
        };

      } catch (error) {
        console.error('无法获取麦克风:', error);
        this.status = '错误：' + (error.message || error);
      }
    },

    async setupAudioProcessing(source) {
      // 尝试使用 AudioWorklet（现代浏览器）
      if ('AudioWorklet' in window) {
        try {
          await this.audioContext.audioWorklet.addModule('/audio-processor.js');
          this.audioWorkletNode = new AudioWorkletNode(this.audioContext, 'audio-processor');
          source.connect(this.audioWorkletNode);
          this.audioWorkletNode.connect(this.audioContext.destination);
          
          this.audioWorkletNode.port.onmessage = (event) => {
            if (!this.isRecording || this.socket.readyState !== WebSocket.OPEN) {
              return;
            }
            this.socket.send(event.data);
          };
          
          this.usesAudioWorklet = true;
          console.log('使用 AudioWorklet 处理音频');
          return;
        } catch (workletError) {
          console.warn('AudioWorklet 不可用，降级到 ScriptProcessorNode:', workletError);
        }
      }
      
      // 降级到 ScriptProcessorNode（兼容性更好）
      this.scriptProcessorNode = this.audioContext.createScriptProcessor(4096, 1, 1);
      source.connect(this.scriptProcessorNode);
      this.scriptProcessorNode.connect(this.audioContext.destination);
      
      this.scriptProcessorNode.onaudioprocess = (event) => {
        if (!this.isRecording || this.socket.readyState !== WebSocket.OPEN) {
          return;
        }
        
        const inputBuffer = event.inputBuffer;
        const channelData = inputBuffer.getChannelData(0);
        
        // 将Float32Array转换为Int16Array (16-bit PCM)
        const int16Array = new Int16Array(channelData.length);
        for (let i = 0; i < channelData.length; i++) {
          int16Array[i] = Math.max(-32768, Math.min(32767, Math.floor(channelData[i] * 32768)));
        }
        
        this.socket.send(int16Array.buffer);
      };
      
      this.usesAudioWorklet = false;
      console.log('使用 ScriptProcessorNode 处理音频');
    },

    stopRecording() {
      if (!this.isRecording) return;
      this.status = '正在停止...';
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.close();
      }
      this.cleanup();
    },

    cleanup() {
      // 停止本地音频流轨道，关闭麦克风指示灯
      if (this.audioStream) {
        this.audioStream.getTracks().forEach(track => track.stop());
        this.audioStream = null;
      }
      
      // 断开音频节点连接
      if (this.audioWorkletNode) {
        this.audioWorkletNode.disconnect();
        this.audioWorkletNode = null;
      }
      
      if (this.scriptProcessorNode) {
        this.scriptProcessorNode.disconnect();
        this.scriptProcessorNode = null;
      }
      
      // 关闭AudioContext
      if (this.audioContext) {
        this.audioContext.close();
        this.audioContext = null;
      }
      
      this.socket = null;
      this.isRecording = false;
      if (this.status !== 'WebSocket 连接已关闭') {
          this.status = '已停止';
      }
    }
  },
  beforeUnmount() {
    // 组件销毁前确保资源被清理
    this.stopRecording();
  }
};
</script>

<style scoped>
.audio-recorder {
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  max-width: 400px;
  margin: 20px auto;
  width: 90%;
  box-sizing: border-box;
}

@media (max-width: 480px) {
  .audio-recorder {
    padding: 15px;
    margin: 10px;
    width: 95%;
  }
  
  h2 {
    font-size: 1.2em;
    margin-bottom: 15px;
  }
  
  .audio-config h3,
  .websocket-output h3 {
    font-size: 1em;
  }
  
  .audio-config ul {
    padding-left: 20px;
    font-size: 0.9em;
  }
}

button {
  margin: 5px;
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  font-size: 16px; /* 防止iOS Safari缩放 */
  width: 100%;
  max-width: 200px;
}

button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.websocket-output {
  margin-top: 20px;
  text-align: left;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

.websocket-output pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
}
</style>