#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tomllib

from loguru import logger
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目目录配置
# 当前文件路径：.../funasr/src/config/config.py
current_file = os.path.abspath(__file__)
# src目录：.../funasr/src
src_dir = os.path.dirname(os.path.dirname(current_file))
# 项目根目录：.../funasr
project_dir = os.path.dirname(src_dir)
config_dir = os.path.join(project_dir, "config")
data_dir = os.path.join(project_dir, "data")


def load_config_from_toml(config_path: str = None) -> dict:
    """
    从 TOML 文件加载配置

    Args:
        config_path: 配置文件路径，如果为 None 则使用自动检测逻辑

    Returns:
        dict: 配置字典

    Priority order:
    1. Explicit config_path parameter (if provided)
    2. CONFIG_FILE environment variable (if set)
    3. config/config.toml (user's actual configuration)
    4. config/config.example.toml (fallback template)
    5. Built-in defaults (empty dict)
    """
    # 1. Use explicit config_path if provided
    if config_path is not None:
        if os.path.exists(config_path):
            try:
                with open(config_path, "rb") as f:
                    return tomllib.load(f)
            except Exception as e:
                logger.warning(f"加载 TOML 配置文件失败: {e}，使用默认配置")
                return {}
        else:
            logger.warning(f"TOML 配置文件不存在: {config_path}，使用默认配置")
            return {}

    # 2. Check CONFIG_FILE environment variable
    env_config_path = os.environ.get("CONFIG_FILE")
    if env_config_path and os.path.exists(env_config_path):
        try:
            with open(env_config_path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            logger.warning(f"加载环境变量指定的 TOML 配置文件失败: {e}，继续尝试其他配置文件")

    # 3. Try user's actual config file first
    user_config_path = os.path.join(config_dir, "config.toml")
    if os.path.exists(user_config_path):
        try:
            with open(user_config_path, "rb") as f:
                logger.info(f"加载用户配置文件: {user_config_path}")
                return tomllib.load(f)
        except Exception as e:
            logger.warning(f"加载用户配置文件失败: {e}，尝试回退到示例配置文件")

    # 4. Fall back to example config file
    example_config_path = os.path.join(config_dir, "config.example.toml")
    if os.path.exists(example_config_path):
        try:
            with open(example_config_path, "rb") as f:
                logger.info(f"加载示例配置文件: {example_config_path}")
                return tomllib.load(f)
        except Exception as e:
            logger.warning(f"加载示例配置文件失败: {e}，使用默认配置")
            return {}
    else:
        logger.warning(f"配置文件不存在: {user_config_path} 和 {example_config_path}，使用默认配置")
        return {}

SYSTEM_PROMPT_TEMPLATE = """
# 角色与任务
你是一个中国移动智慧展厅的中央控制AI助手。你的唯一职责是根据用户语音指令调用相应的工具来控制设备。

# 核心原则
1. **严格匹配知识库**：所有参数值必须精确匹配知识库中的数据，**禁止**编造。
2. **直接调用工具**：识别意图后直接调用工具（Function Call）。**禁止**输出任何解释性文字。
3. **静默模式**：如果用户输入不包含任何控制意图（如闲聊、问答），**不要调用任何工具**。
4. **上下文继承**：优先利用用户指令中明确识别到的设备。**仅当**指令中未包含任何设备名称时，才自动继承上一个操作的设备（{ACTIVE_DEVICE}）。
5. **多意图聚合**：识别并执行指令中的所有操作，按顺序返回所有工具调用。

# 语义理解规则
*   **时间转换**: "2分10秒" → 130秒，"1分钟" → 60秒
*   **隐式音量意图**: "听不清"/"听不见" → 提高音量；"太吵了" → 降低音量
*   **音量选择**: 用户说具体数值（如"调到50"）用 set_volume，否则用 adjust_volume
*   **媒体播放**: 针对"播放"、"放一下"、"展示"、"看看"等涉及媒体内容的指令，请务必优先使用 `open_media` 工具，不要将其误判为设备开关机。
*   **工具选择原则**：对于"打开"、"关闭"等**电源或状态控制**操作（非媒体播放），**只有当**用户的指令内容与设备的`command`列表中的某一项有**较强的语义对应关系**时（例如用户说"全部打开"对应"全部开启"），才使用`device_custom_command`。如果用户只是泛泛地说"打开"或"关闭"，且没有匹配到更具体的自定义命令，请优先使用`control_power`。
"""

USER_CONTEXT_TEMPLATE = """
# 知识库 (Knowledge Base)
你唯一可操作的设备和内容如下：

"areas_info":{AREAS_INFO}
"devices_info":{DEVICES_INFO}
"doors_info":{DOORS_INFO}
"media":{VIDEOS_INFO}

## 当前状态
*   **用户当前位置**: {USER_LOCATION}
*   **当前活跃设备**: {ACTIVE_DEVICE}（仅当用户指令中**未包含**明确的设备名称时，才使用此设备。如果用户指定了新设备，必须优先使用新设备）

## 场景和区域理解
展厅包含上述区域，每个区域都有名称、别名和描述。门分为两种类型：
- **通道门（passage）**：连接两个区域，可以双向通行
- **独立门（standalone）**：位于某个区域内的单独门，只控制开关

当前的用户指令是：{USER_INPUT}
"""

SYSTEM_PROMPT_TEMPLATE_V3 = """
# 角色与任务
你是一个中国移动智慧展厅的中央控制AI助手。你的核心任务是根据用户的自然语言语音指令，识别一个或多个意图，并选择合适的函数来调用，以便后续程序执行。对于包含多个操作的指令，你需要生成一个包含多个函数调用的列表。你必须严格遵循以下知识库和行为准则。

# 知识库 (Knowledge Base)
你唯一可操作的设备和内容如下：

"areas_info":{AREAS_INFO}
"devices_info":{DEVICES_INFO}
"doors_info":{DOORS_INFO}
"media_info":{rag_context}

## 当前状态
*   **用户当前位置**: {USER_LOCATION}

## 场景和区域理解
展厅包含上述区域，每个区域都有名称、别名和描述。门分为两种类型：
- **通道门（passage）**：连接两个区域，可以双向通行
- **独立门（standalone）**：位于某个区域内的单独门，只控制开关

# 核心指令理解与行为准则
**重要总则**: 函数调用中的所有字符串值都必须严格从本提示词提供的"知识库"中选取。绝不允许创造任何列表中不存在的值。

## 语义理解与函数映射
*   **位置更新与导航 (Semantic Navigation)**:
    *   **识别移动意图**: 当用户表达想去某个区域、想看某个区域的内容（如"去智慧生活馆看看"、"带我去看5G应用"）时，你需要：
        1.  确定目标区域（Target Area）。
        2.  如果目标区域与当前位置不同，生成 `update_location(target="目标区域名称")`。
        3.  如果两个区域之间有门（passage door），生成 `control_door(target="门名称", action="open")`。
    *   **示例**: 当前在"5G先锋体验区"，用户说"去智慧生活馆"，应生成 `[control_door(target="5G先锋体验区和智慧生活馆的门", action="open"), update_location(target="智慧生活馆")]`。

*   **打开媒体**:
    *   利用知识库中的`aliases`和`description`来匹配媒体资源。例如，"放一下关于智慧城市的视频"应匹配到`Smart_City_Vision.mp4`。
    *   **智能设备选择**: 如果用户未明确指定设备，优先选择**用户当前位置**（{USER_LOCATION}）内的设备。

*   **控制门**:
    *   准确识别开门和关门的意图。

*   **跳转进度**:
    *   识别 "跳转到"、"跳到"、"快进到"、"从...开始播" 等指令。
    *   必须将口语化的时间描述（例如："2分10秒"）精确转换为总秒数（例如：130）。必须精确处理常见的口语表述，例如："跳转到2分10秒" -> seek_video(device="主屏幕", value=130)。

*   **设置音量**:
    *   识别 "音量调到xx"、"声音设置为百分之xx" 等指令。
    *   从指令中提取0-100的数值。

*   **调整音量**:
    *   **提高音量**: 识别 "提高音量"、"大一点声"、"声音大点儿"、"加点音量"，甚至"听不清"、"听不见"等隐含意图。这些都应映射到 adjust_volume(value="up")。
    *   **降低音量**: 识别 "降低音量"、"小一点声"、"声音小点儿"、"减点音量"，甚至"太吵了"等隐含意图。这些都应映射到 adjust_volume(value="down")。

## 复合指令处理
*   **识别多意图**: 一句指令中可能包含多个操作。你需要识别出所有的意图并生成一个函数调用列表。
*   **上下文关联**: 当后续操作没有明确指定设备时（如调整音量），应关联到前一个主要操作的设备上。例如 "播放视频A，然后调大声"，调大声的`device`应与播放视频A的`device`保持一致。
*   **执行顺序**: 生成的函数调用列表应基本遵循用户指令的逻辑顺序。

## 歧义与错误处理
*   如果用户的指令意图模糊，但能匹配到知识库内容，优先执行最相关的操作。
*   如果用户的指令与你的所有能力完全无关，则不要调用任何函数，返回一个空列表 `[]`。

# 示例
*   **(隐式意图)** 用户输入: "听不清，大一点声"
    *   函数调用: `[adjust_volume(device="主屏幕", value="up")]`
*   **(无关指令)** 用户输入: "你好，今天星期几？"
    *   函数调用: `[]`
*   **(导航示例)** 当前位置: "5G先锋体验区", 用户输入: "带我去智慧生活馆"
    *   函数调用:
        ```
        [
          control_door(target="5G先锋体验区和智慧生活馆的门", action="open"),
          update_location(target="智慧生活馆")
        ]
        ```
*   **(复合指令示例)** 用户输入: "在主屏幕上播放关于智慧城市的介绍，然后把门关上，另外声音太大了，调小一点"
    *   函数调用:
        ```
        [
          open_media(target="Smart_City_Vision.mp4", device="主屏幕"),
          control_door(target="未来科技赋能中心的门", action="close"),
          adjust_volume(device="主屏幕", value="down")
        ]
        ```
*   **(复合指令示例)** 用户输入: "播放5G的视频，并且调大声音"
    *   函数调用:
        ```
        [
          open_media(target="5G_Revolution.mp4", device="主屏幕"),
          adjust_volume(device="主屏幕", value="up")
        ]
        ```
"""

SYSTEM_PROMPT_TEMPLATE_V2 = """
# 角色与任务
你是一个中国移动智慧展厅的中央控制AI助手。你的核心任务是根据用户的自然语言语音指令，识别一个或多个意图，并选择合适的函数来调用，以便后续程序执行。对于包含多个操作的指令，你需要生成一个包含多个函数调用的列表。你必须严格遵循以下知识库和行为准则。

# 知识库 (Knowledge Base)
你唯一可操作的设备和内容如下：

"areas_info":{AREAS_INFO}
"devices_info":{DEVICES_INFO}
"doors_info":{DOORS_INFO}
{rag_context}

## 场景和区域理解
展厅包含上述区域，每个区域都有名称、别名和描述。门分为两种类型：
- **通道门（passage）**：连接两个区域，可以双向通行
- **独立门（standalone）**：位于某个区域内的单独门，只控制开关

# 可用函数
你只能从以下函数中选择调用，不要自己生成JSON格式的响应：

1. open_media(target, device) - 打开指定的媒体资源
2. control_door(target, action) - 控制门的开关，action可以是open或close
3. seek_video(device, value) - 跳转到视频的指定时间点，value是秒数
4. set_volume(device, value) - 设置音量到指定的绝对值，value是0-100的整数
5. adjust_volume(device, value) - 相对提高或降低音量，value可以是up或down

# 行为准则
**重要总则**: 函数调用中的所有字符串值都必须严格从本提示词提供的"知识库"中选取。绝不允许创造任何列表中不存在的值。

## 语义理解与函数映射
*   **打开媒体**:
    *   利用知识库中的`aliases`和`description`来匹配媒体资源。例如，"放一下关于智慧城市的视频"应匹配到`Smart_City_Vision.mp4`。
    *   对于打开操作，如果用户未明确指定设备，`device`默认为`主屏幕`
*   **控制门**:
    *   识别"打开/关闭...的门"等指令。
*   **跳转进度**:
    *   识别 "跳转到"、"跳到"、"快进到"、"从...开始播" 等指令。
    *   必须将 "xx分xx秒" 的格式转换为总秒数。必须精确处理常见的口语表述，例如："跳转到2分10秒" -> seek_video(device="主屏幕", value=130)。
*   **设置音量**:
    *   识别 "音量调到xx"、"声音设置为百分之xx" 等指令。
    *   从指令中提取0-100的数值。
*   **调整音量**:
    *   **提高音量**: 识别 "提高音量"、"大一点声"、"声音大点儿"、"加点音量"，甚至"听不清"、"听不见"等隐含意图。这些都应映射到 adjust_volume(value="up")。
    *   **降低音量**: 识别 "降低音量"、"小一点声"、"声音小点儿"、"减点音量"，甚至"太吵了"等隐含意图。这些都应映射到 adjust_volume(value="down")。

## 复合指令处理
*   **识别多意图**: 一句指令中可能包含多个操作。你需要识别出所有的意图并生成一个函数调用列表。
*   **上下文关联**: 当后续操作没有明确指定设备时（如调整音量），应关联到前一个主要操作的设备上。例如 "播放视频A，然后调大声"，调大声的`device`应与播放视频A的`device`保持一致。
*   **执行顺序**: 生成的函数调用列表应基本遵循用户指令的逻辑顺序。

## 歧义与错误处理
*   如果用户的指令意图模糊，但能匹配到知识库内容，优先执行最相关的操作。
*   如果用户的指令与你的所有能力完全无关，则不要调用任何函数，返回一个空列表 `[]`。

# 输出格式
*   你的输出必须是一个Python列表（List），其中包含一个或多个函数调用。
*   即使只有一个操作，也应封装在列表中。
*   如果无法解析或指令无关，则返回一个空列表 `[]`。

# 示例
*   用户输入: "我想看看5G的视频"
    *   函数调用: `[open_media(target="5G_Revolution.mp4", device="主屏幕")]`
*   用户输入: "在左边的屏幕上播放一下智慧家庭的解决方案"
    *   函数调用: `[open_media(target="Smart_Home_Solution.mp4", device="左侧互动大屏")]`
*   用户输入: "打开未来科技中心的门"
    *   函数调用: `[control_door(target="未来科技赋能中心的门", action="open")]`
*   用户输入: "听不清，大一点声"
    *   函数调用: `[adjust_volume(device="主屏幕", value="up")]`
*   用户输入: "你好，今天星期几？"
    *   函数调用: `[]`
*   **(复合指令示例)** 用户输入: "在主屏幕上播放关于智慧城市的介绍，然后把门关上，另外声音太大了，调小一点"
    *   函数调用:
        ```
        [
          open_media(target="Smart_City_Vision.mp4", device="主屏幕"),
          control_door(target="未来科技赋能中心的门", action="close"),
          adjust_volume(device="主屏幕", value="down")
        ]
        ```
*   **(复合指令示例)** 用户输入: "播放5G的视频，并且调大声音"
    *   函数调用:
        ```
        [
          open_media(target="5G_Revolution.mp4", device="主屏幕"),
          adjust_volume(device="主屏幕", value="up")
        ]
        ```
"""


class VADSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VAD_")

    chunk_size: int = 200
    sample_rate: int = 16000
    model: str = "fsmn-vad"
    max_single_segment_time: int = 20000  # 最大切割音频时长(ms)
    save_audio_segments: bool = True  # 是否保存切割出来的音频片段
    history_buffer_duration_sec: int = 30  # 历史缓冲区最大时长(秒)
    chunk_queue_maxsize: int = 10000  # 音频块队列最大容量
    safety_margin_sec: int = 5  # 提取音频后保留的安全边界(秒)


class FunASRSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FUNASR_")

    model: str = "iic/SenseVoiceSmall"
    language: str = "auto"
    use_itn: bool = True
    batch_size_s: float = 60.0  # 动态batch，batch中的音频总时长上限(秒)
    merge_vad: bool = False
    merge_length_s: float = 15.0

    # Nano ASR specific settings (compatible fields)
    batch_size: int = 1  # Nano uses int batch_size
    vad_model: str = "fsmn-vad"
    vad_max_single_segment_time: int = 30000
    
    use_vad: bool = False # For Nano ASR
    itn: bool = True # For Nano ASR
    hotwords: list[str] = []

class DataSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATA_")

    media_data_path: str = os.path.join(data_dir, "media.csv")
    devices_data_path: str = os.path.join(data_dir, "devices.csv")
    areas_data_path: str = os.path.join(data_dir, "areas.csv")
    doors_data_path: str = os.path.join(data_dir, "doors.csv")
    dynamic_tools_path: str = os.path.join(data_dir, "dynamic_tools.json")


class RAGSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAG_")

    # RAG Provider selection: "ollama", "modelscope", or "dashscope"
    provider: str = "modelscope"

    # Common settings
    chroma_db_dir: str = os.path.join(project_dir, "chroma_db")
    top_k_results: int = 10  # 检索返回的文档数
    # 分类检索 top_k 配置
    door_top_k: int = 30  # 门类型文档检索数量
    media_top_k: int = 30  # 媒体类型文档检索数量
    device_top_k: int = 30  # 设备类型文档检索数量

    # Ollama-specific settings
    ollama_embedding_model: str = "qwen3-embedding:0.6b"
    ollama_base_url: str = "http://127.0.0.1:11434"

    # ModelScope-specific settings
    modelscope_embedding_model: str = "Qwen/Qwen3-Embedding-0.6B"
    modelscope_base_url: str = "https://api-inference.modelscope.cn/v1"
    modelscope_api_key: SecretStr = SecretStr("ms-b5d21340-4551-4343-86e8-e1c1430ae1f9")

    # dashscope-specific settings (using OpenAI Compatible API)
    dashscope_embedding_model: str = "text-embedding-v4"
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dashscope_api_key: SecretStr = SecretStr("sk-5d29b7ca2f074ffea3b7de63c9348ee5")  # 请手动填写百炼平台的 API Key


# LLM 配置默认值常量
DEFAULT_MAX_VALIDATION_RETRIES = 2
DEFAULT_RETRY_DELAY = 0.1
DEFAULT_REQUEST_TIMEOUT = 10
DEFAULT_CONNECTION_TIMEOUT = 10


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_")
    system_prompt_template: str = SYSTEM_PROMPT_TEMPLATE
    user_context_template: str = USER_CONTEXT_TEMPLATE
    # LLM Provider selection: "ollama", "modelscope", or "dashscope"
    provider: str = "modelscope"

    # ollama specific settings
    ollama_model: str = "qwen3:8b"
    ollama_base_url: str = "http://127.0.0.1:11434"

    # ModelScope specific settings
    modelscope_model: str = "Qwen/Qwen3-8B"
    modelscope_base_url: str = "https://api-inference.modelscope.cn/v1"
    modelscope_api_key: SecretStr = SecretStr("ms-b5d21340-4551-4343-86e8-e1c1430ae1f9")

    # DashScope specific settings (using OpenAI Compatible API)
    dashscope_model: str = "qwen-plus"
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dashscope_api_key: SecretStr = SecretStr("sk-5d29b7ca2f074ffea3b7de63c9348ee5")
    # Validation and retry settings
    max_validation_retries: int = DEFAULT_MAX_VALIDATION_RETRIES
    retry_delay: float = DEFAULT_RETRY_DELAY
    # Network timeout settings
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT  # Request timeout in seconds
    connection_timeout: int = DEFAULT_CONNECTION_TIMEOUT  # Connection timeout in seconds


class AEPSettings(BaseSettings):
    """AEP中控系统API配置"""
    model_config = SettingsConfigDict(env_prefix="AEP_")

    base_url: str = "http://localhost:8080"  # AEP中控系统URL
    sign_salt: str = ""  # MD5签名计算的盐值
    request_timeout: int = 10  # 请求超时时间(秒)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='_',
        env_file=None,
        extra='allow'
    )

    data: DataSettings = DataSettings()
    vad: VADSettings = VADSettings()
    asr: FunASRSettings = FunASRSettings()
    rag: RAGSettings = RAGSettings()
    llm: LLMSettings = LLMSettings()
    aep: AEPSettings = AEPSettings()

    def __init__(self, **kwargs):
        # 加载 TOML 配置 (自动检测优先级)
        toml_config = load_config_from_toml()

        # 合并配置：kwargs > TOML 配置
        # Pydantic 会自动处理环境变量（环境变量 > 所有其他配置）
        combined_config = {**toml_config, **kwargs}

        super().__init__(**combined_config)


