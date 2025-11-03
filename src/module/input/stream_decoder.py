import asyncio
import io
import subprocess
import threading
import queue
from typing import List, Optional

import av
import numpy as np
from av.audio.resampler import AudioResampler
from loguru import logger


class StreamDecoder:
    def __init__(self, target_sample_rate: int = 16000, target_layout: str = "mono", target_format: str = "fltp") -> None:
        """
        初始化解码器和重采样器。

        :param target_sample_rate: 目标输出采样率 (Hz)。
        :param target_layout: 目标输出声道布局 (例如, "mono", "stereo")。
        :param target_format: 目标输出样本格式 (例如, "s16" for int16, "fltp" for float32)。
                               'fltp' (planar float) 通常是音频处理的首选。
        """
        self.resampler = AudioResampler(
            format=target_format,
            layout=target_layout,
            rate=target_sample_rate
        )

    def _decode_and_resample_sync(self, encoded_chunk: bytes) -> List[np.ndarray]:
        """
        【同步方法】在一个数据块上执行实际的解码和重采样。
        这个方法会被 `asyncio.to_thread` 在一个独立的线程中运行。
        """
        decoded_frames = []
        try:
            # 使用 BytesIO 将内存中的 bytes 数据模拟成一个文件
            with av.open(io.BytesIO(encoded_chunk), mode='r') as container:
                audio_stream = container.streams.audio[0]

                for frame in container.decode(audio_stream):
                    # 重采样帧以匹配目标格式
                    resampled_frames = self.resampler.resample(frame)
                    for resampled_frame in resampled_frames:
                        # 将 AudioFrame 转换为 NumPy 数组并添加到列表中
                        decoded_frames.append(resampled_frame.to_ndarray())

        except Exception:
            # 使用 logger.exception 可以自动记录堆栈信息
            logger.exception("解码或重采样音频块时发生错误")
            return []  # 发生错误时返回空列表

        return decoded_frames

    async def decode_chunk(self, encoded_chunk: bytes) -> Optional[np.ndarray]:
        frames = await asyncio.to_thread(self._decode_and_resample_sync, encoded_chunk)

        if not frames:
            return None

        # 将从一个块解码出的所有帧拼接成一个大的 NumPy 数组
        # axis=1 表示沿着样本维度拼接
        return np.concatenate(frames, axis=1)


