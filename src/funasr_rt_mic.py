import pyaudio
import threading
import queue
import numpy as np
from funasr import AutoModel

# --- 配置 ---
# 语音识别模型配置
asr_model_name = "paraformer-zh-streaming"
# FunASR流式参数
asr_chunk_size = [0, 10, 5]  # 600ms
asr_chunk_stride = asr_chunk_size[1] * 960
encoder_chunk_look_back = 4
decoder_chunk_look_back = 1

# VAD模型配置
vad_model_name = "fsmn-vad"
vad_chunk_size = 200  # ms
vad_chunk_stride = int(vad_chunk_size * 16000 / 1000)  # 对于16kHz采样率

# PyAudio音频流配置
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
# 每次从麦克风读取的音频帧数，使用VAD的步长
PYAUDIO_CHUNK_SIZE = vad_chunk_stride

# --- 全局变量 ---
# 音频队列用于VAD处理
vad_audio_queue = queue.Queue()
# 音频队列用于ASR处理
asr_audio_queue = queue.Queue()
is_recording = True
# 用于存储当前语音片段的缓冲区
speech_buffer = []
# VAD状态
vad_state = "silence"  # "silence" 或 "speech"
speech_start_time = 0
speech_end_time = 0

# --- 音频采集线程 ---
def audio_capture_thread():
    """
    从麦克风捕获音频并放入队列。
    """
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=PYAUDIO_CHUNK_SIZE)
        print("麦克风已开启，请开始说话...")
        while is_recording:
            data = stream.read(PYAUDIO_CHUNK_SIZE)
            vad_audio_queue.put(data)
    except Exception as e:
        print(f"音频捕获出错: {e}")
    finally:
        print("音频捕获线程正在停止...")
        if 'stream' in locals() and stream.is_active():
            stream.stop_stream()
            stream.close()
        p.terminate()
        print("音频捕获线程已停止。")


