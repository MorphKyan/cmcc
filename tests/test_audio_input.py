#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import unittest
import numpy as np
import soundfile as sf
import time

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.module.input.audio_input import AudioInputer
from src.config.config import FORMAT, CHANNELS, RATE


class TestAudioInputHandler(unittest.TestCase):
    """AudioInputHandler测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.audio_handler = AudioInputer()
        
    def tearDown(self):
        """测试后的清理工作"""
        # 确保音频流被正确关闭
        if hasattr(self, 'audio_handler') and self.audio_handler.stream is not None:
            self.audio_handler.stop()
    
    def test_initialization(self):
        """测试AudioInputHandler的初始化"""
        self.assertIsInstance(self.audio_handler, AudioInputer)
        self.assertIsNotNone(self.audio_handler.audio_queue)
        # 注意：此时stream应该还是None，因为还没有调用init_audio_stream
        
    def test_init_audio_stream(self):
        """测试音频流的初始化"""
        # 检查流是否已创建
        self.assertIsNotNone(self.audio_handler.stream)
        
        # 检查流的参数是否正确
        self.assertEqual(self.audio_handler.stream._format, FORMAT)
        self.assertEqual(self.audio_handler.stream._channels, CHANNELS)
        self.assertEqual(self.audio_handler.stream._rate, RATE)
        
    def test_audio_capture_and_save(self):
        """测试音频捕获并保存到文件"""
        # 启动音频流
        self.audio_handler.start()
        
        # 等待一段时间以捕获音频数据（例如5秒）
        print("请在接下来的5秒内对着麦克风说话...")
        capture_duration = 5  # 秒
        start_time = time.time()
        
        # 收集音频数据
        audio_data = []
        while time.time() - start_time < capture_duration:
            try:
                # 从队列中获取音频数据，设置超时以避免无限等待
                data = self.audio_handler.get_audio_data(timeout=1.0)
                audio_data.append(data)
            except:
                # 如果超时，继续循环直到达到捕获时间
                continue
        
        # 停止音频流
        self.audio_handler.stop()
        
        # 检查是否捕获到了音频数据
        self.assertGreater(len(audio_data), 0, "应该捕获到音频数据")
        
        # 将音频数据保存到文件
        output_file = "test_audio_output.wav"
        
        # 将字节数据转换为numpy数组
        # 首先连接所有字节数据
        audio_bytes = b''.join(audio_data)
        
        # 根据FORMAT转换为numpy数组
        if FORMAT == 8:  # pyaudio.paInt16
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        else:
            # 默认假设是浮点格式
            audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
        
        # 重塑数组以匹配声道数
        audio_array = audio_array.reshape(-1, CHANNELS)
        
        # 保存到WAV文件
        sf.write(output_file, audio_array, RATE)
        
        # 验证文件是否创建
        self.assertTrue(os.path.exists(output_file), "音频文件应该被创建")
        
        # 验证文件是否包含数据
        file_size = os.path.getsize(output_file)
        self.assertGreater(file_size, 44, "音频文件应该包含数据（大于44字节的WAV头部）")
        
        # 清理：删除测试文件
        # if os.path.exists(output_file):
            # os.remove(output_file)
            
    def test_get_audio_data(self):
        """测试获取音频数据"""
        # 启动音频流
        self.audio_handler.start()
        
        # 等待一小段时间以确保音频流开始工作
        time.sleep(0.1)
        
        # 尝试获取音频数据（非阻塞）
        try:
            # 这里我们不等待太久，因为可能没有音频输入
            data = self.audio_handler.get_audio_data(timeout=0.1)
            # 如果获取到数据，检查数据类型
            self.assertIsInstance(data, bytes)
        except:
            # 如果没有获取到数据，这是可以接受的（可能没有音频输入）
            pass
        
        # 停止音频流
        self.audio_handler.stop()

if __name__ == '__main__':
    unittest.main()
