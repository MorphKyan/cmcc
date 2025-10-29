import os
import queue
import threading
from typing import Optional

import av
import numpy as np
from av.audio.resampler import AudioResampler


class StreamDecoder:
    """
    它在一个单独的线程中运行 PyAV 解码器，通过 os.pipe 从主线程接收
    编码后的音频数据块，并将解码后的 PCM 数据放入一个线程安全的队列中。
    """

    def __init__(self, target_sample_rate: int = 16000, target_layout: str = "mono", target_format: str = "fltp"):
        """
        初始化解码器。

        :param target_sample_rate: 目标输出采样率。
        :param target_layout: 目标输出声道布局 (例如, "mono", "stereo")。
        :param target_format: 目标输出样本格式 (例如, "s16", "fltp")。
        """
        self.target_sample_rate = target_sample_rate
        self.target_layout = target_layout
        self.target_format = target_format

        # 1. 创建内存管道用于线程间通信
        r_pipe, w_pipe = os.pipe()
        self._r_pipe_file = os.fdopen(r_pipe, 'rb')
        self._w_pipe_file = os.fdopen(w_pipe, 'wb')

        # 2. 存放解码后 PCM 数据的队列
        self.output_queue = queue.Queue()

        # 3. 线程控制信号
        self._stop_event = threading.Event()

        # 4. 初始化并启动解码线程
        self._decoder_thread = threading.Thread(target=self._run_decoder, daemon=True)
        self._decoder_thread.start()

    def _run_decoder(self):
        """
        解码器线程的主循环。该方法不应被外部直接调用。
        """
        resampler = None
        try:
            with av.open(self._r_pipe_file, mode='r') as container:
                audio_stream = container.streams.audio[0]

                resampler = AudioResampler(
                    format=self.target_format,
                    layout=self.target_layout,
                    rate=self.target_sample_rate
                )

                # 当 stop_event 被设置或流结束时，循环终止
                while not self._stop_event.is_set():
                    try:
                        # container.decode 是一个生成器，会阻塞直到有足够的数据解码一帧
                        frame = next(container.decode(audio_stream))
                        resampled_frames = resampler.resample(frame)
                        for resampled_frame in resampled_frames:
                            self.output_queue.put(resampled_frame.to_ndarray())
                    except StopIteration:
                        # 流结束，正常退出
                        break
                    except Exception as e:
                        print(f"解码循环中发生错误: {e}")
                        break

                # 冲洗重采样器的内部缓冲区
                if resampler:
                    flushed_frames = resampler.resample(None)
                    for frame in flushed_frames:
                        self.output_queue.put(frame.to_ndarray())

        except Exception as e:
            print(f"解码器线程启动失败: {e}")
        finally:
            self._r_pipe_file.close()

    def feed_data(self, data: bytes):
        """
        向解码器输送编码后的音频数据。

        :param data: 从 WebSocket 接收到的二进制音频块。
        """
        if not self._w_pipe_file.closed:
            try:
                self._w_pipe_file.write(data)
                self._w_pipe_file.flush()
            except Exception:
                # 管道可能在另一端被关闭，这是正常关闭流程的一部分
                pass

    def get_decoded_frame(self, block: bool = False, timeout: Optional[float] = None) -> Optional[np.ndarray]:
        """
        从输出队列中获取一个解码后的 PCM 数据帧。

        :param block: 是否阻塞等待，直到有可用的帧。
        :param timeout: 阻塞等待的超时时间（秒）。
        :return: 一个包含 PCM 数据的 NumPy 数组，或在队列为空时返回 None。
        """
        try:
            return self.output_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def close(self):
        """
        优雅地关闭解码器，停止线程并清理资源。
        """
        if not self._stop_event.is_set():
            self._stop_event.set()

        if not self._w_pipe_file.closed:
            self._w_pipe_file.close()

        # 等待解码线程结束
        self._decoder_thread.join(timeout=2.0)
        if self._decoder_thread.is_alive():
            print("警告: 解码器线程在超时后仍未结束。")
