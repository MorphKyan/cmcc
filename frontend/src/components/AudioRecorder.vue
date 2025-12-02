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
    </div>
  </div>
</template>

<script>
// 引入配置
import { config } from '../config';

export default {
  name: 'AudioRecorder',
  data() {
    return {
      isRecording: false,
      status: '未开始',
      isSupported: 'mediaDevices' in navigator && 'WebSocket' in window && 'AudioWorklet' in window,
      socket: null,
      audioContext: null,
      audioStream: null,
      actualAudioConfig: null,
      audioContextSampleRate: null,
      // 为每个客户端生成一个唯一的ID
      clientId: `web-client-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      websocketOutput: '',
      audioWorkletNode: null
    };
  },
  methods: {
    async startRecording() {
      if (this.isRecording) return;
      // 定义音频参数约束
      const audioConstraints = {
        audio: {
          sampleRate: 16000,   // 期望的采样率，例如 16kHz（语音识别常用）
          //sampleSize: 16,      // 期望的采样位数，例如 16-bit
          channelCount: 1,     // 期望的声道数，例如单声道
          autoGainControl: true,
          echoCancellation: false, // 开启回声消除，十分影响效果建议关闭
          noiseSuppression: true  // 开启噪声抑制
        }
      };
      try {
        // 1. 获取用户麦克风权限和音频流
        this.audioStream = await navigator.mediaDevices.getUserMedia(audioConstraints);
        this.status = '已获取麦克风权限';

        // 打印实际应用的配置，用于调试
        const audioTrack = this.audioStream.getAudioTracks()[0];
        const settings = audioTrack.getSettings();
        console.log('实际应用的音频配置:', settings);

        // 保存实际配置到组件数据
        this.actualAudioConfig = {
          sampleRate: settings.sampleRate,
          channelCount: settings.channelCount,
          sampleSize: settings.sampleSize || 16 // 如果未提供sampleSize，默认为16
        };

        // 2. 创建 AudioContext
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
          sampleRate: 16000
        });
        this.audioContextSampleRate = this.audioContext.sampleRate;

        // 3. 加载 AudioWorklet
        await this.audioContext.audioWorklet.addModule('/audio-processor.js');

        // 4. 创建 MediaStreamAudioSourceNode
        const source = this.audioContext.createMediaStreamSource(this.audioStream);

        // 5. 创建 AudioWorkletNode
        this.audioWorkletNode = new AudioWorkletNode(this.audioContext, 'audio-processor');

        // 6. 建立 WebSocket 连接
        const wsUrl = config.getWebSocketUrl(this.clientId);
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
          console.log('已连接到 WebSocket:', wsUrl);
          console.log('已发送元数据:', metadata);

          this.status = 'WebSocket 已连接，正在录音...';
          this.isRecording = true;

          // 连接音频节点
          source.connect(this.audioWorkletNode);
          this.audioWorkletNode.connect(this.audioContext.destination);

          // 监听来自 AudioWorklet 的 PCM 数据
          this.audioWorkletNode.port.onmessage = (event) => {
            if (!this.isRecording || this.socket.readyState !== WebSocket.OPEN) {
              return;
            }

            // 发送原始PCM数据
            this.socket.send(event.data);
          };

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
        this.status = '错误：'+error;
      }
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

      // 关闭AudioContext
      if (this.audioContext) {
        this.audioContext.close();
        this.audioContext = null;
      }

      this.audioWorkletNode = null;
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
}
button {
  margin: 5px;
  padding: 10px 15px;
}
.websocket-output {
  margin-top: 20px;
  text-align: left;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
.websocket-output pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>