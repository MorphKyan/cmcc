#!/usr/bin/env python3
"""
专门测试 run_llm_rag_processor 函数逻辑的测试脚本
该测试独立搭建 run_llm_rag_processor 的完整逻辑，不依赖后台服务
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger

# 导入必要的模块
from src.config.config import get_settings
from src.module.llm.ollama_llm_handler import OllamaLLMHandler
from src.module.rag.ollama_rag_processor import OllamaRAGProcessor
from src.module.llm.smart_retry_handler import SmartRetryHandler


class MockContext:
    """模拟 Context 类，只包含 run_llm_rag_processor 需要的队列"""
    def __init__(self):
        self.asr_output_queue = asyncio.Queue()
        self.function_calling_queue = asyncio.Queue()


class MockWebSocket:
    """模拟 WebSocket 连接"""
    def __init__(self):
        self.sent_messages = []

    async def send_text(self, message: str):
        """模拟发送文本消息"""
        self.sent_messages.append(message)
        logger.info(f"WebSocket 发送消息: {message}")


class RunLLMRAGProcessorTester:
    """专门测试 run_llm_rag_processor 逻辑的测试器"""

    def __init__(self):
        self.settings = get_settings()
        self.test_results = []
        self.failed_cases = []

        # 初始化处理器
        self._initialize_processors()

    def _initialize_processors(self):
        """初始化 LLM 和 RAG 处理器"""
        logger.info("初始化处理器...")

        # 初始化 RAG 处理器 - 使用 Ollama
        self.rag_processor = OllamaRAGProcessor(self.settings.rag)

        # 初始化 LLM 处理器 - 使用 Ollama
        self.llm_processor = OllamaLLMHandler(self.settings.llm)

        logger.info("处理器初始化完成")

    async def initialize_async(self):
        """异步初始化处理器"""
        await self.rag_processor.initialize()
        await self.llm_processor.initialize()
        logger.info("异步初始化完成")

    def create_test_cases(self) -> List[Dict[str, Any]]:
        """创建100条测试样例"""
        test_cases = []

        # 视频播放指令 (40条)
        video_instructions = [
            {"instruction": "我想看看5G技术的总览介绍", "rag_document": "5G_Overview_Intro.mp4", "expected_tools": [{"action": "play", "target": "5G_Overview_Intro.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下智慧家庭解决方案的视频", "rag_document": "Smart_Home_Solutions.mp4", "expected_tools": [{"action": "play", "target": "Smart_Home_Solutions.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "在左边互动屏看看云计算和大数据的能力", "rag_document": "Cloud_BigData_Capabilities.mp4", "expected_tools": [{"action": "play", "target": "Cloud_BigData_Capabilities.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "我想了解一下人工智能应用的最新进展", "rag_document": "AI_Applications_Frontier.mp4", "expected_tools": [{"action": "play", "target": "AI_Applications_Frontier.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "看看移动支付和数字人民币是怎么工作的", "rag_document": "Mobile_Payment_eCNY.mp4", "expected_tools": [{"action": "play", "target": "Mobile_Payment_eCNY.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想看看智慧城市的未来愿景", "rag_document": "Smart_City_Future_Vision.mp4", "expected_tools": [{"action": "play", "target": "Smart_City_Future_Vision.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下绿色通信和可持续发展的介绍", "rag_document": "Green_Communications_Sustainability.mp4", "expected_tools": [{"action": "play", "target": "Green_Communications_Sustainability.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解5G-Advanced的技术解析", "rag_document": "5G_Advanced_Tech_Analysis.mp4", "expected_tools": [{"action": "play", "target": "5G_Advanced_Tech_Analysis.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "看看5G网络切片技术的介绍", "rag_document": "5G_Network_Slicing.mp4", "expected_tools": [{"action": "play", "target": "5G_Network_Slicing.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解一下5G毫米波技术的奥秘", "rag_document": "5G_mmWave_Exploration.mp4", "expected_tools": [{"action": "play", "target": "5G_mmWave_Exploration.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下算力网络的介绍视频", "rag_document": "Computing_First_Network.mp4", "expected_tools": [{"action": "play", "target": "Computing_First_Network.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想看看数据中心基础设施的内容", "rag_document": "Data_Center_Infrastructure.mp4", "expected_tools": [{"action": "play", "target": "Data_Center_Infrastructure.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下家庭安防解决方案的视频", "rag_document": "Home_Security_Solution.mp4", "expected_tools": [{"action": "play", "target": "Home_Security_Solution.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解全屋Wi-Fi覆盖的方案", "rag_document": "Whole_Home_WiFi.mp4", "expected_tools": [{"action": "play", "target": "Whole_Home_WiFi.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想看看智慧社区管理平台的内容", "rag_document": "Smart_Community_Platform.mp4", "expected_tools": [{"action": "play", "target": "Smart_Community_Platform.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下工业互联网平台的介绍", "rag_document": "Industrial_Internet_Platform.mp4", "expected_tools": [{"action": "play", "target": "Industrial_Internet_Platform.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解一下车联网技术", "rag_document": "Vehicle_to_Everything_V2X.mp4", "expected_tools": [{"action": "play", "target": "Vehicle_to_Everything_V2X.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "看看智慧农业解决方案是怎么实现的", "rag_document": "Smart_Agriculture_Solution.mp4", "expected_tools": [{"action": "play", "target": "Smart_Agriculture_Solution.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想看看智慧医疗影像云的内容", "rag_document": "Smart_Healthcare_Imaging_Cloud.mp4", "expected_tools": [{"action": "play", "target": "Smart_Healthcare_Imaging_Cloud.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下智慧教育互动课堂的视频", "rag_document": "Smart_Education_Classroom.mp4", "expected_tools": [{"action": "play", "target": "Smart_Education_Classroom.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解金融行业的数字化方案", "rag_document": "Digital_Finance_Solutions.mp4", "expected_tools": [{"action": "play", "target": "Digital_Finance_Solutions.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "看看智慧文旅的沉浸式体验", "rag_document": "Smart_Tourism_Experience.mp4", "expected_tools": [{"action": "play", "target": "Smart_Tourism_Experience.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解网络安全防护体系", "rag_document": "Cyber_Security_Defense_System.mp4", "expected_tools": [{"action": "play", "target": "Cyber_Security_Defense_System.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "看看数据隐私保护的承诺是什么", "rag_document": "Data_Privacy_Protection.mp4", "expected_tools": [{"action": "play", "target": "Data_Privacy_Protection.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解云原生安全解决方案", "rag_document": "Cloud_Native_Security.mp4", "expected_tools": [{"action": "play", "target": "Cloud_Native_Security.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下量子通信加密技术的介绍", "rag_document": "Quantum_Communication_Encryption.mp4", "expected_tools": [{"action": "play", "target": "Quantum_Communication_Encryption.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想看看超级SIM卡有什么功能", "rag_document": "Super_SIM_Functionality.mp4", "expected_tools": [{"action": "play", "target": "Super_SIM_Functionality.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下和彩云网盘的介绍", "rag_document": "HeCaiYun_Cloud_Drive.mp4", "expected_tools": [{"action": "play", "target": "HeCaiYun_Cloud_Drive.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解移动高清视频彩铃", "rag_document": "Video_Color_Ring_Tone.mp4", "expected_tools": [{"action": "play", "target": "Video_Color_Ring_Tone.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "看看超高清视频技术是怎么实现的", "rag_document": "Ultra_HD_Video_Technology.mp4", "expected_tools": [{"action": "play", "target": "Ultra_HD_Video_Technology.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想看看AR增强现实应用", "rag_document": "Augmented_Reality_Applications.mp4", "expected_tools": [{"action": "play", "target": "Augmented_Reality_Applications.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下VR虚拟现实体验的视频", "rag_document": "Virtual_Reality_Experience.mp4", "expected_tools": [{"action": "play", "target": "Virtual_Reality_Experience.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解数字人和智能客服", "rag_document": "Digital_Human_Avatar.mp4", "expected_tools": [{"action": "play", "target": "Digital_Human_Avatar.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "看看全球发展和一带一路的内容", "rag_document": "Global_Strategy_BRI.mp4", "expected_tools": [{"action": "play", "target": "Global_Strategy_BRI.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解社会公益与慈善的内容", "rag_document": "Social_Welfare_Charity.mp4", "expected_tools": [{"action": "play", "target": "Social_Welfare_Charity.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下应急通信保障的介绍", "rag_document": "Emergency_Communication_Support.mp4p", "expected_tools": [{"action": "play", "target": "Emergency_Communication_Support.mp4p", "device": "主屏幕", "value": None}]},
            {"instruction": "我想看看全民数字素养提升的内容", "rag_document": "Digital_Literacy_Inclusion.mp4", "expected_tools": [{"action": "play", "target": "Digital_Literacy_Inclusion.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "了解一下科技创新体系", "rag_document": "Tech_Innovation_System.mp4", "expected_tools": [{"action": "play", "target": "Tech_Innovation_System.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想看看人才发展与培养的内容", "rag_document": "Talent_Development_Program.mp4", "expected_tools": [{"action": "play", "target": "Talent_Development_Program.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "放一下供应链可持续性的介绍", "rag_document": "Sustainable_Supply_Chain.mp4", "expected_tools": [{"action": "play", "target": "Sustainable_Supply_Chain.mp4", "device": "主屏幕", "value": None}]},
            {"instruction": "我想了解董事会与公司治理", "rag_document": "Corporate_Governance_Structure.mp4", "expected_tools": [{"action": "play", "target": "Corporate_Governance_Structure.mp4", "device": "主屏幕", "value": None}]},
        ]

        # 非主屏幕视频播放指令 (20条)
        alternative_screen_videos = [
            {"instruction": "左边那个互动屏上放一下5G网络切片的介绍", "rag_document": "5G_Network_Slicing.mp4", "expected_tools": [{"action": "play", "target": "5G_Network_Slicing.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "在左边的屏幕上看看智慧农业是怎么做的", "rag_document": "Smart_Agriculture_Solution.mp4", "expected_tools": [{"action": "play", "target": "Smart_Agriculture_Solution.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "左边互动屏播放工业互联网平台的内容", "rag_document": "Industrial_Internet_Platform.mp4", "expected_tools": [{"action": "play", "target": "Industrial_Internet_Platform.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "我想在左边大屏上看看车联网技术", "rag_document": "Vehicle_to_Everything_V2X.mp4", "expected_tools": [{"action": "play", "target": "Vehicle_to_Everything_V2X.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "左边互动屏放一下智慧医疗影像云的演示", "rag_document": "Smart_Healthcare_Imaging_Cloud.mp4", "expected_tools": [{"action": "play", "target": "Smart_Healthcare_Imaging_Cloud.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "在左边屏幕上看看智慧教育的互动课堂", "rag_document": "Smart_Education_Classroom.mp4", "expected_tools": [{"action": "play", "target": "Smart_Education_Classroom.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "左边互动大屏播放金融数字化方案", "rag_document": "Digital_Finance_Solutions.mp4", "expected_tools": [{"action": "play", "target": "Digital_Finance_Solutions.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "我想看看左边屏上的智慧文旅体验", "rag_document": "Smart_Tourism_Experience.mp4", "expected_tools": [{"action": "play", "target": "Smart_Tourism_Experience.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "左边互动屏放一下网络安全防护的内容", "rag_document": "Cyber_Security_Defense_System.mp4", "expected_tools": [{"action": "play", "target": "Cyber_Security_Defense_System.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "在左边大屏上看看数据隐私保护的介绍", "rag_document": "Data_Privacy_Protection.mp4", "expected_tools": [{"action": "play", "target": "Data_Privacy_Protection.mp4", "device": "左侧互动大屏", "value": None}]},
            {"instruction": "右边演示屏播放量子通信加密技术", "rag_document": "Quantum_Communication_Encryption.mp4", "expected_tools": [{"action": "play", "target": "Quantum_Communication_Encryption.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "我想在右边屏幕上看看超级SIM卡的功能", "rag_document": "Super_SIM_Functionality.mp4", "expected_tools": [{"action": "play", "target": "Super_SIM_Functionality.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "右边演示屏放一下和彩云网盘的介绍", "rag_document": "HeCaiYun_Cloud_Drive.mp4", "expected_tools": [{"action": "play", "target": "HeCaiYun_Cloud_Drive.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "在右边屏上看看移动高清视频彩铃", "rag_document": "Video_Color_Ring_Tone.mp4", "expected_tools": [{"action": "play", "target": "Video_Color_Ring_Tone.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "右边演示屏播放超高清视频技术的内容", "rag_document": "Ultra_HD_Video_Technology.mp4", "expected_tools": [{"action": "play", "target": "Ultra_HD_Video_Technology.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "我想看看右边屏上的AR增强现实应用", "rag_document": "Augmented_Reality_Applications.mp4", "expected_tools": [{"action": "play", "target": "Augmented_Reality_Applications.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "右边演示屏放一下VR虚拟现实体验", "rag_document": "Virtual_Reality_Experience.mp4", "expected_tools": [{"action": "play", "target": "Virtual_Reality_Experience.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "在右边屏幕上看看数字人和智能客服", "rag_document": "Digital_Human_Avatar.mp4", "expected_tools": [{"action": "play", "target": "Digital_Human_Avatar.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "右边演示屏播放一带一路的全球发展内容", "rag_document": "Global_Strategy_BRI.mp4", "expected_tools": [{"action": "play", "target": "Global_Strategy_BRI.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "我想看看右边屏上的社会公益慈善内容", "rag_document": "Social_Welfare_Charity.mp4", "expected_tools": [{"action": "play", "target": "Social_Welfare_Charity.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "右边演示屏放一下应急通信保障的介绍", "rag_document": "Emergency_Communication_Support.mp4p", "expected_tools": [{"action": "play", "target": "Emergency_Communication_Support.mp4p", "device": "右侧演示屏", "value": None}]},
            {"instruction": "在右边大屏上看看全民数字素养提升的内容", "rag_document": "Digital_Literacy_Inclusion.mp4", "expected_tools": [{"action": "play", "target": "Digital_Literacy_Inclusion.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "右边演示屏播放科技创新体系的介绍", "rag_document": "Tech_Innovation_System.mp4", "expected_tools": [{"action": "play", "target": "Tech_Innovation_System.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "我想看看右边屏上的人才发展培养内容", "rag_document": "Talent_Development_Program.mp4", "expected_tools": [{"action": "play", "target": "Talent_Development_Program.mp4", "device": "右侧演示屏", "value": None}]},
            {"instruction": "右边演示屏播放供应链可持续性的内容", "rag_document": "Sustainable_Supply_Chain.mp4", "expected_tools": [{"action": "play", "target": "Sustainable_Supply_Chain.mp4", "device": "右侧演示屏", "value": None}]},
        ]

        # 门控制指令 (20条)
        door_instructions = [
            {"instruction": "把5G先锋体验区的门打开", "rag_document": None, "expected_tools": [{"action": "open", "target": "5G先锋体验区的门", "device": None, "value": None}]},
            {"instruction": "智慧生活馆的门帮我关一下", "rag_document": None, "expected_tools": [{"action": "close", "target": "智慧生活馆的门", "device": None, "value": None}]},
            {"instruction": "我想进未来科技赋能中心，开门", "rag_document": None, "expected_tools": [{"action": "open", "target": "未来科技赋能中心的门", "device": None, "value": None}]},
            {"instruction": "数字应用体验中心的门关上", "rag_document": None, "expected_tools": [{"action": "close", "target": "数字应用体验中心的门", "device": None, "value": None}]},
            {"instruction": "请打开5G先锋体验区的门", "rag_document": None, "expected_tools": [{"action": "open", "target": "5G先锋体验区的门", "device": None, "value": None}]},
            {"instruction": "把智慧生活馆的门关上", "rag_document": None, "expected_tools": [{"action": "close", "target": "智慧生活馆的门", "device": None, "value": None}]},
            {"instruction": "开启未来科技赋能中心的门", "rag_document": None, "expected_tools": [{"action": "open", "target": "未来科技赋能中心的门", "device": None, "value": None}]},
            {"instruction": "把数字应用体验中心的门关闭", "rag_document": None, "expected_tools": [{"action": "close", "target": "数字应用体验中心的门", "device": None, "value": None}]},
            {"instruction": "能打开5G先锋体验区的门吗", "rag_document": None, "expected_tools": [{"action": "open", "target": "5G先锋体验区的门", "device": None, "value": None}]},
            {"instruction": "智慧生活馆的门需要关闭", "rag_document": None, "expected_tools": [{"action": "close", "target": "智慧生活馆的门", "device": None, "value": None}]},
            {"instruction": "开启未来科技赋能中心的门", "rag_document": None, "expected_tools": [{"action": "open", "target": "未来科技赋能中心的门", "device": None, "value": None}]},
            {"instruction": "数字应用体验中心的门请关掉", "rag_document": None, "expected_tools": [{"action": "close", "target": "数字应用体验中心的门", "device": None, "value": None}]},
            {"instruction": "把5G先锋体验区的门打开", "rag_document": None, "expected_tools": [{"action": "open", "target": "5G先锋体验区的门", "device": None, "value": None}]},
            {"instruction": "智慧生活馆的门打开一下", "rag_document": None, "expected_tools": [{"action": "open", "target": "智慧生活馆的门", "device": None, "value": None}]},
            {"instruction": "未来科技赋能中心的门关闭", "rag_document": None, "expected_tools": [{"action": "close", "target": "未来科技赋能中心的门", "device": None, "value": None}]},
            {"instruction": "数字应用体验中心的门打开", "rag_document": None, "expected_tools": [{"action": "open", "target": "数字应用体验中心的门", "device": None, "value": None}]},
            {"instruction": "5G先锋体验区的门打开", "rag_document": None, "expected_tools": [{"action": "open", "target": "5G先锋体验区的门", "device": None, "value": None}]},
            {"instruction": "智慧生活馆的门关上", "rag_document": None, "expected_tools": [{"action": "close", "target": "智慧生活馆的门", "device": None, "value": None}]},
            {"instruction": "未来科技赋能中心的门请打开", "rag_document": None, "expected_tools": [{"action": "open", "target": "未来科技赋能中心的门", "device": None, "value": None}]},
            {"instruction": "数字应用体验中心的门关闭", "rag_document": None, "expected_tools": [{"action": "close", "target": "数字应用体验中心的门", "device": None, "value": None}]},
        ]

        # 音量控制指令 (15条)
        volume_instructions = [
            {"instruction": "音量调到50", "rag_document": None, "expected_tools": [{"action": "set_volume", "target": None, "device": "主屏幕", "value": 50}]},
            {"instruction": "声音大一点", "rag_document": None, "expected_tools": [{"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "up"}]},
            {"instruction": "我想把音量设为80", "rag_document": None, "expected_tools": [{"action": "set_volume", "target": None, "device": "主屏幕", "value": 80}]},
            {"instruction": "声音小一点", "rag_document": None, "expected_tools": [{"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "down"}]},
            {"instruction": "声音调到30", "rag_document": None, "expected_tools": [{"action": "set_volume", "target": None, "device": "主屏幕", "value": 30}]},
            {"instruction": "音量调大一点", "rag_document": None, "expected_tools": [{"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "up"}]},
            {"instruction": "调小音量", "rag_document": None, "expected_tools": [{"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "down"}]},
            {"instruction": "音量设置为60", "rag_document": None, "expected_tools": [{"action": "set_volume", "target": None, "device": "主屏幕", "value": 60}]},
            {"instruction": "声音大一点", "rag_document": None, "expected_tools": [{"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "up"}]},
            {"instruction": "声音小一点", "rag_document": None, "expected_tools": [{"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "down"}]},
            {"instruction": "音量调到90", "rag_document": None, "expected_tools": [{"action": "set_volume", "target": None, "device": "主屏幕", "value": 90}]},
            {"instruction": "提高音量", "rag_document": None, "expected_tools": [{"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "up"}]},
            {"instruction": "降低音量", "rag_document": None, "expected_tools": [{"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "down"}]},
            {"instruction": "设置音量为20", "rag_document": None, "expected_tools": [{"action": "set_volume", "target": None, "device": "主屏幕", "value": 20}]},
            {"instruction": "音量调到100", "rag_document": None, "expected_tools": [{"action": "set_volume", "target": None, "device": "主屏幕", "value": 100}]},
        ]

        # 视频跳转指令 (10条)
        seek_instructions = [
            {"instruction": "我想跳到2分30秒", "rag_document": None, "expected_tools": [{"action": "seek_video", "target": None, "device": "主屏幕", "value": 150}]},
            {"instruction": "快进到1分10秒", "rag_document": None, "expected_tools": [{"action": "seek_video", "target": None, "device": "主屏幕", "value": 70}]},
            {"instruction": "跳到5分钟看看", "rag_document": None, "expected_tools": [{"action": "seek_video", "target": None, "device": "主屏幕", "value": 300}]},
            {"instruction": "从30秒开始播放", "rag_document": None, "expected_tools": [{"action": "seek_video", "target": None, "device": "主屏幕", "value": 30}]},
            {"instruction": "帮我跳到3分20秒", "rag_document": None, "expected_tools": [{"action": "seek_video", "target": None, "device": "主屏幕", "value": 200}]},
            {"instruction": "快进到4分15秒", "rag_document": None, "expected_tools": [{"action": "seek_video", "target": None, "device": "主屏幕", "value": 255}]},
            {"instruction": "跳到1分钟", "rag_document": None, "expected_tools": [{"action": "seek_video", "target": None, "device": "主屏幕", "value": 60}]},
            {"instruction": "跳转到2分45秒", "rag_document": None, "expected_tools": [{"action": "seek_video", "target": None, "device": "主屏幕", "value": 165}]},
            {"instruction": "从10秒开始", "rag_document": None, "expected_tools": [{"action": "seek_video", "target": None, "device": "主屏幕", "value": 10}]},
            {"instruction": "跳转到6分30秒", "rag_document": None, "expected_tools": [{"action": "seek_video", "target": None, "device": "主屏幕", "value": 390}]},
        ]

        # 复合指令 (15条)
        complex_instructions = [
            {"instruction": "我想看5G技术总览，然后打开5G先锋体验区的门", "rag_document": "5G_Overview_Intro.mp4", "expected_tools": [
                {"action": "play", "target": "5G_Overview_Intro.mp4", "device": "主屏幕", "value": None},
                {"action": "open", "target": "5G先锋体验区的门", "device": None, "value": None}
            ]},
            {"instruction": "放一下智慧家庭解决方案的视频，音量调到80", "rag_document": "Smart_Home_Solutions.mp4", "expected_tools": [
                {"action": "play", "target": "Smart_Home_Solutions.mp4", "device": "主屏幕", "value": None},
                {"action": "set_volume", "target": None, "device": "主屏幕", "value": 80}
            ]},
            {"instruction": "在左边互动屏看看云计算，然后跳到2分钟", "rag_document": "Cloud_BigData_Capabilities.mp4", "expected_tools": [
                {"action": "play", "target": "Cloud_BigData_Capabilities.mp4", "device": "左侧互动大屏", "value": None},
                {"action": "seek_video", "target": None, "device": "左侧互动大屏", "value": 120}
            ]},
            {"instruction": "播放人工智能视频，声音大一点", "rag_document": "AI_Applications_Frontier.mp4", "expected_tools": [
                {"action": "play", "target": "AI_Applications_Frontier.mp4", "device": "主屏幕", "value": None},
                {"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "up"}
            ]},
            {"instruction": "打开智慧生活馆的门，然后放智慧城市的视频", "rag_document": "Smart_City_Future_Vision.mp4", "expected_tools": [
                {"action": "open", "target": "智慧生活馆的门", "device": None, "value": None},
                {"action": "play", "target": "Smart_City_Future_Vision.mp4", "device": "主屏幕", "value": None}
            ]},
            {"instruction": "放一下5G网络切片，音量调60，然后打开未来科技中心的门", "rag_document": "5G_Network_Slicing.mp4", "expected_tools": [
                {"action": "play", "target": "5G_Network_Slicing.mp4", "device": "主屏幕", "value": None},
                {"action": "set_volume", "target": None, "device": "主屏幕", "value": 60},
                {"action": "open", "target": "未来科技赋能中心的门", "device": None, "value": None}
            ]},
            {"instruction": "在右边演示屏看看智慧农业，然后跳到1分30秒", "rag_document": "Smart_Agriculture_Solution.mp4", "expected_tools": [
                {"action": "play", "target": "Smart_Agriculture_Solution.mp4", "device": "右侧演示屏", "value": None},
                {"action": "seek_video", "target": None, "device": "右侧演示屏", "value": 90}
            ]},
            {"instruction": "播放智慧医疗视频，声音小一点，然后关上数字应用体验中心的门", "rag_document": "Smart_Healthcare_Imaging_Cloud.mp4", "expected_tools": [
                {"action": "play", "target": "Smart_Healthcare_Imaging_Cloud.mp4", "device": "主屏幕", "value": None},
                {"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "down"},
                {"action": "close", "target": "数字应用体验中心的门", "device": None, "value": None}
            ]},
            {"instruction": "播放AR应用视频，音量设置为70，然后跳转到3分钟", "rag_document": "Augmented_Reality_Applications.mp4", "expected_tools": [
                {"action": "play", "target": "Augmented_Reality_Applications.mp4", "device": "主屏幕", "value": None},
                {"action": "set_volume", "target": None, "device": "主屏幕", "value": 70},
                {"action": "seek_video", "target": None, "device": "主屏幕", "value": 180}
            ]},
            {"instruction": "打开5G先锋体验区的门，播放VR体验视频，然后提高音量", "rag_document": "Virtual_Reality_Experience.mp4", "expected_tools": [
                {"action": "open", "target": "5G先锋体验区的门", "device": None, "value": None},
                {"action": "play", "target": "Virtual_Reality_Experience.mp4", "device": "主屏幕", "value": None},
                {"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "up"}
            ]},
            {"instruction": "播放全球战略视频，音量调到40，然后打开未来科技中心的门", "rag_document": "Global_Strategy_BRI.mp4", "expected_tools": [
                {"action": "play", "target": "Global_Strategy_BRI.mp4", "device": "主屏幕", "value": None},
                {"action": "set_volume", "target": None, "device": "主屏幕", "value": 40},
                {"action": "open", "target": "未来科技赋能中心的门", "device": None, "value": None}
            ]},
            {"instruction": "在左侧互动大屏播放网络安全视频，然后降低音量", "rag_document": "Cyber_Security_Defense_System.mp4", "expected_tools": [
                {"action": "play", "target": "Cyber_Security_Defense_System.mp4", "device": "左侧互动大屏", "value": None},
                {"action": "adjust_volume", "target": None, "device": "左侧互动大屏", "value": "down"}
            ]},
            {"instruction": "播放量子通信视频，跳转到2分15秒，然后关闭智慧生活馆的门", "rag_document": "Quantum_Communication_Encryption.mp4", "expected_tools": [
                {"action": "play", "target": "Quantum_Communication_Encryption.mp4", "device": "主屏幕", "value": None},
                {"action": "seek_video", "target": None, "device": "主屏幕", "value": 135},
                {"action": "close", "target": "智慧生活馆的门", "device": None, "value": None}
            ]},
            {"instruction": "播放超级SIM卡视频，音量增加到90，然后打开数字应用体验中心的门", "rag_document": "Super_SIM_Functionality.mp4", "expected_tools": [
                {"action": "play", "target": "Super_SIM_Functionality.mp4", "device": "主屏幕", "value": None},
                {"action": "set_volume", "target": None, "device": "主屏幕", "value": 90},
                {"action": "open", "target": "数字应用体验中心的门", "device": None, "value": None}
            ]},
            {"instruction": "播放和彩云网盘视频，音量调小，跳转到1分钟，然后关闭5G先锋体验区的门", "rag_document": "HeCaiYun_Cloud_Drive.mp4", "expected_tools": [
                {"action": "play", "target": "HeCaiYun_Cloud_Drive.mp4", "device": "主屏幕", "value": None},
                {"action": "adjust_volume", "target": None, "device": "主屏幕", "value": "down"},
                {"action": "seek_video", "target": None, "device": "主屏幕", "value": 60},
                {"action": "close", "target": "5G先锋体验区的门", "device": None, "value": None}
            ]},
        ]

        # 组合所有测试用例
        test_cases.extend(video_instructions)
        test_cases.extend(door_instructions)
        test_cases.extend(volume_instructions)
        test_cases.extend(seek_instructions)
        test_cases.extend(complex_instructions)
        test_cases.extend(alternative_screen_videos)

        # 确保总共100条
        while len(test_cases) < 100:
            # 复制一些简单指令来补齐
            test_cases.extend(video_instructions[:100-len(test_cases)])

        return test_cases[:100]

    async def run_llm_rag_processor_logic(self, recognized_text: str) -> Dict[str, Any]:
        """
        独立实现 run_llm_rag_processor 的核心逻辑
        这完全复制了原函数的处理流程
        """
        logger.info(f"处理指令: {recognized_text}")

        try:
            # 1. RAG检索
            retrieved_docs = await self.rag_processor.retrieve_context(recognized_text)
            logger.info(f"RAG检索到 {len(retrieved_docs)} 个文档")

            # 2. 创建指令重试处理器
            retry_handler = SmartRetryHandler(self.settings.llm)

            # 3. 执行指令重试
            retry_result = await retry_handler.execute_instruction_retry(
                original_input=recognized_text,
                llm_function=self.llm_processor.get_response,
                rag_docs=retrieved_docs
            )

            # 4. 记录重试统计信息
            if retry_result.attempt_count > 1:
                logger.info(f"[重试统计] 尝试次数: {retry_result.attempt_count}, 总耗时: {retry_result.total_time:.2f}s, 成功: {retry_result.success}")

            llm_response = retry_result.response
            logger.info(f"[大模型响应] {llm_response}")

            # 5. 解析响应
            try:
                parsed_response = json.loads(llm_response)
                if isinstance(parsed_response, list):
                    tool_calls = parsed_response
                else:
                    tool_calls = [parsed_response]
            except json.JSONDecodeError:
                tool_calls = []

            return {
                "recognized_text": recognized_text,
                "rag_docs": [doc.metadata.get("filename", "") for doc in retrieved_docs],
                "llm_response": llm_response,
                "tool_calls": tool_calls,
                "retry_count": retry_result.attempt_count,
                "success": retry_result.success,
                "total_time": retry_result.total_time
            }

        except Exception as e:
            logger.error(f"处理指令时出错: {e}")
            return {
                "recognized_text": recognized_text,
                "rag_docs": [],
                "llm_response": "",
                "tool_calls": [],
                "retry_count": 0,
                "success": False,
                "total_time": 0,
                "error": str(e)
            }

    def validate_test_case(self, test_case: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证测试用例的结果
        """
        instruction = test_case["instruction"]
        rag_document = test_case.get("rag_document")
        expected_tools = test_case["expected_tools"]

        # 检查RAG文档是否包含预期的文档（如果指定了的话）
        rag_validation = True
        rag_reason = ""

        if rag_document and rag_document not in result["rag_docs"]:
            rag_validation = False
            rag_reason = f"预期RAG文档 '{rag_document}' 未找到，实际返回: {result['rag_docs']}"

        # 检查工具调用
        tool_validation = True
        tool_reason = ""

        if len(result["tool_calls"]) != len(expected_tools):
            tool_validation = False
            tool_reason = f"工具调用数量不匹配，预期: {len(expected_tools)}, 实际: {len(result['tool_calls'])}"
        else:
            for i, (expected, actual) in enumerate(zip(expected_tools, result["tool_calls"])):
                # 检查action
                if expected["action"] != actual.get("action"):
                    tool_validation = False
                    tool_reason = f"工具{i} action不匹配，预期: {expected['action']}, 实际: {actual.get('action')}"
                    break

                # 检查target
                if expected["target"] != actual.get("target"):
                    tool_validation = False
                    tool_reason = f"工具{i} target不匹配，预期: {expected['target']}, 实际: {actual.get('target')}"
                    break

                # 检查device（考虑None值）
                if expected["device"] != actual.get("device"):
                    tool_validation = False
                    tool_reason = f"工具{i} device不匹配，预期: {expected['device']}, 实际: {actual.get('device')}"
                    break

                # 检查value（如果存在）
                if "value" in expected and expected["value"] != actual.get("value"):
                    tool_validation = False
                    tool_reason = f"工具{i} value不匹配，预期: {expected['value']}, 实际: {actual.get('value')}"
                    break

        overall_success = rag_validation and tool_validation and result["success"]

        return {
            "instruction": instruction,
            "success": overall_success,
            "rag_validation": rag_validation,
            "rag_reason": rag_reason,
            "tool_validation": tool_validation,
            "tool_reason": tool_reason,
            "result": result
        }

    async def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行单个测试用例
        """
        instruction = test_case["instruction"]

        logger.info(f"测试指令: {instruction}")

        # 执行 run_llm_rag_processor 逻辑
        result = await self.run_llm_rag_processor_logic(instruction)

        # 验证结果
        validation = self.validate_test_case(test_case, result)

        return validation

    async def run_all_tests(self) -> Dict[str, Any]:
        """
        运行所有测试用例
        """
        logger.info("开始运行 run_llm_rag_processor 测试...")

        # 创建测试用例
        test_cases = self.create_test_cases()
        logger.info(f"创建了 {len(test_cases)} 个测试用例")

        # 运行测试
        total_tests = len(test_cases)
        passed = 0
        failed = 0

        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"运行测试 {i}/{total_tests}")

            try:
                result = await self.run_single_test(test_case)
                self.test_results.append(result)

                if result["success"]:
                    passed += 1
                else:
                    failed += 1
                    self.failed_cases.append(result)

                # Ollama 不需要速率限制
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"测试用例 {i} 执行失败: {e}")
                failed += 1
                self.failed_cases.append({
                    "instruction": test_case["instruction"],
                    "success": False,
                    "error": str(e)
                })

        # 生成总结
        summary = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total_tests) * 100,
            "failed_cases": self.failed_cases
        }

        logger.info(f"测试完成: {passed}/{total_tests} 通过 ({summary['success_rate']:.1f}%)")

        return summary

    def print_summary(self, summary: Dict[str, Any]):
        """
        打印测试总结
        """
        print("\n" + "="*80)
        print("run_llm_rag_processor 测试总结")
        print("="*80)
        print(f"总测试数: {summary['total_tests']}")
        print(f"通过: {summary['passed']}")
        print(f"失败: {summary['failed']}")
        print(f"成功率: {summary['success_rate']:.1f}%")

        if summary['failed_cases']:
            print(f"\n失败用例 ({len(summary['failed_cases'])}):")
            print("-" * 80)
            for i, case in enumerate(summary['failed_cases'], 1):
                print(f"{i}. 指令: {case['instruction']}")
                print(f"   状态: 失败")
                if 'error' in case:
                    print(f"   错误: {case['error']}")
                elif 'rag_reason' in case and case['rag_reason']:
                    print(f"   RAG问题: {case['rag_reason']}")
                elif 'tool_reason' in case and case['tool_reason']:
                    print(f"   工具调用问题: {case['tool_reason']}")
                print()


async def main():
    """
    主测试函数
    """
    # 配置日志
    logger.add("test_run_llm_rag_processor_results.log", rotation="10 MB", level="INFO")

    print("开始 run_llm_rag_processor 专项测试...")
    print("注意: 确保 Ollama 服务正在运行")
    print("注意: 本测试独立搭建 run_llm_rag_processor 逻辑，不依赖后台服务")
    print("注意: 对 ModelScope 应用速率限制 (2秒/测试)\n")

    # 创建测试器
    tester = RunLLMRAGProcessorTester()

    # 异步初始化
    await tester.initialize_async()

    # 运行测试
    summary = await tester.run_all_tests()

    # 打印总结
    tester.print_summary(summary)

    # 保存详细结果
    with open("test_run_llm_rag_processor_detailed.json", 'w', encoding='utf-8') as f:
        json.dump({
            "summary": summary,
            "detailed_results": tester.test_results
        }, f, ensure_ascii=False, indent=2)

    # 保存总结
    with open("test_run_llm_rag_processor_summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n详细结果保存到: test_run_llm_rag_processor_detailed.json")
    print(f"测试总结保存到: test_run_llm_rag_processor_summary.json")


if __name__ == "__main__":
    asyncio.run(main())