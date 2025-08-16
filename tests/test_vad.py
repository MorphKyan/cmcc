#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import soundfile as sf

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.vad_processor import VADProcessor

# 测试配置常量
DEFAULT_CHUNK_SIZE = 200  # ms
DEFAULT_SAMPLE_RATE = 16000  # Hz
TEST_CHUNK_SIZE = 200  # ms
TEST_SAMPLE_RATE = 16000  # Hz

class VADTestSuite:
    """VAD处理器测试套件"""
    
    def __init__(self):
        """初始化测试套件"""
        self.vad_processor = None
        self.test_results = []
    
    def load_audio_file(self, audio_file_path: str) -> tuple:
        """加载音频文件
        
        Args:
            audio_file_path (str): 音频文件路径
            
        Returns:
            tuple: (speech_data, sample_rate) 或 (None, None) 如果加载失败
        """
        try:
            speech, sample_rate = sf.read(audio_file_path)
            print(f"音频文件加载成功: {sample_rate}Hz, {len(speech)} samples")
            return speech, sample_rate
        except Exception as e:
            print(f"加载音频文件失败: {e}")
            return None, None

    def get_model_example_file(self) -> str:
        """获取模型自带的示例音频文件路径
        
        Returns:
            str: 音频文件路径，如果未找到则返回None
        """
        try:
            from funasr import AutoModel
            model = AutoModel(model="fsmn-vad", model_revision="v2.0.4")
            model_path = model.model_path
            wav_file = f"{model_path}/example/vad_example.wav"
            return wav_file if os.path.exists(wav_file) else None
        except Exception as e:
            print(f"获取模型示例文件时出错: {e}")
            return None

    def process_speech_segments(self, speech_segments):
        """处理并输出语音段信息
        
        Args:
            speech_segments: 语音段列表，每个语音段包含开始时间、结束时间和音频数据
        """
        if speech_segments:
            print(f"检测到语音段: {len(speech_segments)} 个")
            for i, segment in enumerate(speech_segments):
                if isinstance(segment, (list, tuple)) and len(segment) >= 2:
                    print(f"段 {i+1}: 开始={segment[0]}ms, 结束={segment[1]}ms")
                else:
                    print(f"段 {i+1}: {segment}")
        else:
            print("未检测到语音段")

    def initialize_vad_processor(self, chunk_size: int = TEST_CHUNK_SIZE, sample_rate: int = TEST_SAMPLE_RATE) -> VADProcessor:
        """初始化VAD处理器（避免重复初始化）
        
        Args:
            chunk_size (int): 音频块大小（毫秒）
            sample_rate (int): 采样率
            
        Returns:
            VADProcessor: VAD处理器实例
        """
        if self.vad_processor is None:
            print("正在初始化VAD处理器...")
            self.vad_processor = VADProcessor(chunk_size=chunk_size, sample_rate=sample_rate)
        return self.vad_processor

    def test_vad_with_file(self, audio_file_path: str) -> bool:
        """使用音频文件测试VAD功能
        
        Args:
            audio_file_path (str): 音频文件路径
            
        Returns:
            bool: 测试是否成功
        """
        print(f"正在加载音频文件: {audio_file_path}")
        
        # 读取音频文件
        speech, sample_rate = self.load_audio_file(audio_file_path)
        if speech is None:
            return False
        
        # 初始化VAD处理器
        vad_processor = self.initialize_vad_processor(DEFAULT_CHUNK_SIZE, sample_rate)
        
        # 处理音频流
        print("正在处理音频流...")
        speech_segments = vad_processor.process_audio_stream(speech)
        
        # 输出结果
        self.process_speech_segments(speech_segments)
        return True

    def test_vad_with_model_example(self) -> bool:
        """使用模型自带的示例音频测试VAD功能
        
        Returns:
            bool: 测试是否成功
        """
        print("正在测试VAD模型自带的示例...")
        
        # 获取模型示例文件
        wav_file = self.get_model_example_file()
        if not wav_file:
            print("未找到模型示例音频文件")
            return False
        
        print(f"使用示例文件: {wav_file}")
        return self.test_vad_with_file(wav_file)

    def test_silent_audio_chunk(self) -> bool:
        """测试静音音频块
        
        Returns:
            bool: 测试是否通过
        """
        print("正在测试静音音频块...")
        
        # 初始化VAD处理器
        vad_processor = self.initialize_vad_processor()
        
        # 创建静音音频块
        chunk_size_samples = int(TEST_CHUNK_SIZE * TEST_SAMPLE_RATE / 1000)
        silent_chunk = np.zeros(chunk_size_samples, dtype=np.float32)
        
        # 处理静音块
        segments = vad_processor.process_audio_chunk(silent_chunk)
        
        if not segments:
            print("静音块测试通过: 未检测到语音段")
            return True
        else:
            print(f"静音块测试失败: 检测到 {len(segments)} 个语音段")
            return False

    def test_real_speech_chunk(self) -> bool:
        """测试真实语音块
        
        Returns:
            bool: 测试是否通过
        """
        print("正在测试真实语音块...")
        
        # 获取模型示例文件
        wav_file = self.get_model_example_file()
        if not wav_file:
            print("未找到模型示例音频文件，跳过真实语音块测试")
            return False
        
        # 加载音频文件
        speech, sr = self.load_audio_file(wav_file)
        if speech is None:
            return False
        
        # 初始化VAD处理器
        vad_processor = self.initialize_vad_processor()
        
        # 检查采样率是否匹配
        if sr != TEST_SAMPLE_RATE:
            print(f"警告: 示例音频采样率 ({sr}Hz) 与测试采样率 ({TEST_SAMPLE_RATE}Hz) 不同。")
        
        # 分块处理音频
        chunk_stride = int(TEST_CHUNK_SIZE * TEST_SAMPLE_RATE / 1000)
        total_chunk_num = (len(speech) + chunk_stride - 1) // chunk_stride
        
        found_speech = False
        vad_processor.reset_cache()  # 重置缓存以进行独立测试
        
        for i in range(total_chunk_num):
            speech_chunk = speech[i * chunk_stride:(i + 1) * chunk_stride]
            if len(speech_chunk) == 0:
                continue
            
            segments = vad_processor.process_audio_chunk(speech_chunk)
            if segments:
                found_speech = True
                # 提取时间信息用于显示
                segment_info = [(start, end) for start, end, _ in segments]
                print(f"在块 {i} 中检测到语音段: {segment_info}")
        
        if found_speech:
            print("真实语音块测试通过: 成功检测到语音段")
            return True
        else:
            print("真实语音块测试失败: 未检测到任何语音段")
            return False

    def test_empty_audio(self):
        """测试空音频"""
        print("正在测试空音频...")
        
        # 初始化VAD处理器
        vad_processor = self.initialize_vad_processor()
        
        # 创建空音频
        empty_audio = np.array([], dtype=np.float32)
        
        # 处理空音频
        segments = vad_processor.process_audio_stream(empty_audio)
        
        if not segments:
            print("空音频测试通过: 未检测到语音段")
            return True
        else:
            print(f"空音频测试失败: 检测到 {len(segments)} 个语音段")
            return False

    def test_short_audio(self):
        """测试短音频"""
        print("正在测试短音频...")
        
        # 初始化VAD处理器
        vad_processor = self.initialize_vad_processor()
        
        # 创建短音频（小于一个块）
        short_audio = np.random.rand(100).astype(np.float32)
        
        # 处理短音频
        segments = vad_processor.process_audio_stream(short_audio)
        
        print(f"短音频测试完成: 检测到 {len(segments)} 个语音段")
        return True  # 短音频测试只要不抛出异常就算通过

    def test_process_audio_chunk(self):
        """测试 process_audio_chunk 函数"""
        print("正在测试 process_audio_chunk 函数...")
        
        # 测试静音块
        silent_test_passed = self.test_silent_audio_chunk()
        
        # 测试真实语音块
        speech_test_passed = self.test_real_speech_chunk()
        
        return silent_test_passed and speech_test_passed

    def run_all_tests(self):
        """运行所有测试"""
        print("VAD功能测试")
        print("=" * 50)
        
        # 测试模型自带的示例
        model_test_passed = self.test_vad_with_model_example()
        
        print("\n" + "=" * 50)
        
        # 测试 process_audio_chunk 函数
        chunk_test_passed = self.test_process_audio_chunk()
        
        print("\n" + "=" * 50)
        
        # 测试边界条件
        print("正在测试边界条件...")
        empty_test_passed = self.test_empty_audio()
        short_test_passed = self.test_short_audio()
        boundary_test_passed = empty_test_passed and short_test_passed
        
        print("\n" + "=" * 50)
        
        # 如果提供了音频文件路径作为参数，则测试该文件
        file_test_passed = True
        if len(sys.argv) > 1:
            audio_file_path = sys.argv[1]
            print(f"测试指定音频文件: {audio_file_path}")
            file_test_passed = self.test_vad_with_file(audio_file_path)
        
        # 输出测试总结
        print("\n" + "=" * 50)
        print("测试总结:")
        print(f"  模型示例测试: {'通过' if model_test_passed else '失败'}")
        print(f"  音频块测试: {'通过' if chunk_test_passed else '失败'}")
        print(f"  边界条件测试: {'通过' if boundary_test_passed else '失败'}")
        print(f"  文件测试: {'通过' if file_test_passed else '失败'}")
        
        all_tests_passed = model_test_passed and chunk_test_passed and boundary_test_passed and file_test_passed
        print(f"  总体结果: {'通过' if all_tests_passed else '失败'}")
        
        return all_tests_passed

def main():
    """主函数"""
    test_suite = VADTestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
