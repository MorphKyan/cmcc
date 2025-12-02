import sys
from contextvars import ContextVar
from loguru import logger

# 创建一个 ContextVar 用于在异步任务中传递 request_id
# 这是在 asyncio 环境下传递上下文的正确方式
request_id_var: ContextVar[str] = ContextVar("request_id", default="SYSTEM")


def setup_logging(log_level: str = "INFO"):
    """
    使用 Loguru 配置日志系统。
    """
    # 移除默认的、未配置的处理器
    logger.remove()
    # 添加一个彩色、格式化的 Sink 到标准错误输出
    logger.add(
        sys.stderr,
        level=log_level.upper(),
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<bold>{name}</bold>:<bold>{function}</bold>:<bold>{line}</bold> - "
               "<level>{message}</level>",
        colorize=True,
        backtrace=True,  # 在异常时显示完整的堆栈跟踪
        diagnose=True  # 添加异常变量的详细诊断信息
    )
    # 添加一个输出到文件的 Sink，用于持久化日志
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        level=log_level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",  # 每天午夜轮转
        retention="10 days",
        compression="zip",  # 压缩旧日志
        enqueue=True,  # 【核心】使日志写入非阻塞且进程安全
        serialize=False  # 在多进程场景下，设置为 True 可以保证日志消息的原子性，但通常 enqueue 足够
    )
    # 添加一个错误日志文件，只记录 ERROR 及以上级别
    logger.add(
        "logs/error_{time:YYYY-MM-DD}.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True
    )
    logger.patch(lambda record: record["extra"].update(request_id=request_id_var.get()))
    logger.info("Loguru 日志系统配置完成。")
