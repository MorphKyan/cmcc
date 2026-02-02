#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.routers import audio
from src.api.routers import config
from src.api.routers import data
from src.api.routers import llm
from src.api.routers import rag
from src.api.routers import asr
from src.api.routers import vad
from src.api.routers import monitoring
from src.api.routers import tool
from src.api.routers import pipeline
from src.api.schemas import HealthResponse
from src.config.logging_config import setup_logging
from src.core.lifespan import lifespan

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

# Create a global API router with prefix /api
api_router = APIRouter(prefix="/api")

api_router.include_router(audio.router)
api_router.include_router(rag.router)
api_router.include_router(llm.router)
api_router.include_router(config.router)
api_router.include_router(data.router)
api_router.include_router(vad.router)
api_router.include_router(monitoring.router)
api_router.include_router(tool.router)
api_router.include_router(pipeline.router)
api_router.include_router(asr.router)

# Include the global API router into the app
app.include_router(api_router)


@api_router.get("/", tags=["Health"], response_model=HealthResponse)
async def root() -> HealthResponse:
    """API Root Health Check"""
    return HealthResponse(status="healthy", service="API Service")


# Include the global API router into the app
app.include_router(api_router)


@app.get("/")
async def app_root():
    """Redirect root to API docs or health"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


def run_api(host: str = '0.0.0.0', port: int = 8000) -> None:
    """运行API服务（HTTP模式，由nginx处理HTTPS终结）"""
    import uvicorn
    # 使用 log_config=None 让 uvicorn 不去重新配置日志，
    # 而是使用我们已经通过 setup_logging 配置好的 handlers (InterceptHandler)
    uvicorn.run(app, host=host, port=port, reload=False, log_config=None)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='API Service')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    args = parser.parse_args()

    logger.info("启动API服务: http://{host}:{port}", host=args.host, port=args.port)
    run_api(host=args.host, port=args.port)
