import sys
import logging
from contextvars import ContextVar
from loguru import logger


# 创建一个 ContextVar 用于在异步任务中传递 request_id
# 这是在 asyncio 环境下传递上下文的正确方式
request_id_var: ContextVar[str] = ContextVar("request_id", default="SYSTEM")



class InterceptHandler(logging.Handler):
    """
    将标准 logging 日志拦截并重定向到 Loguru
    """
    def emit(self, record: logging.LogRecord) -> None:
        # 获取对应的 Loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 判断是否调用者栈信息
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 过滤掉健康检查日志 (GET / HTTP)
        if record.name == "uvicorn.access" and "GET / HTTP" in record.getMessage():
            return

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(log_level: str = "INFO"):
    """
    使用 Loguru 配置日志系统，并拦截 logging 日志
    """
    # 移除默认的、未配置的处理器
    logger.remove()
    
    # 拦截标准库 logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # 配置 Loguru Sink
    # 标准输出
    logger.add(
        sys.stderr,
        level=log_level.upper(),
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<bold>{name}</bold>:<bold>{function}</bold>:<bold>{line}</bold> - "
               "<level>{message}</level>",
        colorize=True,
    )
    # 文件输出 (常规)
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        level=log_level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",
        retention="10 days",
        compression="zip",
        enqueue=True,
        serialize=False
    )
    # 文件输出 (错误)
    logger.add(
        "logs/error_{time:YYYY-MM-DD}.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        enqueue=True,
        # backtrace=True,
        # diagnose=True
    )
    
    logger.patch(lambda record: record["extra"].update(request_id=request_id_var.get()))
    logger.info("Loguru 日志系统配置完成。")


