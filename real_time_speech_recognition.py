import pyaudio
import numpy as np
import threading
import queue
import time
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

class RealTimeSpeechRecognizer:
    def __init__(self):
        # 初始化模型
        model_dir = "iic/SenseVoiceSmall"
        self.model = AutoModel(
            model=model_dir,
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            device="cuda:0" if self._check_cuda() else "cpu",
        )
        
        # 音频参数
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024
        self.RECORD_SECONDS = 5  # 每次识别的时长
        
        # 创建音频流队列
        self.audio_queue = queue.Queue()
        
        # 初始化PyAudio
        self.audio = pyaudio.PyAudio()
        
        # 打开音频流
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.audio_callback
        )
        
    def _check_cuda(self):
        """检查CUDA是否可用"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """音频回调函数"""
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def start_recognition(self):
        """开始实时语音识别"""
        print("开始录音，按 Ctrl+C 停止...")
        
        # 开始录音
        self.stream.start_stream()
        
        try:
            while True:
                # 收集音频数据
                frames = []
                for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                    data = self.audio_queue.get()
                    frames.append(data)
                
                # 将音频数据转换为numpy数组
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                
                # 在新线程中进行语音识别，避免阻塞录音
                recognition_thread = threading.Thread(target=self.recognize_audio, args=(audio_data,))
                recognition_thread.start()
                
        except KeyboardInterrupt:
            print("\n录音已停止")
        
        # 停止并关闭音频流
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
    
    def recognize_audio(self, audio_data):
        """识别音频数据"""
        try:
            # 将音频数据转换为float32格式
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            
            # 进行语音识别
            res = self.model.generate(
                input=audio_data,
                cache={},
                language="auto",
                use_itn=True,
                batch_size_s=60,
                merge_vad=True,
                merge_length_s=15,
            )
            
            # 处理结果
            if res and len(res) > 0:
                text = rich_transcription_postprocess(res[0]["text"])
                if text.strip():  # 只输出非空结果
                    print(f"识别结果: {text}")
        except Exception as e:
            print(f"识别出错: {e}")

# 主程序
if __name__ == "__main__":
    recognizer = RealTimeSpeechRecognizer()
    recognizer.start_recognition()
