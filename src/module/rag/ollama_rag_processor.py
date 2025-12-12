#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import urljoin

import httpx
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings
from loguru import logger

from src.config.config import RAGSettings
from src.module.rag.base_rag_processor import BaseRAGProcessor


class OllamaRAGProcessor(BaseRAGProcessor):
    """使用Ollama本地服务的RAG处理器。"""
    
    def __init__(self, settings: RAGSettings) -> None:
        """初始化Ollama RAG处理器。

        Args:
            settings: RAG配置
        """
        super().__init__(settings)
        self._http_client = httpx.AsyncClient(timeout=10.0)

    def _create_embedding_model(self) -> Embeddings:
        """创建Ollama Embedding模型。"""
        return OllamaEmbeddings(
            model=self.settings.ollama_embedding_model,
            base_url=self.settings.ollama_base_url
        )

    async def _pre_initialize(self) -> None:
        """初始化前检查Ollama服务连接和模型可用性。"""
        await self._check_ollama_connection()

    async def _check_ollama_connection(self) -> None:
        """检查Ollama服务连接和模型可用性。"""
        logger.info("正在检查Ollama服务连接: {url}", url=self.settings.ollama_base_url)
        try:
            response = await self._http_client.get(self.settings.ollama_base_url)
            response.raise_for_status()
            api_url = urljoin(self.settings.ollama_base_url, "api/tags")
            response = await self._http_client.get(api_url)
            response.raise_for_status()

            available_models = [m['name'] for m in response.json().get('models', [])]
            logger.info("Ollama服务连接成功。可用模型: {models}", models=available_models)
            if self.settings.ollama_embedding_model not in available_models:
                error_msg = (
                    f"Ollama服务中未找到所需模型: '{self.settings.ollama_embedding_model}'. "
                    f"请先执行: ollama pull {self.settings.ollama_embedding_model}"
                )
                raise RuntimeError(error_msg)

            logger.info("所需Embedding模型 '{model}' 在Ollama中可用。", 
                       model=self.settings.ollama_embedding_model)

        except httpx.RequestError as e:
            raise ConnectionError(
                f"无法连接到Ollama服务: {self.settings.ollama_base_url}。请确保Ollama正在运行。"
            ) from e
        except Exception as e:
            if isinstance(e, (RuntimeError, ConnectionError)):
                raise
            raise RuntimeError(f"检查Ollama时发生未知错误: {e}") from e

    async def close(self) -> None:
        """清理Ollama RAG资源。"""
        logger.info("正在清理Ollama RAG资源...")
        await self._http_client.aclose()
