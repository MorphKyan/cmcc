#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时语音转文字程序
使用FunASR库和SenseVoiceSmall模型进行实时语音识别
支持中英文等多种语言的实时识别
"""

import pyaudio
import numpy as np
import threading
import queue
import os
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

# 导入火山引擎SDK
from volcenginesdkarkruntime import Ark

system_prompt="""
# 角色与任务
你是一个中国移动智慧展厅的中央控制AI助手。你的核心任务是将用户的自然语言语音指令，精确地转换为结构化的JSON指令，以便后续程序执行。你必须严格遵循以下知识库和行为准则。

# 知识库 (Knowledge Base)
你唯一可操作的设备和内容如下：
{
  "screens": [
    {"name": "主屏幕", "aliases": ["中间的屏幕", "大屏幕"]},
    {"name": "左侧互动大屏", "aliases": ["左边的屏幕", "左边那个屏"]},
    {"name": "右侧演示屏", "aliases": ["右边的屏幕", "右边那个屏"]}
  ],
  "doors": [
    {"name": "5G先锋体验区的门", "aliases": ["5G体验区", "5G区"]},
    {"name": "智慧生活畅想馆的门", "aliases": ["智慧生活馆", "智能家居区"]},
    {"name": "未来科技赋能中心的门", "aliases": ["未来科技中心", "企业方案区"]},
    {"name": "数字服务互动站的门", "aliases": ["数字服务站", "互动站"]}
  ],
  "videos": [
    {"filename": "5G_Revolution.mp4", "description": "中国移动5G技术的核心优势、网络覆盖及未来发展愿景"},
    {"filename": "Smart_Home_Solution.mp4", "description": "智慧家庭全套解决方案，包括智能安防、智能家电控制"},
    {"filename": "IoT_Applications.mp4", "description": "案例分析：智慧城市、工业互联网、智慧农业等领域的物联网应用"},
    {"filename": "CMCC_Culture.mp4", "description": "中国移动的企业文化、社会责任以及员工风采"},
    {"filename": "Rural_Digital.mp4", "description": "通过数字化技术助力乡村振兴和数字普惠的实践"},
    {"filename": "Cloud_BigData.mp4", "description": "云计算、大数据方面的技术能力、服务产品及行业赋能"},
    {"filename": "AI_Empower_Life.mp4", "description": "人工智能如何赋能生活，包括AI语音助手、智能客服"},
    {"filename": "Mobile_Payment.mp4", "description": "移动支付技术如何让生活更便捷高效"},
    {"filename": "Smart_City_Vision.mp4", "description": "展望智慧城市的未来图景，以及在智慧交通、环境监测等领域的贡献"},
    {"filename": "Green_Telecom.mp4", "description": "在绿色通信、节能减排和可持续发展方面所做的努力与成果"}
  ]
}

# 行为准则与输出格式
1.  **输出格式**: 你的最终输出必须是一个单独的、不包含任何解释性文字的JSON对象。JSON对象必须包含以下字段: `{"action": "...", "target": "...", "device": "..."}`。
2.  **动作 (action)**: `action`字段的值必须是以下之一: `play`, `open`, `close`。
3.  **目标 (target)**:
    *   如果`action`是`play`，`target`必须是知识库中`videos`列表里对应视频的`filename`。你需要根据用户描述的语义来匹配最相关的视频。
    *   如果`action`是`open`或`close`，`target`必须是知识库中`doors`列表里对应门的全称，即`xxx的门`。
4.  **设备 (device)**:
    *   如果`action`是`play`，`device`必须是知识库中`screens`列表里对应屏幕的`name`。如果用户没有明确指定屏幕，默认使用`主屏幕`。
    *   如果`action`是`open`或`close`，`device`字段的值必须是`null`。
