#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyaudio
import os

# 获取项目根目录（假设config.py在 src/component/ 下）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# --- API Keys and Endpoints ---
# 请从火山引擎官网获取您的API Key并替换
# https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey
ARK_API_KEY = "aabd9362-9ca8-43ac-bb4d-828f0ba98f4d" 
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
LLM_MODEL_NAME = "doubao-seed-1-6-flash-250715"

# --- Speech Recognition Settings ---
SENSE_VOICE_MODEL_DIR = "iic/SenseVoiceSmall"
VAD_MODEL = "fsmn-vad"
VAD_KWARGS = {"max_single_segment_time": 30000}
LANGUAGE = "auto"
USE_ITN = True
BATCH_SIZE_S = 60
MERGE_VAD = True
MERGE_LENGTH_S = 15

# --- Audio Settings ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # FunASR的最佳采样率
CHUNK = 1024
RECORD_SECONDS = 5  # 每次处理的音频块时长

# --- RAG and ChromaDB Settings ---
EXCEL_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "data.xlsx")
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, "chroma_db")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# RAG检索返回的文档数量
TOP_K_RESULTS = 3 

# --- System Prompt ---
SYSTEM_PROMPT_TEMPLATE = """
# 角色与任务
你是一个中国移动智慧展厅的中央控制AI助手。你的核心任务是将用户的自然语言语音指令，精确地转换为结构化的JSON指令，以便后续程序执行。你必须严格遵循以下知识库和行为准则。

# 知识库 (Knowledge Base)
你唯一可操作的设备和内容如下：
{rag_context}

# 行为准则与输出格式
1.  **输出格式**: 你的最终输出必须是一个单独的、不包含任何解释性文字的JSON对象。JSON对象必须包含以下字段: {{"action": "...", "target": "...", "device": "..."}}。
2.  **动作 (action)**: `action`字段的值必须是以下之一: `play`, `open`, `close`。
3.  **目标 (target)**:
    *   如果`action`是`play`，`target`必须是知识库中`videos`列表里对应视频的`filename`。你需要根据用户描述的语义来匹配最相关的视频。
    *   如果`action`是`open`或`close`，`target`必须是知识库中`doors`列表里对应门的全称，即`xxx的门`。
4.  **设备 (device)**:
    *   如果`action`是`play`，`device`必须是知识库中`screens`列表里对应屏幕的`name`。如果用户没有明确指定屏幕，默认使用`主屏幕`。
    *   如果`action`是`open`或`close`，`device`字段的值必须是`null`。
5.  **歧义与错误处理**:
    *   利用知识库中的`aliases`和`description`来最大程度地理解用户的意图。例如，用户说“放一下关于智慧城市的视频”，你应该匹配到`Smart_City_Vision.mp4`。
    *   如果用户的指令与知识库中的任何内容都无法匹配，或意图完全无关（如询问天气），则必须输出 `{{"action": "error", "reason": "intent_unclear"}}`。

# 示例
- 用户输入: "我想看看5G的视频" -> 输出: {{"action": "play", "target": "5G_Revolution.mp4", "device": "主屏幕"}}
- 用户输入: "在左边的屏幕上播放一下智慧家庭的解决方案" -> 输出: {{"action": "play", "target": "Smart_Home_Solution.mp4", "device": "左侧互动大屏"}}
- 用户输入: "打开未来科技中心的门" -> 输出: {{"action": "open", "target": "未来科技赋能中心的门", "device": null}}
- 用户输入: "你好，今天星期几？" -> 输出: {{"action": "error", "reason": "intent_unclear"}}

# 用户当前指令:
{{USER_INPUT}}
"""