# --- VAD处理线程 ---
def vad_thread():
    """
    从队列中获取音频数据并进行端点检测。
    """
    global speech_buffer, vad_state, speech_start_time, speech_end_time
    
    print("正在加载VAD模型...")
    try:
        vad_model = AutoModel(model=vad_model_name)
        print("VAD模型加载完毕。")
    except Exception as e:
        print(f"加载VAD模型失败: {e}")
        return

    vad_cache = {}
    chunk_count = 0
    while is_recording or not vad_audio_queue.empty():
        try:
            # 从队列中获取音频数据，设置超时以避免永久阻塞
            audio_chunk_bytes = vad_audio_queue.get(timeout=1)
            chunk_count += 1

            # 将字节数据转换为numpy数组
            audio_int16 = np.frombuffer(audio_chunk_bytes, dtype=np.int16)
            # 转换为模型所需的float32格式
            audio_float32 = audio_int16.astype(np.float32) / 32768.0

            # 送入VAD模型进行检测
            vad_res = vad_model.generate(
                input=audio_float32,
                cache=vad_cache,
                is_final=False,
                chunk_size=vad_chunk_size
            )
            
            # 处理VAD返回结果
            if isinstance(vad_res, list) and len(vad_res) > 0:
                vad_result_item = vad_res[0]
            else:
                vad_result_item = vad_res

            # 检查是否有语音活动检测结果
            if vad_result_item and 'value' in vad_result_item and len(vad_result_item['value']) > 0:
                # value是一个包含[开始时间, 结束时间]的列表
                for segment in vad_result_item['value']:
                    start_time, end_time = segment
                    print(f"检测到语音活动: {start_time} - {end_time} (ms)")
                    
                    # 简单的状态机来处理语音活动
                    if vad_state == "silence":
                        # 从静默状态进入语音状态
                        vad_state = "speech"
                        speech_buffer = [audio_chunk_bytes]  # 开始新的语音片段
                        speech_start_time = chunk_count * vad_chunk_size - vad_chunk_size + start_time
                        print(f"开始语音片段，起始时间: {speech_start_time} ms")
                    elif vad_state == "speech":
                        # 继续语音状态
                        speech_buffer.append(audio_chunk_bytes)
                        
                    # 检查是否是语音结束
                    if end_time < vad_chunk_size:  # 如果结束时间在当前块内，说明语音结束了
                        if vad_state == "speech":
                            vad_state = "silence"
                            # 将完整的语音片段放入ASR队列
                            asr_audio_queue.put(b''.join(speech_buffer))
                            speech_buffer = []
                            speech_end_time = chunk_count * vad_chunk_size - vad_chunk_size + end_time
                            print(f"结束语音片段，结束时间: {speech_end_time} ms")
            else:
                # 没有检测到语音活动
                if vad_state == "speech":
                    # 在语音状态下，如果没有检测到活动，我们可能需要等待一段时间再判断是否结束
                    # 这里简化处理，直接认为语音结束了
                    vad_state = "silence"
                    # 将当前缓冲的语音片段放入ASR队列
                    if speech_buffer:
                        asr_audio_queue.put(b''.join(speech_buffer))
                        speech_buffer = []
                        speech_end_time = chunk_count * vad_chunk_size
                        print(f"结束语音片段(无活动)，结束时间: {speech_end_time} ms")
                elif vad_state == "silence":
                    # 保持静默状态
                    pass

        except queue.Empty:
            # 如果队列为空，短暂等待后继续，直到录音停止
            continue
        except Exception as e:
            print(f"\nVAD处理过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            break
    print("\nVAD线程已停止。")


# --- 语音识别线程 ---
def asr_thread():
    """
    从队列中获取完整的语音片段并进行识别。
    """
    print("正在加载语音识别模型...")
    try:
        asr_model = AutoModel(model=asr_model_name)
        print("ASR模型加载完毕。")
    except Exception as e:
        print(f"加载ASR模型失败: {e}")
        return

    asr_cache = {}
    while is_recording or not asr_audio_queue.empty():
        try:
            # 从队列中获取完整的语音片段，设置超时以避免永久阻塞
            speech_data_bytes = asr_audio_queue.get(timeout=1)

            # 将字节数据转换为numpy数组
            speech_int16 = np.frombuffer(speech_data_bytes, dtype=np.int16)
            # 转换为模型所需的float32格式
            speech_float32 = speech_int16.astype(np.float32) / 32768.0

            print("开始识别语音片段...")
            # 送入ASR模型进行识别
            asr_res = asr_model.generate(
                input=speech_float32,
                cache=asr_cache,
                is_final=True,  # 对于完整的语音片段，发送is_final=True
                chunk_size=asr_chunk_size,
                encoder_chunk_look_back=encoder_chunk_look_back,
                decoder_chunk_look_back=decoder_chunk_look_back
            )
            
            # 处理ASR返回结果
            if isinstance(asr_res, list) and len(asr_res) > 0:
                asr_result_item = asr_res[0]
            else:
                asr_result_item = asr_res

            # 提取文本
            if asr_result_item and 'text' in asr_result_item:
                print(f"识别结果: {asr_result_item['text']}")
            else:
                print("识别结果: (无)")

        except queue.Empty:
            # 如果队列为空，短暂等待后继续，直到录音停止
            continue
        except Exception as e:
            print(f"\nASR处理过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            break
    print("\nASR线程已停止。")


# --- 主函数 ---
if __name__ == "__main__":
    try:
        # 创建并启动线程
        capture = threading.Thread(target=audio_capture_thread)
        vad = threading.Thread(target=vad_thread)
        asr = threading.Thread(target=asr_thread)

        capture.start()
        vad.start()
        asr.start()

        # 等待用户输入来停止程序
        input("按 Enter 键停止录音...\n")

    finally:
        is_recording = False
        print("\n正在停止程序，请稍候...")
        # 等待线程结束
        if 'capture' in locals() and capture.is_alive():
            capture.join()
        if 'vad' in locals() and vad.is_alive():
            vad.join()
        if 'asr' in locals() and asr.is_alive():
            asr.join()
        print("程序已完全停止。")
