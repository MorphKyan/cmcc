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
*   **多资源模糊匹配**: 当用户的语音指令中包含“打开”、“播放”、“展示”、“看看”等意图时，如果其指代的资源名称不完整、描述模糊，或者在知识库中匹配到了多个名称相近的候选资源，导致你无法唯一确定要播放哪一个资源时，请**积极调用** `prompt_multiple_choices` 工具。将最佳候选资源（最多3项）以列表形式返回供用户选择。只要存在匹配歧义，应优先让用户选择而不是盲目猜测或拒绝。
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


class VADSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VAD_")

    chunk_size: int = 200
    sample_rate: int = 16000
    model: str = "silero-vad"
    model_dir: str = os.path.join(project_dir, "models", "silero_vad.onnx")
    max_single_segment_time: int = 20000  # 最大切割音频时长(ms)
    save_audio_segments: bool = True  # 是否保存切割出来的音频片段
    history_buffer_duration_sec: int = 30  # 历史缓冲区最大时长(秒)
    chunk_queue_maxsize: int = 10000  # 音频块队列最大容量
    safety_margin_sec: int = 5  # 提取音频后保留的安全边界(秒)
    speech_noise_thres: float = 0.5  # 语音/噪声阈值，Silero VAD 推荐 0.5
    decibel_thres: float = -100.0  # 绝对语音/静音分贝阈值，低于此值强制判定为静音


class ASRSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ASR_", extra="ignore")

    # ASR Settings (SenseVoice Small ONNX)
    model_dir: str = os.path.join(project_dir, "models", "sense-voice-small")
    sample_rate: int = 16000
    language: str = "auto"
    use_itn: bool = True
    
    # SPK Settings (WeSpeaker ResNet34 ONNX)
    spk_model_path: str = os.path.join(project_dir, "models", "wespeaker_resnet34.onnx")
    spk_sim_threshold: float = 0.55  # 识别目标说话人的相似度阈值
    fallback_speaker_label: str = "环境音/非目标" # 如果未识别出目标说话人时的标签

    # For compatibility if used elsewhere
    batch_size: int = 1 
    use_vad: bool = False
    itn: bool = True
    hotwords: list[str] = []

class DataSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATA_")

    media_data_path: str = os.path.join(data_dir, "media.csv")
    devices_data_path: str = os.path.join(data_dir, "devices.csv")
    areas_data_path: str = os.path.join(data_dir, "areas.csv")
    doors_data_path: str = os.path.join(data_dir, "doors.csv")
    dynamic_tools_path: str = os.path.join(data_dir, "dynamic_tools.json")
    hotwords_data_path: str = os.path.join(data_dir, "hotwords.json")


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


class TTSSettings(BaseSettings):
    """文本转语音(TTS)配置"""
    model_config = SettingsConfigDict(env_prefix="TTS_")

    model_dir: str = os.path.join(project_dir, "models", "vits-melo-tts-zh_en")
    speed: float = 1.0
    speaker_id: int = 0
    num_threads: int = 2


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter='_',
        env_file=None,
        extra='allow'
    )

    data: DataSettings = DataSettings()
    vad: VADSettings = VADSettings()
    asr: ASRSettings = ASRSettings()
    rag: RAGSettings = RAGSettings()
    llm: LLMSettings = LLMSettings()
    aep: AEPSettings = AEPSettings()
    tts: TTSSettings = TTSSettings()

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