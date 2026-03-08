# 纯 ONNX 极简目标说话人语音识别 (Target Speaker ASR) 实现计划

本计划详细说明了如何彻底抛弃臃肿的 PyTorch 和 FunASR `AutoModel` 依赖，采用极简、极速的 **全 ONNX 架构** 来实现您的流式要求。核心套件将基于 `sherpa-onnx`（负责 ASR 和 VAD）与 `onnxruntime`（负责声纹比对）。

## 架构优势与变更说明

> [!TIP]
> **为什么要全面转向 ONNX？**
> 1. **体积骤降**：不需要安装几个 GB 的 PyTorch 环境，只需安装轻量级的 `sherpa-onnx`（约几 MB）和模型权重文件即可。
> 2. **速度起飞**：底层全 C++ 运行引擎，内存/库占用极小。**SenseVoice-Small 在 ONNX 下的推理速度远超 Python 原生环境**。
> 3. **完美适配兜底逻辑**：各模块（VAD -> SPK -> ASR）完全解耦，您可以像搭积木一样在内存中传递短句音频，极其适合编写“判断是谁，再说不同的话”这种业务逻辑。

**核心技术栈选型：**
*   **VAD (端点检测)**：使用 `sherpa-onnx` 内置的 **Silero VAD (ONNX)**。比 fsmn-vad 更轻量、抗噪能力更强。
*   **SPK (声纹识别)**：使用 **WeSpeaker 的 ResNet34 (ONNX)** 导出模型。提取一个特征只需要 ~15ms。
*   **ASR (语音识别)**：使用 **SenseVoice-Small (ONNX)**。由 `sherpa-onnx` 引擎直接加载调用。

## 提议的变更步骤

### 第一步：环境与依赖清理
移除沉重的深度学习框架，迎接轻量级运行时。

#### [MODIFY] requirements.txt
*   **移除**: `funasr`, `torch`, `torchaudio` (如果其他模块不需要用到 PyTorch 的话)。
*   **新增**: 
    *   `sherpa-onnx>=1.10.0` (负责加载 VAD 和 SenseVoice_Small)。
    *   `onnxruntime` (负责加载 WeSpeaker 进行矩阵计算)。

### 第二步：模型下载与配置更新
准备 ONNX 模型文件并更新配置项。

#### [NEW] 模型存放目录
您需要在项目中建立一个目录（例如 `data/models/`）来存放下载好的三个 ONNX 模型：
1.  `silero_vad.onnx`
2.  `sense-voice-small.onnx`
3.  `wespeaker_resnet34.onnx`

#### [MODIFY] src/config/config.py
*   将之前的 FunASR 模型名称配置更改为上述三个 `.onnx` 文件的绝对或相对路径。

### 第三步：重构核心处理器代码
抛弃现有的 [asr_processor.py](file:///c:/Users/morph/funasr/src/module/asr/asr_processor.py) 中基于 `AutoModel` 的逻辑，使用更干净的调用方式。

#### [MODIFY] src/module/vad/vad_core.py
*   不再使用 `AutoModel(model="fsmn-vad")`。
*   改为初始化 `sherpa_onnx.VoiceActivityDetector`，挂载 `silero_vad.onnx` 模型。

#### [MODIFY] src/module/asr/asr_processor.py
*   **模块一：声纹提取引擎 (WeSpeaker ONNX)**
    *   在类初始化时，加载 `onnxruntime.InferenceSession("wespeaker_resnet34.onnx")`。
    *   实现 `extract_speaker_embedding(audio_chunk)`: 接收从 VAD 切出来的 numpy 数组，送入 `session.run()` 返回 256 维向量。
*   **模块二：ASR 识别引擎 (SenseVoice Small ONNX)**
    *   在类初始化时，使用 `sherpa_onnx.OfflineRecognizer` 加载 `sense-voice-small.onnx` 文件。
*   **模块三：组装流水线含兜底逻辑验证**
    *   拿到 VAD 音频 -> 取声纹特征 -> 验证相似度。
        *   -> (是目标) -> 调 `recognizer.decode_stream` -> 只输出文字。
        *   -> (不是目标) -> 调 `recognizer.decode_stream` -> 标记为背景音。

## 验证计划

1.  **环境精简验证**：在彻底干净的虚拟环境里仅通过 `pip install sherpa-onnx onnxruntime` 确认项目可以正常启动运行。
2.  **极速流式验证**：播放嘈杂的多人测试音频，观察日志时间戳，确认每次 VAD 抛出片段后，（计算身纹 + 识别）的总耗时是否在百毫秒级别内完成，确保不堵塞队列。
3.  **兜底逻辑验证**：播放未注册人声的音频，确保系统打上了识别出来的文字但做出了拒绝/丢弃的处理。
