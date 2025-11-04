#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from typing import NoReturn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.core.lifespan import lifespan
from src.api.routers import audio
from src.api.routers import rag
from src.api.schemas import HealthResponse
from src.config.logging_config import setup_logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 初始化日志配置
setup_logging()

app = FastAPI(title="API Service", description="RESTful API for assistant", version="1.0.0", lifespan=lifespan)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio.router)
app.include_router(rag.router)


@app.get("/", tags=["Health"], response_model=HealthResponse)
async def root() -> HealthResponse:
    return HealthResponse(status="healthy", service="Main API Service")


def run_api(host: str = '0.0.0.0', port: int = 5000) -> None:
    """运行API服务"""
    import uvicorn
    uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='API Service')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    args = parser.parse_args()

    logger.info("启动API服务: http://{host}:{port}", host=args.host, port=args.port)
    run_api(host=args.host, port=args.port)
