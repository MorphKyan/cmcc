#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network retry strategies for LLM handlers.

This module provides reusable retry logic that can be used across different
LLM processors to handle network-related errors with exponential backoff.
"""

import asyncio
import random
from functools import wraps
from typing import TypeVar, Callable, Awaitable

import httpx
import requests
from loguru import logger

T = TypeVar('T')


def is_network_error(error: Exception) -> bool:
    """
    判断异常是否为网络相关错误，需要重试。

    Args:
        error: 异常对象

    Returns:
        bool: 是否为可重试的网络错误
    """
    # HTTP相关错误
    if isinstance(error, (httpx.ConnectError, httpx.TimeoutException, httpx.ReadTimeout,
                         httpx.WriteTimeout, httpx.PoolTimeout, httpx.NetworkError)):
        return True

    # requests库错误（备用）
    if isinstance(error, (requests.ConnectionError, requests.Timeout, requests.RequestException)):
        return True

    # 常见的网络相关错误消息
    error_str = str(error).lower()
    network_keywords = [
        'connection', 'timeout', 'network', 'dns', 'ssl', 'tls',
        'reset', 'refused', 'unreachable', 'interrupted'
    ]

    return any(keyword in error_str for keyword in network_keywords)


def exponential_backoff_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    jitter: bool = True
):
    """
    指数退避重试装饰器，用于异步函数。

    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        jitter: 是否添加随机抖动以避免重试风暴
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # 检查是否为可重试的网络错误
                    if not is_network_error(e) or attempt >= max_retries:
                        # 不可重试的错误或已达到最大重试次数，抛出异常
                        raise e

                    # 计算延迟时间
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)  # 0.5x to 1.0x

                    logger.warning(
                        f"网络请求失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}. "
                        f"将在 {delay:.2f} 秒后重试..."
                    )

                    await asyncio.sleep(delay)

            # 理论上不会到达这里，因为最后一次重试会抛出异常
            raise last_exception

        return wrapper
    return decorator


class RetryStrategy:
    """重试策略基类"""

    async def execute(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """
        执行带重试的函数调用。

        Args:
            func: 要执行的异步函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            函数的返回值

        Raises:
            Exception: 如果所有重试都失败
        """
        raise NotImplementedError("子类必须实现 execute 方法")


class ExponentialBackoffRetryStrategy(RetryStrategy):
    """
    指数退避重试策略实现。

    这个类提供了与装饰器相同的功能，但以面向对象的方式实现，
    便于依赖注入和配置管理。
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    async def execute(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """执行带指数退避重试的函数调用。"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                # 检查是否为可重试的网络错误
                if not is_network_error(e) or attempt >= self.max_retries:
                    # 不可重试的错误或已达到最大重试次数，抛出异常
                    raise e

                # 计算延迟时间
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                if self.jitter:
                    delay *= (0.5 + random.random() * 0.5)  # 0.5x to 1.0x

                logger.warning(
                    f"网络请求失败 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}. "
                    f"将在 {delay:.2f} 秒后重试..."
                )

                await asyncio.sleep(delay)

        # 理论上不会到达这里，因为最后一次重试会抛出异常
        raise last_exception