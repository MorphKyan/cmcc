#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流式WebM解码器测试用例
"""

import os
import tempfile
import unittest
import logging
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)

# 导入解码器
from streaming_webm_decoder import StreamingWebMDecoder


class TestStreamingWebMDecoder(unittest.TestCase):
    """流式WebM解码器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.decoder = StreamingWebMDecoder()
        self.test_webm_file = self._create_test_webm_file()
        
    def tearDown(self):
        """测试后清理"""
        self.decoder.reset()
        if os.path.exists(self.test_webm_file):
            os.remove(self.test_webm_file)
            
    def _create_test_webm_file(self):
        """
        创建测试用例WebM文件
        由于无法在测试中生成真实的WebM文件，
        我们将使用一个简单的策略来验证解码器逻辑
        """
        # 创建一个临时文件用于测试
        temp_file = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
        temp_file.close()
        
        # 由于我们无法在纯Python中生成WebM文件，
        # 我们将模拟WebM数据的结构进行测试
        return temp_file.name
        
    def test_webm_header_detection(self):
        """测试WebM header检测"""
        # WebM EBML header: 0x1A 0x45 0xDF 0xA3
        webm_header = b'\x1a\x45\xdf\xa3' + b'\x00' * 100
        self.assertTrue(self.decoder._detect_webm_header_end(webm_header) > 0)
        
    def test_feed_data(self):
        """测试数据喂入功能"""
        test_data = b'\x00' * 1024
        result = self.decoder.feed_data(test_data)
        self.assertTrue(result)
        self.assertEqual(self.decoder.total_bytes_received, 1024)
        
    def test_buffer_management(self):
        """测试缓冲区管理"""
        # 喂入多块数据
        for i in range(5):
            self.decoder.feed_data(b'\x00' * 1024)
            
        self.assertEqual(self.decoder.get_buffer_size(), 5120)
        
    def test_decoder_initialization(self):
        """测试解码器初始化"""
        self.assertIsNotNone(self.decoder.resampler)
        
    def test_edge_cases(self):
        """测试边界情况"""
        # 空数据
        self.assertFalse(self.decoder.feed_data(b''))
        
        # None数据（虽然类型提示不允许，但测试一下）
        with self.assertRaises(TypeError):
            self.decoder.feed_data(None)
            
    def manual_test_with_real_webm(self, webm_file_path):
        """
        手动测试函数 - 使用真实的WebM文件
        这个测试需要用户提供真实的WebM文件路径
        """
        if not os.path.exists(webm_file_path):
            print(f"测试文件不存在: {webm_file_path}")
            return
            
        print(f"使用真实WebM文件测试: {webm_file_path}")
        
        # 读取完整文件
        with open(webm_file_path, 'rb') as f:
            full_data = f.read()
            
        # 模拟流式传输：分块喂入
        chunk_size = 1024
        decoder = StreamingWebMDecoder()
        
        total_decoded = 0
        for i in range(0, len(full_data), chunk_size):
            chunk = full_data[i:i+chunk_size]
            decoder.feed_data(chunk)
            
            # 尝试解码
            decoded_audio = decoder.get_decoded_audio()
            if decoded_audio is not None:
                print(f"解码成功 - 形状: {decoded_audio.shape}, 类型: {decoded_audio.dtype}")
                total_decoded += decoded_audio.size
                
        print(f"总计解码样本数: {total_decoded}")
        
        # 重置并一次性解码完整文件进行对比
        decoder.reset()
        decoder.feed_data(full_data)
        full_decoded = decoder.get_decoded_audio()
        if full_decoded is not None:
            print(f"完整文件解码 - 形状: {full_decoded.shape}")
            
        return total_decoded > 0


def create_sample_webm():
    """
    创建示例WebM文件的辅助函数
    需要ffmpeg或其他工具
    """
    try:
        import subprocess
        # 创建一个简单的音频文件并转换为WebM
        # 这需要系统安装ffmpeg
        test_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        test_wav.close()
        
        # 使用ffmpeg生成测试文件（如果可用）
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=3',
            '-c:a', 'libopus', test_wav.name.replace('.wav', '.webm')
        ], capture_output=True)
        
        return test_wav.name.replace('.wav', '.webm')
    except Exception as e:
        print(f"无法创建测试WebM文件: {e}")
        return None


if __name__ == '__main__':
    # 运行单元测试
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 如果有真实的WebM文件，可以取消注释下面的代码进行手动测试
    # test_file = "path/to/your/test.webm"  # 替换为实际文件路径
    # decoder_test = TestStreamingWebMDecoder()
    # success = decoder_test.manual_test_with_real_webm(test_file)
    # print(f"手动测试结果: {'成功' if success else '失败'}")