class FFmpegStreamDecoder:
    def __init__(self, target_sample_rate: int = 16000, target_layout: str = "mono", target_format: str = "fltp") -> None:
        """
        初始化FFmpeg流式解码器。

        :param target_sample_rate: 目标输出采样率 (Hz)。
        :param target_layout: 目标输出声道布局 (例如, "mono", "stereo")。
        :param target_format: 目标输出样本格式 (例如, "s16" for int16, "fltp" for float32)。
        """
        self.target_sample_rate = target_sample_rate
        self.target_channels = 1 if target_layout == "mono" else 2
        self.target_format = target_format
        
        # 确定输出格式
        if target_format == "fltp":
            self.output_format = "f32le"  # 32-bit float little-endian
        elif target_format == "s16":
            self.output_format = "s16le"  # 16-bit signed integer little-endian
        else:
            self.output_format = "f32le"  # 默认使用float32
            
        # 流式处理相关的属性
        self._ffmpeg_process: Optional[subprocess.Popen] = None
        self._is_initialized = False
        self._stdout_queue: Optional[queue.Queue] = None
        self._stdout_thread: Optional[threading.Thread] = None

    def _initialize_ffmpeg_process(self) -> bool:
        """初始化FFmpeg进程用于流式处理"""
        if self._ffmpeg_process is not None and self._ffmpeg_process.poll() is None:
            # 进程已经在运行
            return True
            
        try:
            # 构建FFmpeg命令 - 使用流式输入
            cmd = [
                'ffmpeg',
                '-hide_banner',
                '-loglevel', 'warning',  # 降低日志级别以减少输出
                '-f', 'webm',  # 输入格式
                '-probesize', '32768',  # 减少探测大小以加快启动
                '-analyzeduration', '0',  # 不分析持续时间
                '-i', 'pipe:0',  # 从stdin读取
                '-f', self.output_format,  # 输出格式
                '-ar', str(self.target_sample_rate),  # 采样率
                '-ac', str(self.target_channels),  # 声道数
                '-acodec', 'pcm_' + self.output_format,  # PCM编码
                '-fflags', 'nobuffer',  # 减少缓冲
                '-flags', 'low_delay',  # 低延迟模式
                '-flush_packets', '1',  # 立即刷新包
                'pipe:1'  # 输出到stdout
            ]
            
            self._ffmpeg_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0  # 无缓冲
            )
            
            # 初始化队列和读取线程
            self._stdout_queue = queue.Queue()
            self._stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
            self._stdout_thread.start()
            
            self._is_initialized = True
            logger.info("FFmpeg流式解码器已初始化")
            return True
            
        except Exception as e:
            logger.exception(f"初始化FFmpeg进程失败: {e}")
            self._cleanup_process()
            return False

    def _read_stdout(self):
        """从FFmpeg stdout读取数据并放入队列"""
        try:
            if self._ffmpeg_process and self._ffmpeg_process.stdout:
                while True:
                    # 检查进程是否还在运行
                    if self._ffmpeg_process.poll() is not None:
                        break
                    chunk = self._ffmpeg_process.stdout.read(4096)
                    if not chunk:
                        break
                    if self._stdout_queue:
                        self._stdout_queue.put(chunk)
        except Exception as e:
            # 检查是否是因为进程已经结束
            if self._ffmpeg_process and self._ffmpeg_process.poll() is None:
                logger.warning(f"读取FFmpeg stdout时发生错误: {e}")
        finally:
            # 确保队列中有结束标记
            if self._stdout_queue:
                self._stdout_queue.put(None)

    def _cleanup_process(self):
        """清理FFmpeg进程"""
        if self._ffmpeg_process is not None:
            try:
                if self._ffmpeg_process.stdin:
                    self._ffmpeg_process.stdin.close()
                if self._ffmpeg_process.stdout:
                    self._ffmpeg_process.stdout.close()
                if self._ffmpeg_process.stderr:
                    self._ffmpeg_process.stderr.close()
                self._ffmpeg_process.terminate()
                self._ffmpeg_process.wait(timeout=2)
            except Exception as e:
                logger.warning(f"清理FFmpeg进程时发生警告: {e}")
                try:
                    self._ffmpeg_process.kill()
                except:
                    pass
            finally:
                self._ffmpeg_process = None
                self._is_initialized = False
                # 清空队列
                if self._stdout_queue:
                    while not self._stdout_queue.empty():
                        try:
                            self._stdout_queue.get_nowait()
                        except queue.Empty:
                            break
                self._stdout_queue = None
                self._stdout_thread = None

    def _decode_stream_sync(self, encoded_chunk: bytes) -> Optional[np.ndarray]:
        """
        【同步方法】向流式FFmpeg进程写入数据并读取输出。
        这个方法会被 `asyncio.to_thread` 在一个独立的线程中运行。
        """
        if not encoded_chunk:
            return None
            
        if not self._initialize_ffmpeg_process():
            return None
            
        try:
            # 写入数据到FFmpeg stdin
            if self._ffmpeg_process.stdin is not None:
                self._ffmpeg_process.stdin.write(encoded_chunk)
                self._ffmpeg_process.stdin.flush()
            
            # 从队列中读取可用的数据（非阻塞）
            output_data = b''
            if self._stdout_queue is not None:
                try:
                    # 尝试从队列中获取数据，设置短超时
                    while True:
                        try:
                            chunk = self._stdout_queue.get(timeout=0.01)  # 10ms超时
                            if chunk is None:
                                # FFmpeg进程已结束
                                break
                            output_data += chunk
                        except queue.Empty:
                            # 队列为空，没有更多数据
                            break
                except Exception as e:
                    logger.warning(f"从stdout队列读取数据时发生错误: {e}")
            
            if not output_data:
                # 可能还没有输出数据，这是正常的
                return None
                
            # 根据输出格式转换为NumPy数组
            if self.output_format == "f32le":
                audio_data = np.frombuffer(output_data, dtype=np.float32)
            elif self.output_format == "s16le":
                audio_data = np.frombuffer(output_data, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                audio_data = np.frombuffer(output_data, dtype=np.float32)
                
            # 重塑数组形状 (声道数, 样本数)
            if len(audio_data) % self.target_channels != 0:
                # 数据不完整，截断到最后一个完整样本
                valid_samples = (len(audio_data) // self.target_channels) * self.target_channels
                audio_data = audio_data[:valid_samples]
                
            if self.target_channels == 1:
                audio_data = audio_data.reshape(1, -1)
            else:
                audio_data = audio_data.reshape(self.target_channels, -1)
                
            return audio_data
            
        except Exception as e:
            logger.exception(f"FFmpeg流式解码时发生错误: {e}")
            self._cleanup_process()
            return None

    async def decode_chunk(self, encoded_chunk: bytes) -> Optional[np.ndarray]:
        """
        异步解码音频块（流式处理）。
        
        :param encoded_chunk: WebM格式的编码音频数据
        :return: 解码后的音频数据NumPy数组，形状为 (channels, samples)，如果暂时没有输出则返回None
        """
        if not encoded_chunk:
            return None
            
        audio_data = await asyncio.to_thread(self._decode_stream_sync, encoded_chunk)
        return audio_data

    async def close(self):
        """关闭解码器并清理资源"""
        await asyncio.to_thread(self._cleanup_process)
