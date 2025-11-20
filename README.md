# 中国移动智慧展厅 - 实时语音控制中心

本项目是一个基于实时语音识别和大型语言模型（LLM）的智能控制系统。它能够将用户的自然语言语音指令，通过RAG（检索增强生成）技术和本地知识库，精确地转换为结构化的JSON指令，用于控制展厅内的设备。

## 项目特性

- **模块化设计**: 代码遵循最佳实践，被拆分为配置、数据加载、RAG处理、LLM交互和语音识别等多个模块，易于维护和扩展。
- **RAG增强**: 集成了基于本地CSV文件的RAG流程。系统会自动从`data/`目录读取知识，并创建本地向量数据库（ChromaDB），以提高LLM在特定领域任务上的准确性。
- **实时处理**: 使用FunASR和PyAudio实现低延迟的实时语音识别。
- **语音活动检测**: 集成了基于FunASR的VAD（语音活动检测）功能，只在检测到语音活动时进行处理，提高效率并减少误识别。
- **本地化知识库**: 知识库管理通过本地ChromaDB实现，无需依赖外部服务，保证了数据私密性和响应速度。
- **配置灵活**: 支持通过命令行参数选择推理设备（CPU/GPU）并可强制刷新知识库。
- **RESTful API服务**: 提供了基于FastAPI的RESTful API服务，支持远程刷新RAG数据库和查询功能，具有自动生成的API文档。

## 项目结构

```
.
├── src/
│   ├── __init__.py
│   ├── config.py               # 存放所有配置，如API密钥、模型路径、Prompt模板
│   ├── data_loader.py          # 从CSV加载和格式化文档
│   ├── ark_llm_handler.py      # 封装与火山引擎大模型的交互逻辑
│   ├── ollama_llm_handler.py   # 封装与本地Ollama大模型的交互逻辑
│   ├── rag_processor.py        # 负责创建和查询本地ChromaDB向量数据库
│   ├── audio_input.py          # 处理麦克风音频输入
│   ├── vad_processor.py        # 语音活动检测处理器
│   ├── app/
│   │   └── voice_assistant.py  # 核心业务逻辑，整合语音识别、RAG和LLM
│   └── api/
│       └── rag_api.py          # RESTful API服务，提供RAG数据库管理接口
├── data/
│   ├── screens.csv             # 屏幕设备信息
│   ├── doors.csv               # 门设备信息（包含 name, type, area1, area2, location 列）
│   ├── areas.csv               # 区域信息（包含 name, aliases, description 列）
│   └── videos.csv              # 视频信息
├── chroma_db/
│   └── ...                     # (自动生成) 本地向量数据库文件
├── main.py                     # 项目主入口
├── run_api.py                  # API服务启动脚本
├── test_api.py                 # API服务测试脚本
├── requirements.txt            # 项目依赖
└── README.md                   # 本文档
```
```

## 安装指南

1.  **克隆或下载项目**:
    将本项目代码下载到您的本地机器。

2.  **激活虚拟环境**:
    项目使用 `.venv` 虚拟环境。在项目根目录下激活虚拟环境：
    - **Windows**: `.venv\Scripts\activate`
    - **Linux/macOS**: `source .venv/bin/activate`

3.  **安装Python依赖** (如果虚拟环境未预先配置):
    在激活的虚拟环境中运行：
    ```bash
    pip install -r requirements.txt
    ```
    *注意: `pyaudio` 在某些系统上可能需要预先安装PortAudio库。*
    -   在Debian/Ubuntu上: `sudo apt-get install portaudio19-dev`
    -   在macOS上: `brew install portaudio`

4.  **配置API Key**:
    打开 `src/config/config.py` 文件，找到 `ARK_API_KEY` 变量，并将其替换为您自己的火山引擎API密钥。

### 配置文件优先级

系统使用以下优先级顺序加载配置：

1. **`config/config.toml`** - 用户的实际配置文件（推荐使用）
2. **`config/config.example.toml`** - 回退到示例配置文件（如果用户配置不存在）
3. **内置默认值** - 如果配置文件都不存在，使用代码中的默认值

**使用方法**：
- 复制 `config/config.example.toml` 到 `config/config.toml`
- 编辑 `config/config.toml` 以自定义您的设置
- 系统会自动优先加载您的 `config.toml` 文件

**环境变量覆盖**：
- 可以通过 `CONFIG_FILE` 环境变量指定配置文件路径
- 例如：`CONFIG_FILE=/path/to/custom/config.toml python main.py`

## 运行程序

在项目根目录下打开终端，确保已激活虚拟环境，然后执行以下命令：

```bash
python main.py
```

程序启动后，会自动检测并加载所需的模型和数据。第一次运行时，它会从`data/`目录下的CSV文件创建本地向量数据库，这可能需要一些时间，具体取决于您的机器性能。

### 命令行选项

-   **基本配置**:
    ```bash
    # 指定主机和端口
    python main.py --host 0.0.0.0 --port 5000

    # 启用HTTPS/WSS支持（使用项目中的SSL证书）
    python main.py --ssl-certfile frontend/vue-project/morph_icu.pem --ssl-keyfile frontend/vue-project/morph_icu.key

    # 启用HTTPS/WSS支持（使用自定义SSL证书）
    python main.py --ssl-certfile /path/to/your/cert.pem --ssl-keyfile /path/to/your/key.key --port 443
    ```

-   **自动SSL检测**:
    如果未指定SSL证书参数，系统会自动检测 `frontend/vue-project/` 目录中的 `morph_icu.pem` 和 `morph_icu.key` 文件，如果存在则自动启用HTTPS/WSS支持。

-   **HTTPS/WSS优势**:
    - 解决前端HTTPS与后端HTTP的混合内容问题
    - 支持WebSocket Secure (WSS) 连接
    - 适用于局域网内部安全通信
    - 与前端Vite开发服务器的HTTPS配置完美匹配

### 注意事项

- 确保在运行命令前已激活虚拟环境：`.venv\Scripts\activate` (Windows) 或 `source .venv/bin/activate` (Linux/macOS)
- SSL证书文件路径必须正确，否则会显示错误信息
- 如果只提供证书文件或密钥文件中的一个，程序将报错并退出

## 如何工作

1.  **启动**: 程序加载FunASR语音识别模型和本地ChromaDB向量数据库。
2.  **录音**: 程序通过麦克风实时录制音频。
3.  **语音活动检测 (VAD)**: 使用VAD模型检测音频中的语音活动，只在检测到语音时进行处理。
4.  **语音转文字 (ASR)**: 将检测到的语音段发送给FunASR模型，转换为文本。
5.  **检索 (Retrieve)**: 识别出的文本被用作查询，在ChromaDB中进行语义搜索，找出最相关的几条知识（例如，相关的视频或设备信息）。
6.  **增强 (Augment)**: 检索到的知识被格式化并插入到一个预设的Prompt模板中，形成一个内容丰富的上下文。
7.  **生成 (Generate)**: 增强后的Prompt被发送给大模型（火山引擎或Ollama）。
8.  **输出**: 大模型根据上下文和用户指令，生成一个结构化的JSON命令，并打印在控制台。

## 运行API服务

本项目提供了一个基于FastAPI的RESTful API服务，可以远程管理RAG数据库。API服务已集成到主程序中，启动主程序即启动API服务：

```bash
# HTTP模式（默认）
python main.py

