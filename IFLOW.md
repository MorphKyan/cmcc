# iFlow CLI 上下文信息 (IFLOW.md)

## 项目概述

这是一个基于实时语音识别和大型语言模型（LLM）的智能控制系统，专为中国移动智慧展厅设计。它能够将用户的自然语言语音指令，通过RAG（检索增强生成）技术和本地知识库，精确地转换为结构化的JSON指令，用于控制展厅内的设备。

### 核心技术栈

- **Python 3.x**
- **语音识别**: FunASR, PyAudio
- **语音活动检测 (VAD)**: FunASR VAD模型
- **大语言模型 (LLM)**: 支持本地Ollama模型和火山引擎方舟模型
- **RAG (检索增强生成)**: Langchain, ChromaDB, HuggingFace Embeddings
- **数据处理**: Pandas
- **Web API**: FastAPI, Uvicorn

### 项目架构

项目采用模块化设计，主要模块包括：

1.  **配置 (`src/config.py`)**: 集中管理所有配置项，如API密钥、模型路径、Prompt模板、音频参数等。
2.  **数据加载 (`src/module/data_loader.py`)**: 从CSV文件加载设备和视频信息，并格式化为文档。
3.  **RAG处理 (`src/module/rag/rag_processor.py`)**: 负责创建和查询本地ChromaDB向量数据库，为LLM提供上下文信息。
4.  **LLM交互**:
    -   Ollama (`src/module/llm/ollama_llm_handler.py`): 与本地Ollama大模型交互。
    -   火山引擎 (`src/module/llm/ark_llm_handler.py`): 与火山引擎方舟大模型交互。
5.  **音频处理**:
    -   音频输入 (`src/module/input/audio_input.py`): 处理麦克风音频输入。
    -   VAD处理 (`src/module/vad/vad_processor.py`): 检测语音活动。
    -   ASR处理 (`src/module/asr/asr_processor.py`): 将语音转换为文本。
6.  **应用核心 (`src/app/voice_assistant.py`)**: 整合所有模块，实现核心业务逻辑。
7.  **主入口 (`src/main.py`)**: 程序的启动点，处理命令行参数并初始化`VoiceAssistant`。
8.  **Web API服务 (`src/api/main.py`)**: 提供基于FastAPI的RESTful API服务，支持RAG查询、数据库刷新和文件上传等功能。
9.  **WebSocket音频处理 (`src/api/routers/audio.py`)**: 通过WebSocket接收实时音频流并进行处理。

### 数据源

-   `data/screens.csv`: 屏幕设备信息。
-   `data/doors.csv`: 门设备信息。
-   `data/videos.csv`: 视频信息。

## 构建和运行

### 环境准备

在启动项目之前，需要确保已安装所有依赖项。

### 安装依赖

在项目根目录下运行以下命令安装所需依赖：

```bash
pip install -r requirements.txt
```

**注意**: `pyaudio` 在某些系统上可能需要预先安装PortAudio库。

### 配置

1.  **API密钥**: 如果使用火山引擎模型，需要在 `src/config.py` 中配置 `ARK_API_KEY`。
2.  **Ollama模型**: 确保本地已安装并运行Ollama服务，并且所需模型（如 `qwen3:8b`）已拉取。

### 启动程序

#### 1. 启动主语音控制程序

在项目根目录下执行以下命令启动程序：

```bash
python src/main.py
```

#### 2. 启动Web API服务

在项目根目录下执行以下命令启动FastAPI服务：

```bash
python src/api/main.py
```

或者使用uvicorn命令启动：

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 5000
```

### 命令行选项

#### 主程序 (`src/main.py`)

-   `--device [auto|cpu|cuda:0]`: 选择用于推理的设备 (默认: `auto`)。
-   `--llm-provider [ark|ollama]`: 选择大语言模型提供商 (默认: `ollama`)。

#### Web API服务 (`src/api/main.py`)

-   `--host`: 指定绑定的主机地址 (默认: 0.0.0.0)
-   `--port`: 指定绑定的端口号 (默认: 5000)

## API端点

- `GET /` - 健康检查端点
- `GET /api/health` - 健康检查端点
- `POST /api/rag/refresh` - 刷新RAG数据库
- `GET /api/rag/status` - 获取RAG状态
- `POST /api/rag/query` - 查询RAG数据库
- `POST /api/rag/upload-videos` - 上传videos.csv文件并更新RAG数据库
- `WebSocket /api/audio/ws/{client_id}` - WebSocket音频处理端点

## 开发约定

-   **模块化**: 代码严格遵循模块化设计，每个模块职责单一。
-   **配置驱动**: 通过 `config.py` 集中管理配置，便于维护。
-   **RAG增强**: 利用本地知识库和向量数据库提升LLM在特定领域的准确性。
-   **实时处理**: 采用多线程处理音频流、VAD、ASR、RAG和LLM调用，保证实时性。
-   **错误处理**: 各模块包含基本的错误处理逻辑，确保程序稳定性。
-   **Prompt Engineering**: 使用详细的系统提示模板指导LLM行为，支持Function Calling。
-   **API设计**: 遵循RESTful API设计原则，提供清晰的接口文档和错误处理机制。