5.  **歧义与错误处理**:
    *   利用`aliases`和`description`来最大程度地理解用户的意图。例如，用户说“放一下关于智慧城市的视频”，你应该匹配到`Smart_City_Vision.mp4`。
    *   如果用户的指令与知识库中的任何内容都无法匹配，或意图完全无关（如询问天气），则必须输出 `{"action": "error", "reason": "intent_unclear"}`。

# 示例
- 用户输入: "我想看看5G的视频" -> 输出: {"action": "play", "target": "5G_Revolution.mp4", "device": "主屏幕"}
- 用户输入: "在左边的屏幕上播放一下智慧家庭的解决方案" -> 输出: {"action": "play", "target": "Smart_Home_Solution.mp4", "device": "左侧互动大屏"}
- 用户输入: "打开未来科技中心的门" -> 输出: {"action": "open", "target": "未来科技赋能中心的门", "device": null}
- 用户输入: "你好，今天星期几？" -> 输出: {"action": "error", "reason": "intent_unclear"}

# 用户当前指令:
{{USER_INPUT}}
"""

ARK_API_KEY="aabd9362-9ca8-43ac-bb4d-828f0ba98f4d"

class RealTimeSpeechRecognizer:
    def __init__(self, device="auto"):
        """
        初始化实时语音识别器
        
        Args:
            device (str): 设备类型，"cuda:0"表示使用GPU，"cpu"表示使用CPU，"auto"表示自动检测
        """
        # 初始化模型
        model_dir = "iic/SenseVoiceSmall"
        
        # 根据设备选择使用GPU还是CPU
        if device == "auto":
            device = "cuda:0" if self._check_cuda() else "cpu"
        
        print(f"正在使用 {device} 进行推理...")
        
        self.model = AutoModel(
            model=model_dir,
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            device=device,
        )
        
        # 初始化火山引擎客户端
        self.client = Ark(
            # 此为默认路径，您可根据业务所在地域进行配置
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
            api_key=ARK_API_KEY,
        )

        # 初始化对话历史
        self.conversation_history = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # 音频参数
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # 采样率
        self.CHUNK = 1024  # 每个音频块的大小
        self.RECORD_SECONDS = 5  # 每次识别的时长（秒）
        
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
        print("=" * 50)
        print("实时语音转文字程序")
        print("=" * 50)
        print("正在加载模型，请稍候...")
        print("开始录音，按 Ctrl+C 停止...")
        print("-" * 50)
        
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
            print("\n" + "-" * 50)
            print("录音已停止")
            print("感谢使用实时语音转文字程序！")
        
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
                language="auto",  # 自动检测语言
                use_itn=True,     # 使用逆文本归一化
                batch_size_s=60,
                merge_vad=True,
                merge_length_s=15,
            )
            
            # 处理结果
            if res and len(res) > 0:
                text = rich_transcription_postprocess(res[0]["text"])
                if text.strip():  # 只输出非空结果
                    print(f"[识别结果] {text}")
                    
                    # 将当前用户输入添加到对话历史
                    self.conversation_history.append({
                        "role": "user",
                        "content": text
                    })
                    
                    # 调用火山引擎大模型API
                    try:
                        response = self.client.chat.completions.create(
                            model="doubao-seed-1-6-flash-250715",  # 指定模型
                            messages=self.conversation_history # 发送完整对话历史
                        )
                        
                        # 获取并输出大模型的响应
                        assistant_message = response.choices.message.content
                        print(f"[大模型响应] {assistant_message}")
                        
                        # 将大模型的响应也添加到对话历史中
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": assistant_message
                        })
                    except Exception as api_error:
                        print(f"[错误] 调用大模型API出错: {api_error}")
                        # 如果API调用失败，移除刚刚添加的用户输入，以便下次重试
                        self.conversation_history.pop()
        except Exception as e:
            print(f"[错误] 识别出错: {e}")

def main():
    """主函数"""
    # 创建识别器实例（默认自动选择设备）
    recognizer = RealTimeSpeechRecognizer(device="auto")
    
    # 开始识别
    recognizer.start_recognition()

if __name__ == "__main__":
    main()
