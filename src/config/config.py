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
data_dir = os.path.join(os.path.dirname(project_dir), "data")


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
你是一个中国移动智慧展厅的中央控制AI助手。你的核心任务是根据用户的自然语言语音指令，识别一个或多个意图，并选择合适的函数来调用，以便后续程序执行。对于包含多个操作的指令，你需要生成一个包含多个函数调用的列表。你必须严格遵循以下知识库和行为准则。

# 知识库 (Knowledge Base)
你唯一可操作的设备和内容如下：

"areas_info":{AREAS_INFO}
"screens_info":{SCREENS_INFO}
"doors_info":{DOORS_INFO}
"videos_info":{rag_context}

## 场景和区域理解
展厅包含上述区域，每个区域都有名称、别名和描述。门分为两种类型：
- **通道门（passage）**：连接两个区域，可以双向通行
- **独立门（standalone）**：位于某个区域内的单独门，只控制开关

# 核心指令理解与行为准则
**重要总则**: 函数调用中的所有字符串值都必须严格从本提示词提供的"知识库"中选取。绝不允许创造任何列表中不存在的值。

## 语义理解与函数映射
*   **播放视频**:
    *   利用知识库中的`aliases`和`description`来匹配视频。例如，"放一下关于智慧城市的视频"应匹配到`Smart_City_Vision.mp4`。
    *   如果用户未明确指定屏幕，默认在`主屏幕`上播放。
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
*   **(复合指令示例)** 用户输入: "在主屏幕上播放关于智慧城市的介绍，然后把门关上，另外声音太大了，调小一点"
    *   函数调用:
        ```
        [
          play_video(target="Smart_City_Vision.mp4", device="主屏幕"),
          control_door(target="未来科技赋能中心的门", action="close"),
          adjust_volume(device="主屏幕", value="down")
        ]
        ```
*   **(复合指令示例)** 用户输入: "播放5G的视频，并且调大声音"
    *   函数调用:
        ```
        [
          play_video(target="5G_Revolution.mp4", device="主屏幕"),
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
"screens_info":{SCREENS_INFO}
"doors_info":{DOORS_INFO}
{rag_context}

## 场景和区域理解
展厅包含上述区域，每个区域都有名称、别名和描述。门分为两种类型：
- **通道门（passage）**：连接两个区域，可以双向通行
- **独立门（standalone）**：位于某个区域内的单独门，只控制开关

# 可用函数
你只能从以下函数中选择调用，不要自己生成JSON格式的响应：

1. play_video(target, device) - 播放指定的视频文件
2. control_door(target, action) - 控制门的开关，action可以是open或close
3. seek_video(device, value) - 跳转到视频的指定时间点，value是秒数
4. set_volume(device, value) - 设置音量到指定的绝对值，value是0-100的整数
5. adjust_volume(device, value) - 相对提高或降低音量，value可以是up或down

# 行为准则
**重要总则**: 函数调用中的所有字符串值都必须严格从本提示词提供的"知识库"中选取。绝不允许创造任何列表中不存在的值。

## 语义理解与函数映射
*   **播放视频**:
    *   利用知识库中的`aliases`和`description`来匹配视频。例如，"放一下关于智慧城市的视频"应匹配到`Smart_City_Vision.mp4`。
    *   对于播放操作，如果用户未明确指定屏幕，`device`默认为`主屏幕`。
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
    *   函数调用: `[play_video(target="5G_Revolution.mp4", device="主屏幕")]`
*   用户输入: "在左边的屏幕上播放一下智慧家庭的解决方案"
    *   函数调用: `[play_video(target="Smart_Home_Solution.mp4", device="左侧互动大屏")]`
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
          play_video(target="Smart_City_Vision.mp4", device="主屏幕"),
          control_door(target="未来科技赋能中心的门", action="close"),
          adjust_volume(device="主屏幕", value="down")
        ]
        ```
*   **(复合指令示例)** 用户输入: "播放5G的视频，并且调大声音"
    *   函数调用:
        ```
        [
          play_video(target="5G_Revolution.mp4", device="主屏幕"),
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


class FunASRSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FUNASR_")

    model: str = "iic/SenseVoiceSmall"
    language: str = "auto"
    use_itn: bool = True
    batch_size_s: float = 60.0  # 动态batch，batch中的音频总时长上限(秒)
    merge_vad: bool = True
    merge_length_s: float = 15.0


class RAGSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAG_")

    videos_data_path: str = os.path.join(data_dir, "videos.csv")
    chroma_db_dir: str = os.path.join(project_dir, "chroma_db")
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_embedding_model: str = "qwen3-embedding:0.6b"
    top_k_results: int = 3  # 检索返回的文档数


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_")
    system_prompt_template: str = SYSTEM_PROMPT_TEMPLATE
    # LLM Provider selection: "ollama" or "modelscope"
    provider: str = "ollama"

    # ollama specific settings
    ollama_model: str = "qwen3:8b"
    ollama_base_url: str = "http://127.0.0.1:11434"

    # ModelScope specific settings
    modelscope_model: str = "qwen3-8b"
    modelscope_base_url: str = "https://api-inference.modelscope.cn/v1"
    modelscope_api_key: SecretStr = SecretStr("ms-b5d21340-4551-4343-86e8-e1c1430ae1f9")
    # Validation and retry settings
    max_validation_retries: int = 2
    retry_delay: float = 0.1
    # Network timeout settings
    request_timeout: int = 10  # Request timeout in seconds
    connection_timeout: int = 10  # Connection timeout in seconds
    # Network retry settings
    max_network_retries: int = 3  # Maximum network retry attempts
    base_retry_delay: float = 1.0  # Base delay for exponential backoff (seconds)
    max_retry_delay: float = 10.0  # Maximum retry delay (seconds)
    # Legacy retry settings (for backward compatibility)
    max_retries: int = 3  # Legacy field, maps to max_network_retries
    enable_reconnection: bool = True  # Legacy field, always enabled


class VolcEngineSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VOLCENGINE_")

    ark_api_key: SecretStr = SecretStr("aabd9362-9ca8-43ac-bb4d-828f0ba98f4d")
    ark_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    llm_model_name: str = "doubao-seed-1-6-flash-250715"
    # Network timeout settings (inherited from LLMSettings if not specified)
    request_timeout: int = 30  # Request timeout in seconds
    connection_timeout: int = 10  # Connection timeout in seconds
    # Network retry settings (inherited from LLMSettings if not specified)
    max_network_retries: int = 3  # Maximum network retry attempts
    base_retry_delay: float = 1.0  # Base delay for exponential backoff (seconds)
    max_retry_delay: float = 10.0  # Maximum retry delay (seconds)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='_',
        env_file=None,
        extra='allow'
    )

    vad: VADSettings = VADSettings()
    asr: FunASRSettings = FunASRSettings()
    rag: RAGSettings = RAGSettings()
    llm: LLMSettings = LLMSettings()
    volcengine: VolcEngineSettings = VolcEngineSettings()

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


# 为了向后兼容，仍然提供 settings 属性
# 但建议使用 get_settings() 函数
class SettingsProxy:
    def __getattr__(self, name):
        return getattr(get_settings(), name)

    def __setattr__(self, name, value):
        setattr(get_settings(), name, value)


settings = SettingsProxy()

# --- Audio Settings ---
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 16000  # FunASR的最佳采样率
# CHUNK = 1024

# --- System Prompt (V1版本，保持兼容) ---
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
    *   如果`action`是`play`，`device`必须是知识库中`screens`列表里对应屏幕的`name`。如果用户没有明确指定屏幕，默认使用`主屏幕`。
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
