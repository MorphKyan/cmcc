import asyncio
import io
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
