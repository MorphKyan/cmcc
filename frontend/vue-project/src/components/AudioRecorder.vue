<template>
  <div class="audio-recorder">
    <h2>网页麦克风输入</h2>
    <div v-if="isSupported">
      <button @click="startRecording" :disabled="isRecording">开始录音</button>
      <button @click="stopRecording" :disabled="!isRecording">停止录音</button>
      <p>状态: {{ status }}</p>
    </div>
    <div v-else>
      <p>抱歉，您的浏览器不支持所需功能。</p>
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
      mediaRecorder: null,
      audioStream: null,
      // 为每个客户端生成一个唯一的ID
      clientId: `web-client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    };
  },
  methods: {
    async startRecording() {
      if (this.isRecording) return;

      try {
        // 1. 获取用户麦克风权限和音频流
        this.audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.status = '已获取麦克风权限';

        // 2. 建立 WebSocket 连接
        const wsUrl = `ws://localhost:5000/api/audio/ws/${this.clientId}`; // 确保主机和端口正确
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
          this.status = 'WebSocket 已连接，正在录音...';
          this.isRecording = true;
          
          // 3. 创建 MediaRecorder 实例
          this.mediaRecorder = new MediaRecorder(this.audioStream);

          // 4. 设置 ondataavailable 回调，当有音频数据时触发
          this.mediaRecorder.ondataavailable = (event) => {
            // 确保有数据并且WebSocket处于连接状态
            if (event.data.size > 0 && this.socket.readyState === WebSocket.OPEN) {
              // 5. 通过 WebSocket 发送音频数据块
              this.socket.send(event.data);
            }
          };

          // 6. 启动 MediaRecorder，timeslice 参数表示每 250ms 触发一次 ondataavailable
          this.mediaRecorder.start(250);
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
        this.status = '错误：无法获取麦克风权限';
      }
    },

    stopRecording() {
      if (!this.isRecording) return;
      this.status = '正在停止...';
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.stop();
      }
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
      this.mediaRecorder = null;
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
</style>