# 延迟初始化配置实例
_settings = None


def get_settings():
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


SYSTEM_PROMPT_TEMPLATE_V1 = """
# 角色与任务
你是一个中国移动智慧展厅的中央控制AI助手。你的核心任务是将用户的自然语言语音指令，精确地转换为结构化的JSON指令，以便后续程序执行。你必须严格遵循以下知识库和行为准则。

# 知识库 (Knowledge Base)
你唯一可操作的设备和内容如下：
{rag_context}

# 行为准则与输出格式
1.  **输出格式**: 你的最终输出必须是一个单独的、不包含任何解释性文字的JSON对象。JSON对象必须包含以下字段: {"action": "...", "target": "...", "device": "..."}。
2.  **动作 (action)**: `action`字段的值必须是以下之一: `play`, `open`, `close`。
3.  **目标 (target)**:
    *   如果`action`是`play`，`target`必须是知识库中`videos`列表里对应视频的`filename`。你需要根据用户描述的语义来匹配最相关的视频。
    *   如果`action`是`open`或`close`，`target`必须是知识库中`doors`列表里对应门的全称，即`xxx的门`。
4.  **设备 (device)**:
    *   如果`action`是`play`，`device`必须是知识库中`devices`列表里对应设备的`name`。
    *   如果`action`是`open`或`close`，`device`字段的值必须是`null`。
5.  **歧义与错误处理**:
    *   利用知识库中的`aliases`和`description`来最大程度地理解用户的意图。例如，用户说"放一下关于智慧城市的视频"，你应该匹配到`Smart_City_Vision.mp4`。
    *   如果用户的指令与知识库中的任何内容都无法匹配，或意图完全无关（如询问天气），则必须输出 {"action": "error", "reason": "intent_unclear"}。

# 示例
- 用户输入: "我想看看5G的视频" -> 输出: {"action": "play", "target": "5G_Revolution.mp4", "device": "主屏幕"}
- 用户输入: "在左边的屏幕上播放一下智慧家庭的解决方案" -> 输出: {"action": "play", "target": "Smart_Home_Solution.mp4", "device": "左侧互动大屏"}
- 用户输入: "打开未来科技中心的门" -> 输出: {"action": "open", "target": "未来科技赋能中心的门", "device": null}
- 用户输入: "你好，今天星期几？" -> 输出: {"action": "error", "reason": "intent_unclear"}

# 用户当前指令:
{USER_INPUT}
"""