# HTTPS模式（推荐，解决混合内容问题）
python main.py --ssl-certfile frontend/vue-project/morph_icu.pem --ssl-keyfile frontend/vue-project/morph_icu.key
```

API服务将在以下地址启动：
- HTTP模式: `http://localhost:5000`
- HTTPS模式: `https://localhost:5000`

FastAPI提供了自动生成的API文档：
- 交互式API文档: `[http|https]://localhost:5000/docs`
- ReDoc文档: `[http|https]://localhost:5000/redoc`

### API端点

- `GET /api/health` - 健康检查端点
- `POST /api/rag/refresh` - 刷新RAG数据库
- `GET /api/rag/status` - 获取RAG状态
- `POST /api/rag/query` - 查询RAG数据库
- `POST /api/data/upload-videos` - 上传videos.csv文件并更新RAG数据库

### API使用示例

1. 刷新RAG数据库:
   ```bash
   curl -X POST http://localhost:5000/api/rag/refresh
   ```

2. 查询RAG状态:
   ```bash
   curl -X GET http://localhost:5000/api/rag/status
   ```

3. 查询RAG数据库:
   ```bash
   curl -X POST http://localhost:5000/api/rag/query \
        -H "Content-Type: application/json" \
        -d '{"query": "我想看关于5G的视频"}'
   ```

4. 上传videos.csv文件:
   ```bash
   curl -X POST http://localhost:5000/api/data/upload-videos \
        -F "file=@/path/to/your/videos.csv"
   ```
