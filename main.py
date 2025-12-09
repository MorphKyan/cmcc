#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.routers import audio
from src.api.routers import config
from src.api.routers import data
from src.api.routers import llm
from src.api.routers import rag
from src.api.routers import vad
from src.api.routers import monitoring
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

app.include_router(audio.router)
app.include_router(rag.router)
app.include_router(llm.router)
app.include_router(config.router)
app.include_router(data.router)
app.include_router(vad.router)
app.include_router(monitoring.router)


@app.get("/", tags=["Health"], response_model=HealthResponse)
async def root() -> HealthResponse:
    return HealthResponse(status="healthy", service="Main API Service")


def run_api(host: str = '0.0.0.0', port: int = 5000, ssl_certfile: str = None, ssl_keyfile: str = None) -> None:
    """运行API服务"""
    import uvicorn

    # 配置SSL参数（如果提供）
    ssl_config = {}
    if ssl_certfile and ssl_keyfile:
        ssl_config = {
            "ssl_certfile": ssl_certfile,
            "ssl_keyfile": ssl_keyfile
        }
        logger.info("启用HTTPS/WSS支持")
    else:
        logger.info("使用HTTP/WS模式（未提供SSL证书）")

    uvicorn.run(app, host=host, port=port, reload=False, **ssl_config)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='API Service')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--ssl-certfile', help='SSL certificate file path (for HTTPS/WSS)')
    parser.add_argument('--ssl-keyfile', help='SSL private key file path (for HTTPS/WSS)')
    args = parser.parse_args()

    # 自动检测前端目录中的证书文件（如果未指定）
    if not args.ssl_certfile and not args.ssl_keyfile:
        frontend_cert = os.path.join(os.path.dirname(__file__), 'frontend', 'local_morphk_icu.pem')
        frontend_key = os.path.join(os.path.dirname(__file__), 'frontend', 'local_morphk_icu.key')
        if os.path.exists(frontend_cert) and os.path.exists(frontend_key):
            logger.info("检测到前端目录中的SSL证书，自动启用HTTPS/WSS")
            args.ssl_certfile = frontend_cert
            args.ssl_keyfile = frontend_key

    # 确保同时提供证书和密钥文件
    if (args.ssl_certfile and not args.ssl_keyfile) or (args.ssl_keyfile and not args.ssl_certfile):
        logger.error("错误：必须同时提供--ssl-certfile和--ssl-keyfile参数")
        sys.exit(1)

    protocol = "https" if args.ssl_certfile and args.ssl_keyfile else "http"
    logger.info("启动API服务: {protocol}://{host}:{port}", protocol=protocol, host=args.host, port=args.port)
    run_api(host=args.host, port=args.port, ssl_certfile=args.ssl_certfile, ssl_keyfile=args.ssl_keyfile)
