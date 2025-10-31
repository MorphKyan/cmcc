#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import queue
import threading
from typing import Any, Optional

import websockets


class WebSocketInput:
    """
    通过WebSocket接收音频输入的类
    """

    def __init__(self, host: str = "localhost", port: int = 8765) -> None:
        """
        初始化WebSocket音频输入处理器
        
        Args:
            host: WebSocket服务器主机地址
            port: WebSocket服务器端口
        """
        self.host: str = host
        self.port: int = port
        self.thread = None
        self.audio_queue = queue.Queue()
        self.server = None
        self.running = False
        self.clients = set()

    async def _handle_client(self, websocket: Any, path: str) -> None:
        """
        处理客户端连接
        
        Args:
            websocket: WebSocket连接对象
            path: 请求路径
        """
        # 添加客户端到集合
        self.clients.add(websocket)
        print(f"新客户端连接: {websocket.remote_address}")

        try:
            async for message in websocket:
                # 检查消息类型
                if isinstance(message, bytes):
                    # 音频数据（二进制）
                    self.audio_queue.put(message)
                else:
                    # 控制消息（文本）
                    try:
                        control_msg = json.loads(message)
                        if control_msg.get('type') == 'ping':
                            await websocket.send(json.dumps({'type': 'pong'}))
                    except json.JSONDecodeError:
                        print(f"无法解析控制消息: {message}")
        except websockets.exceptions.ConnectionClosed:
            print(f"客户端断开连接: {websocket.remote_address}")
        finally:
            # 从集合中移除客户端
            self.clients.remove(websocket)

    async def _start_server(self) -> None:
        """启动WebSocket服务器"""
        self.server = await websockets.serve(self._handle_client, self.host, self.port)
        print(f"WebSocket服务器启动: {self.host}:{self.port}")

        # 保持服务器运行
        await self.server.wait_closed()

    def start(self) -> None:
        """启动WebSocket服务器"""
        if not self.running:
            self.running = True
            # 在新线程中运行事件循环
            self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
            self.thread.start()

    def _run_event_loop(self) -> None:
        """在新线程中运行事件循环"""
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 运行服务器
        loop.run_until_complete(self._start_server())

    def stop(self) -> None:
        """停止WebSocket服务器"""
        if self.running:
            self.running = False
            if self.server:
                self.server.close()

    def get_audio_data(self, timeout: Optional[float] = None) -> bytes:
        """
        从音频队列中获取数据
        
        Args:
            timeout: 超时时间（秒），None表示无限等待
            
        Returns:
            音频数据
            
        Raises:
            queue.Empty: 如果在指定的超时时间内没有数据
        """
        return self.audio_queue.get(timeout=timeout)

    def is_running(self) -> bool:
        """检查服务器是否正在运行"""
        return self.running
