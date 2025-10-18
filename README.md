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
│   ├── doors.csv               # 门设备信息
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

2.  **安装Python依赖**:
    建议在Python 3.8+ 的虚拟环境中进行安装。打开终端，进入项目根目录，然后运行：
    ```bash
    pip install -r requirements.txt
    ```
    *注意: `pyaudio` 在某些系统上可能需要预先安装PortAudio库。*
    -   在Debian/Ubuntu上: `sudo apt-get install portaudio19-dev`
    -   在macOS上: `brew install portaudio`

3.  **配置API Key**:
    打开 `src/config.py` 文件，找到 `ARK_API_KEY` 变量，并将其替换为您自己的火山引擎API密钥。

## 运行程序

在项目根目录下打开终端，执行以下命令：

```bash
python main.py
```

程序启动后，会自动检测并加载所需的模型和数据。第一次运行时，它会从`data/`目录下的CSV文件创建本地向量数据库，这可能需要一些时间，具体取决于您的机器性能。

### 命令行选项

-   **选择设备**:
    默认情况下，程序会自动检测并使用GPU（如果可用）。您可以强制指定设备：
    ```bash
    # 强制使用CPU
    python main.py --device cpu

    # 强制使用GPU
    python main.py --device cuda:0
    ```

-   **更新知识库**:
    如果您修改了 `data/` 目录下的CSV文件（例如，添加了新的视频或设备），您需要使用 `--force-rag-reload` 标志来强制重建向量数据库，以使更改生效：
    ```bash
    python main.py --force-rag-reload
    ```

-   **启用API服务**:
    您可以在启动主程序的同时启动RESTful API服务：
    ```bash
    # 启动主程序并同时启动API服务
    python main.py --enable-api

    # 启动主程序并同时启动API服务，指定端口
    python main.py --enable-api --api-port 8000
    ```

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

本项目还提供了一个基于FastAPI的RESTful API服务，可以远程管理RAG数据库。要启动API服务，请在项目根目录下执行：

```bash
python run_api.py
```

API服务将在 `http://localhost:5000` 上启动。

FastAPI提供了自动生成的API文档：
- 交互式API文档: `http://localhost:5000/docs`
- ReDoc文档: `http://localhost:5000/redoc`

### API端点

- `GET /api/health` - 健康检查端点
- `POST /api/rag/refresh` - 刷新RAG数据库
- `GET /api/rag/status` - 获取RAG状态
- `POST /api/rag/query` - 查询RAG数据库
- `POST /api/rag/upload-videos` - 上传videos.csv文件并更新RAG数据库

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
   curl -X POST http://localhost:5000/api/rag/upload-videos \
        -F "file=@/path/to/your/videos.csv"
   ```
