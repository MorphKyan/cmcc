#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能开关模块 - 通过环境变量控制可选功能的启用。

支持的功能开关：
- ENABLE_MIC_INPUT: 启用本地麦克风输入（需要 pyaudio）
- ENABLE_OLLAMA: 启用 Ollama 本地服务支持（需要 langchain-ollama）
"""

import os
from functools import lru_cache
from loguru import logger


class FeatureFlags:
    """功能开关管理器，通过环境变量控制可选功能。"""

    @staticmethod
    @lru_cache(maxsize=1)
    def is_mic_input_enabled() -> bool:
        """检查是否启用本地麦克风输入功能。
        
        Returns:
            bool: 如果 ENABLE_MIC_INPUT 环境变量设置为 "true" 则返回 True
        """
        enabled = os.getenv("ENABLE_MIC_INPUT", "false").lower() == "true"
        if enabled:
            logger.info("功能开关: 本地麦克风输入已启用")
        return enabled

    @staticmethod
    @lru_cache(maxsize=1)
    def is_ollama_enabled() -> bool:
        """检查是否启用 Ollama 支持。
        
        Returns:
            bool: 如果 ENABLE_OLLAMA 环境变量设置为 "true" 则返回 True
        """
        enabled = os.getenv("ENABLE_OLLAMA", "false").lower() == "true"
        if enabled:
            logger.info("功能开关: Ollama 支持已启用")
        return enabled

    @staticmethod
    def check_ollama_available() -> bool:
        """检查 Ollama 依赖是否可用。
        
        Returns:
            bool: 如果 langchain-ollama 已安装则返回 True
        """
        try:
            import langchain_ollama  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def check_mic_input_available() -> bool:
        """检查麦克风输入依赖是否可用。
        
        Returns:
            bool: 如果 pyaudio 已安装则返回 True
        """
        try:
            import pyaudio  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def validate_ollama_config() -> None:
        """验证 Ollama 配置是否有效。
        
        Raises:
            RuntimeError: 如果配置为使用 Ollama 但环境变量未启用或依赖未安装
        """
        if not FeatureFlags.is_ollama_enabled():
            raise RuntimeError(
                "Ollama 被配置为 provider 但 ENABLE_OLLAMA 环境变量未设置为 'true'。"
                "请设置环境变量: ENABLE_OLLAMA=true"
            )
        if not FeatureFlags.check_ollama_available():
            raise RuntimeError(
                "Ollama 被配置为 provider 但 langchain-ollama 未安装。"
                "请安装依赖: pip install langchain-ollama"
            )

    @staticmethod
    def log_feature_status() -> None:
        """记录所有功能开关的状态。"""
        logger.info("=== 功能开关状态 ===")
        logger.info(f"  本地麦克风输入 (ENABLE_MIC_INPUT): {FeatureFlags.is_mic_input_enabled()}")
        logger.info(f"  Ollama 支持 (ENABLE_OLLAMA): {FeatureFlags.is_ollama_enabled()}")
        logger.info(f"  pyaudio 可用: {FeatureFlags.check_mic_input_available()}")
        logger.info(f"  langchain-ollama 可用: {FeatureFlags.check_ollama_available()}")
        logger.info("=====================")
