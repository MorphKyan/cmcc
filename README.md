# 中国移动智慧展厅 - 实时语音控制中心

本项目是一个基于实时语音识别和大型语言模型（LLM）的智能控制系统。它能够将用户的自然语言语音指令，通过RAG（检索增强生成）技术和本地知识库，精确地转换为结构化的JSON指令，用于控制展厅内的设备。

## 项目特性

- **模块化设计**: 代码遵循最佳实践，被拆分为配置、数据加载、RAG处理、LLM交互和语音识别等多个模块，易于维护和扩展。
- **RAG增强**: 集成了基于本地Excel文件的RAG流程。系统会自动从`data/data.xlsx`读取知识，并创建本地向量数据库（ChromaDB），以提高LLM在特定领域任务上的准确性。
- **实时处理**: 使用FunASR和PyAudio实现低延迟的实时语音识别。
- **本地化知识库**: 知识库管理通过本地ChromaDB实现，无需依赖外部服务，保证了数据私密性和响应速度。
- **配置灵活**: 支持通过命令行参数选择推理设备（CPU/GPU）并可强制刷新知识库。

## 项目结构

```
.
├── cmcc_assistant/
│   ├── __init__.py
│   ├── config.py               # 存放所有配置，如API密钥、模型路径、Prompt模板
│   ├── data_loader.py          # 从Excel加载和格式化文档
│   ├── llm_handler.py          # 封装与火山引擎大模型的交互逻辑
│   ├── rag_processor.py        # 负责创建和查询本地ChromaDB向量数据库
│   └── speech_recognizer.py    # 核心业务逻辑，整合语音识别、RAG和LLM
├── data/
│   └── data.xlsx               # 项目的知识源文件，可在此处增删设备和视频信息
├── chroma_db/
│   └── ...                     # (自动生成) 本地向量数据库文件
├── main.py                     # 项目主入口
├── requirements.txt            # 项目依赖
└── README.md                   # 本文档
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
    打开 `cmcc_assistant/config.py` 文件，找到 `ARK_API_KEY` 变量，并将其替换为您自己的火山引擎API密钥。

## 运行程序

在项目根目录下打开终端，执行以下命令：

```bash
python main.py
```

程序启动后，会自动检测并加载所需的模型和数据。第一次运行时，它会从`data/data.xlsx`创建本地向量数据库，这可能需要一些时间，具体取决于您的机器性能。

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
    如果您修改了 `data/data.xlsx` 文件（例如，添加了新的视频或设备），您需要使用 `--force-rag-reload` 标志来强制重建向量数据库，以使更改生效：
    ```bash
    python main.py --force-rag-reload
    ```

## 如何工作

1.  **启动**: 程序加载FunASR语音识别模型和本地ChromaDB向量数据库。
2.  **录音**: 程序通过麦克风实时录制音频。
3.  **语音转文字 (ASR)**: 每隔5秒，程序将收集到的音频块发送给FunASR模型，转换为文本。
4.  **检索 (Retrieve)**: 识别出的文本被用作查询，在ChromaDB中进行语义搜索，找出最相关的几条知识（例如，相关的视频或设备信息）。
5.  **增强 (Augment)**: 检索到的知识被格式化并插入到一个预设的Prompt模板中，形成一个内容丰富的上下文。
6.  **生成 (Generate)**: 增强后的Prompt被发送给火山引擎大模型。
7.  **输出**: 大模型根据上下文和用户指令，生成一个结构化的JSON命令，并打印在控制台。
