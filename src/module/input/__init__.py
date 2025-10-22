#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频输入模块初始化文件
"""

from .audio_input import AudioInputer
from .websocket_input import WebSocketInput

# 定义音频输入类型常量
AUDIO_INPUT_TYPE_MIC = "mic"
AUDIO_INPUT_TYPE_WEBSOCKET = "websocket"

__all__ = ['AudioInputer', 'WebSocketInput', 'AUDIO_INPUT_TYPE_MIC', 'AUDIO_INPUT_TYPE_WEBSOCKET']