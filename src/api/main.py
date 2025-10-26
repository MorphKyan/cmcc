#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
import sys
import threading
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.context import Context
from src.api.schemas import HealthResponse

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# 使用绝对导入而不是相对导入

app = FastAPI(title="API Service", description="RESTful API for assistant", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(status="healthy", service="RAG API Service")


async def process_audio_for_client(client_id: str):
    """
    为单个客户端处理音频队列中的数据。
    这是一个后台异步任务。
    """
    print(f"开始为客户端 {client_id} 处理音频...")
    context = active_contexts.get(client_id)
    if not context:
        print(f"错误：找不到客户端 {client_id} 的上下文。")
        return

    while True:
        try:
            # 从队列中获取音频数据
            # 这里是异步等待，不会阻塞整个服务
            audio_data = await context.audio_input_queue.get()

            # TODO: 在这里实现你的音频处理逻辑
            # 例如：语音识别 (ASR), 静音检测 (VAD) 等
            # 当前只是简单打印
            print(f"从客户端 {client_id} 收到 {len(audio_data)} 字节的音频数据。")

            # 处理完成后，标记任务完成
            context.audio_input_queue.task_done()

        except asyncio.CancelledError:
            # 当任务被取消时（例如客户端断开连接），退出循环
            print(f"客户端 {client_id} 的音频处理任务已取消。")
            break
        except Exception as e:
            print(f"处理客户端 {client_id} 的音频时出错: {e}")
            # 避免因单个错误导致整个任务崩溃
            await asyncio.sleep(1)


def run_api(host='0.0.0.0', port=5000):
    """运行API服务"""
    import uvicorn
    uvicorn.run("src.api.main:app", host=host, port=port, reload=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='API Service')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    args = parser.parse_args()

    print(f"启动API服务: http://{args.host}:{args.port}")
    run_api(host=args.host, port=args.port)
