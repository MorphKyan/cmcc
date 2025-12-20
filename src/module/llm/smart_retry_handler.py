#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import List

from loguru import logger

from src.config.config import LLMSettings
from src.module.llm.tool.definitions import CommandAction


@dataclass
class RetryResult:
    """重试结果"""
    success: bool
    response: str
    attempt_count: int
    total_time: float
    error_messages: List[str] = field(default_factory=list)


class SmartRetryHandler:
    """指令重试处理器"""

    def __init__(self, settings: LLMSettings):
        self.max_retries = settings.max_validation_retries
        self.retry_delay = settings.retry_delay
        logger.info("指令重试处理器初始化完成",
                    max_retries=self.max_retries,
                    retry_delay=self.retry_delay)

    def _extract_validation_errors(self, response: str) -> List[str]:
        """提取验证错误信息"""
        try:
            commands = json.loads(response)
            errors = []

            for command in commands:
                if command.get("action") == CommandAction.ERROR.value:
                    value = command.get("value", "")
                    if "validation_failed:" in value:
                        errors.append(value.replace("validation_failed:", "").strip())

            return errors
        except (json.JSONDecodeError, AttributeError):
            return []

    def _has_validation_errors(self, response: str) -> bool:
        """检查响应是否包含验证错误"""
        errors = self._extract_validation_errors(response)
        return len(errors) > 0

    def _create_retry_prompt(self, original_input: str, validation_errors: List[str]) -> str:
        """创建重试提示"""
        error_feedback = "\n".join([f"- {error}" for error in validation_errors])

        retry_prompt = f"""
原始用户输入: {original_input}

你的上一次响应中的工具调用包含了以下验证错误:
{error_feedback}

请重新分析用户需求，并使用正确的设备名称、视频文件名或门名称。

请提供修正后的工具调用。
"""
        return retry_prompt.strip()

    async def execute_instruction_retry(
            self,
            original_input: str,
            llm_function,
            rag_docs: List
    ) -> RetryResult:
        """执行指令重试，最多重试3次"""
        start_time = time.time()
        current_input = original_input
        error_messages = []

        for attempt in range(self.max_retries):
            try:
                if attempt != 0:
                    logger.info(f"指令重试尝试 {attempt + 1}/{self.max_retries}")

                response = await llm_function(current_input, rag_docs)

                if not self._has_validation_errors(response):
                    total_time = time.time() - start_time
                    logger.info(f"指令在第{attempt + 1}次尝试后成功")
                    return RetryResult(
                        success=True,
                        response=response,
                        attempt_count=attempt + 1,
                        total_time=total_time,
                        error_messages=error_messages
                    )

                # 有验证错误，准备重试
                if attempt < self.max_retries - 1:
                    validation_errors = self._extract_validation_errors(response)
                    error_messages.extend(validation_errors)
                    logger.warning(f"LLM响应包含验证错误: {validation_errors}")

                    current_input = self._create_retry_prompt(original_input, validation_errors)
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    # 最后一次尝试仍有错误
                    error_messages.extend(self._extract_validation_errors(response))
                    total_time = time.time() - start_time
                    logger.error(f"指令验证在{self.max_retries}次尝试后失败")
                    return RetryResult(
                        success=False,
                        response=response,
                        attempt_count=self.max_retries,
                        total_time=total_time,
                        error_messages=error_messages
                    )

            except Exception as e:
                error_messages.append(f"LLM调用失败: {str(e)}")
                logger.error(f"LLM在第{attempt + 1}次尝试时失败: {e}")

                if attempt == self.max_retries - 1:
                    total_time = time.time() - start_time
                    return RetryResult(
                        success=False,
                        response=str(e),
                        attempt_count=self.max_retries,
                        total_time=total_time,
                        error_messages=error_messages
                    )

                await asyncio.sleep(self.retry_delay)

        total_time = time.time() - start_time
        return RetryResult(
            success=False,
            response="重试失败",
            attempt_count=self.max_retries,
            total_time=total_time,
            error_messages=error_messages
        )
