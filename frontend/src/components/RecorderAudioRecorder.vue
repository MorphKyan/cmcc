<template>
  <div class="recorder-audio-recorder">
    <h2>Recorder库麦克风输入</h2>
      <button @click="startRecording" :disabled="isRecording">开始录音</button>
      <button @click="stopRecording" :disabled="!isRecording">停止录音</button>
      <p>状态: {{ status }}</p>
      <div v-if="actualAudioConfig" class="audio-config">
        <h3>实际音频配置:</h3>
        <ul>
          <li>采样率: {{ actualAudioConfig.sampleRate }} Hz</li>
          <li>声道数: {{ actualAudioConfig.channelCount }}</li>
          <li>采样位数: {{ actualAudioConfig.sampleSize }} bit</li>
        </ul>
      </div>
      <div v-if="websocketOutput" class="websocket-output">
        <h3>处理结果:</h3>
        <pre>{{ websocketOutput }}</pre>
      </div>
    <div v-else>
      <p>抱歉，您的浏览器不支持所需功能。</p>
    </div>
  </div>
</template>

<script>
// 引入Recorder库
import Recorder from 'recorder-core';
import 'recorder-core/src/engine/pcm';
// 引入配置
import { config } from '../config';

export default {
  name: 'RecorderAudioRecorder',
  data() {
    return {
      isRecording: false,
      status: '未开始',
      socket: null,
      recorder: null,
      actualAudioConfig: null,
      // 为每个客户端生成一个唯一的ID
      clientId: `recorder-client-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      websocketOutput: '',
      // 内存清理相关
      clearBufferIdx: 0,
      processTime: 0,
      // 发送相关变量
      send_pcmBuffer: new Int16Array(0),
      send_pcmSampleRate: 16000,
      send_chunk: null,
      send_lastFrame: null
    };
  },
  methods: {
    async startRecording() {
      if (this.isRecording) return;
      
      try {
        // Validate Recorder library is available
        if (typeof Recorder === 'undefined' || Recorder === null) {
          throw new Error('Recorder library is not properly loaded');
        }

        // 1. 创建Recorder实例
        this.recorder = Recorder({
          type: "unknown", // 使用unknown格式以便清理内存
          sampleRate: 16000, // 目标采样率
          bitRate: 16, // 目标位深度
          onProcess: (buffers, powerLevel, bufferDuration, bufferSampleRate, newBufferIdx, asyncEnd) => {
            this.processTime = Date.now();

            // 实时释放清理内存，用于支持长时间录音
            for (let i = this.clearBufferIdx; i < newBufferIdx; i++) {
              buffers[i] = null;
            }
            this.clearBufferIdx = newBufferIdx;

            // 【关键代码】推入实时处理
            this.realTimeSendTry(buffers, bufferSampleRate, false);
          }
        });

        // Validate recorder instance was created successfully
        if (!this.recorder || typeof this.recorder.open !== 'function') {
          throw new Error('Failed to initialize Recorder instance');
        }

        // 2. 打开麦克风授权
        this.recorder.open(() => {
          // 获取实际的音频配置
          const audioTrack = this.recorder.srcStream.getAudioTracks()[0];
          const settings = audioTrack.getSettings();
          // Use fixed sample size of 16 bits since that's what we process
          // Browser-reported sampleSize may not be reliable
          this.actualAudioConfig = {
            sampleRate: settings.sampleRate,
            channelCount: settings.channelCount,
            sampleSize: 16
          };

          // 3. 建立WebSocket连接
          const wsUrl = config.getWebSocketUrl(this.clientId);
          this.socket = new WebSocket(wsUrl);

          this.socket.onopen = () => {
            // 发送元数据
            const metadata = {
              type: 'config',
              format: 'pcm',
              sampleRate: this.actualAudioConfig.sampleRate,
              sampleSize: 16, // Always send 16-bit as that's what we process
              channelCount: this.actualAudioConfig.channelCount
            };
            this.socket.send(JSON.stringify(metadata));
            console.log('已连接到 WebSocket:', wsUrl);
            console.log('已发送元数据:', metadata);

            // 开始录音
            this.recorder.start();
            this.status = 'WebSocket已连接，正在录音...';
            this.isRecording = true;

            // 【稳如老狗WDT】监控录音是否正常
            const startTime = Date.now();
            const wdt = setInterval(() => {
              if (!this.recorder || this.recorder.watchDogTimer !== wdt) {
                clearInterval(wdt);
                return;
              }
              if (Date.now() < (this.recorder.wdtPauseT || 0)) return;
              if (Date.now() - (this.processTime || startTime) > 1500) {
                clearInterval(wdt);
                console.error(this.processTime ? "录音被中断" : "录音未能正常开始");
                this.status = this.processTime ? "录音被中断" : "录音未能正常开始";
                this.stopRecording();
              }
            }, 1000);
            this.recorder.watchDogTimer = wdt;
            this.recorder.wdtPauseT = 0;
          };

          // 接收后端处理结果
          this.socket.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data);
              this.websocketOutput = JSON.stringify(data, null, 2);
            } catch (e) {
              this.websocketOutput = event.data;
            }
          };

          this.socket.onclose = () => {
            this.status = 'WebSocket连接已关闭';
            this.cleanup();
          };

          this.socket.onerror = (error) => {
            console.error('WebSocket Error:', error);
            this.status = 'WebSocket连接出错';
            this.cleanup();
          };

        }, (msg, isUserNotAllow) => {
          console.error((isUserNotAllow ? "UserNotAllow，" : "") + "无法录音:" + msg);
          this.status = '错误：' + msg;
        });

      } catch (error) {
        console.error('无法初始化录音:', error);
        this.status = '错误：' + (error.message || '未知错误');
        // Ensure cleanup is called even if initialization fails
        this.cleanup();
      }
    },

    // =====实时处理核心函数==========
    realTimeSendTry(buffers, bufferSampleRate, isClose) {
      // 提取出新的pcm数据
      let pcm = new Int16Array(0);
      if (buffers.length > 0) {
        // 【关键代码】借用SampleData函数进行数据的连续处理，采样率转换是顺带的，得到新的pcm数据
        const chunk = Recorder.SampleData(buffers, bufferSampleRate, 16000, this.send_chunk);
        this.send_chunk = chunk;
        
        pcm = chunk.data; // 此时的pcm就是原始的音频16位pcm数据（小端LE）
        this.send_pcmSampleRate = chunk.sampleRate;
      }

      // 非固定帧模式：直接把pcm发送出去即可
      this.transferUpload(pcm, isClose);
    },

    // =====数据传输函数==========
    transferUpload(pcmFrame, isClose) {
      if (isClose && pcmFrame.length === 0) {
        // 最后一帧数据，生成一帧静默的pcm（全0）
        const len = this.send_lastFrame ? this.send_lastFrame.length : Math.round(this.send_pcmSampleRate / 1000 * 50);
        pcmFrame = new Int16Array(len);
      }
      this.send_lastFrame = pcmFrame;

      // 直接ArrayBuffer二进制发送
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(pcmFrame.buffer);
      }

      // 最后一次调用发送
      if (isClose) {
        console.log("已停止传输");
      }
    },

    stopRecording() {
      if (!this.isRecording) return;
      this.status = '正在停止...';
      
      if (this.recorder) {
        this.recorder.watchDogTimer = 0; // 停止监控
        this.recorder.close(); // 直接close掉，不需要获得最终音频文件
      }
      
      // 最后一次发送
      this.realTimeSendTry([], 0, true);
      
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.close();
      }
      this.cleanup();
    },

    cleanup() {
      // 清理Recorder实例
      if (this.recorder) {
        this.recorder = null;
      }

      // 清理WebSocket
      this.socket = null;
      this.isRecording = false;
      
      // 重置发送相关变量
      this.send_pcmBuffer = new Int16Array(0);
      this.send_pcmSampleRate = 16000;
      this.send_chunk = null;
      this.send_lastFrame = null;
      
      if (this.status !== 'WebSocket连接已关闭') {
        this.status = '已停止';
      }
    }
  },
  beforeUnmount() {
    this.stopRecording();
  }
};
</script>

<style scoped>
.recorder-audio-recorder {
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