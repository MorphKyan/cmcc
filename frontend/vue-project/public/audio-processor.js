class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.port.onmessage = (event) => {
      // 可以接收来自主线程的消息（如果需要）
    };
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const output = outputs[0];
    
    // 如果有输入音频数据
    if (input.length > 0 && input[0].length > 0) {
      const channelData = input[0]; // 获取第一个声道的数据
      
      // 将Float32Array转换为Int16Array (16-bit PCM)
      const int16Array = new Int16Array(channelData.length);
      for (let i = 0; i < channelData.length; i++) {
        // 将-1.0到1.0的浮点数转换为-32768到32767的整数
        int16Array[i] = Math.max(-32768, Math.min(32767, Math.round(channelData[i] * 32767)));
      }
      
      // 通过port发送PCM数据到主线程
      this.port.postMessage(int16Array.buffer, [int16Array.buffer]);
    }
    
    // 将输入直接复制到输出（用于监听）
    for (let channel = 0; channel < output.length; channel++) {
      if (input[channel]) {
        output[channel].set(input[channel]);
      }
    }
    
    return true; // 继续处理
  }
}

registerProcessor('audio-processor', AudioProcessor);