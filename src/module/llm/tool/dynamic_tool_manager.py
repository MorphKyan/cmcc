"""
Dynamic Tool Manager - 动态LLM工具管理器

提供动态工具的创建、持久化和热重载功能。
"""
import json
import threading
from pathlib import Path
from typing import Any, Callable, Literal

import httpx
from loguru import logger
from pydantic import BaseModel, Field, create_model
from langchain_core.tools import StructuredTool

from src.config.config import get_settings


# =============================================================================
# Pydantic Models
# =============================================================================

class ToolApiConfig(BaseModel):
    """外部 API 调用配置"""
    endpoint: str = Field(description="外部 API 端点 URL")
    method: str = Field(default="POST", description="HTTP 方法 (GET, POST, PUT, DELETE)")
    headers: dict[str, str] | None = Field(default=None, description="请求头")
    timeout: float = Field(default=10.0, description="请求超时时间（秒）")


class ToolParameterDef(BaseModel):
    """工具参数定义"""
    type: Literal["str", "int", "float", "bool"] = Field(description="参数类型")
    description: str = Field(description="参数描述")
    required: bool = Field(default=True, description="是否必填")


class DynamicToolDefinition(BaseModel):
    """动态工具定义"""
    name: str = Field(description="工具名称，需唯一")
    description: str = Field(description="工具描述，供 LLM 理解何时调用此工具")
    api_config: ToolApiConfig = Field(description="外部 API 配置")
    parameters: dict[str, ToolParameterDef] = Field(
        description="工具参数定义 {param_name: ToolParameterDef}"
    )


# =============================================================================
# Dynamic Tool Manager (Singleton)
# =============================================================================

class DynamicToolManager:
    """
    动态工具管理器 - 单例模式 + 线程安全
    
    功能：
    - 动态工具的增删改查
    - JSON 持久化
    - 回调机制用于通知 LLM Handler 更新
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        
        self._data_lock = threading.Lock()
        self._tools: dict[str, DynamicToolDefinition] = {}
        self._langchain_tools: dict[str, StructuredTool] = {}
        self._callbacks: list[Callable[[], None]] = []
        self._initialized = True
        
        # 加载持久化的工具
        self._load_tools()
        logger.info("DynamicToolManager 初始化完成，已加载 {} 个动态工具", len(self._tools))
    
    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    
    def add_tool(self, tool_def: DynamicToolDefinition) -> bool:
        """
        添加动态工具
        
        Args:
            tool_def: 工具定义
            
        Returns:
            bool: 是否成功
        """
        with self._data_lock:
            if tool_def.name in self._tools:
                logger.warning("工具 '{}' 已存在，添加失败", tool_def.name)
                return False
            
            # 创建 LangChain 工具
            langchain_tool = self._create_langchain_tool(tool_def)
            
            self._tools[tool_def.name] = tool_def
            self._langchain_tools[tool_def.name] = langchain_tool
            self._save_tools()
        
        logger.info("成功添加动态工具: {}", tool_def.name)
        self._notify_update()
        return True
    
    def delete_tool(self, name: str) -> bool:
        """
        删除动态工具
        
        Args:
            name: 工具名称
            
        Returns:
            bool: 是否成功
        """
        with self._data_lock:
            if name not in self._tools:
                logger.warning("工具 '{}' 不存在，删除失败", name)
                return False
            
            del self._tools[name]
            del self._langchain_tools[name]
            self._save_tools()
        
        logger.info("成功删除动态工具: {}", name)
        self._notify_update()
        return True
    
    def get_tool(self, name: str) -> DynamicToolDefinition | None:
        """获取工具定义"""
        with self._data_lock:
            return self._tools.get(name)
    
    def get_all_tools(self) -> list[DynamicToolDefinition]:
        """获取所有工具定义"""
        with self._data_lock:
            return list(self._tools.values())
    
    def get_langchain_tools(self) -> list[StructuredTool]:
        """获取所有 LangChain 工具对象"""
        with self._data_lock:
            return list(self._langchain_tools.values())
    
    def on_update(self, callback: Callable[[], None]) -> None:
        """
        注册工具更新回调
        
        Args:
            callback: 无参回调函数，在工具增删时调用
        """
        self._callbacks.append(callback)
        logger.debug("已注册工具更新回调，当前回调数: {}", len(self._callbacks))
    
    def reload(self) -> None:
        """重新从文件加载工具"""
        with self._data_lock:
            self._tools.clear()
            self._langchain_tools.clear()
            self._load_tools()
        self._notify_update()
    
    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------
    
    def _get_persist_path(self) -> Path:
        """获取持久化文件路径"""
        settings = get_settings()
        return Path(settings.data.dynamic_tools_path)
    
    def _load_tools(self) -> None:
        """从 JSON 文件加载工具"""
        persist_path = self._get_persist_path()
        
        if not persist_path.exists():
            logger.debug("动态工具配置文件不存在: {}", persist_path)
            return
        
        try:
            content = persist_path.read_text(encoding='utf-8')
            data = json.loads(content)
            
            for name, tool_dict in data.items():
                tool_def = DynamicToolDefinition(**tool_dict)
                self._tools[name] = tool_def
                self._langchain_tools[name] = self._create_langchain_tool(tool_def)
            
            logger.info("从 {} 加载了 {} 个动态工具", persist_path, len(self._tools))
        except Exception as e:
            logger.exception("加载动态工具配置失败: {}", e)
    
    def _save_tools(self) -> None:
        """保存工具到 JSON 文件"""
        persist_path = self._get_persist_path()
        
        try:
            persist_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {name: tool_def.model_dump() for name, tool_def in self._tools.items()}
            persist_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            
            logger.debug("动态工具配置已保存到: {}", persist_path)
        except Exception as e:
            logger.exception("保存动态工具配置失败: {}", e)
    
    def _notify_update(self) -> None:
        """触发所有更新回调"""
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                logger.exception("执行工具更新回调时出错: {}", e)
    
    def _create_langchain_tool(self, tool_def: DynamicToolDefinition) -> StructuredTool:
        """
        根据工具定义创建 LangChain StructuredTool
        
        Args:
            tool_def: 工具定义
            
        Returns:
            StructuredTool: LangChain 工具对象
        """
        # 1. 动态创建 Pydantic 输入模型
        type_mapping = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool
        }
        
        field_definitions: dict[str, Any] = {}
        for param_name, param_def in tool_def.parameters.items():
            py_type = type_mapping.get(param_def.type, str)
            if param_def.required:
                field_definitions[param_name] = (py_type, Field(description=param_def.description))
            else:
                field_definitions[param_name] = (py_type | None, Field(default=None, description=param_def.description))
        
        InputModel = create_model(f"{tool_def.name}Input", **field_definitions)
        
        # 2. 创建执行函数（同步版本，调用外部 API）
        def sync_tool_func(**kwargs) -> dict:
            api_config = tool_def.api_config
            try:
                with httpx.Client(timeout=api_config.timeout) as client:
                    response = client.request(
                        method=api_config.method,
                        url=api_config.endpoint,
                        json=kwargs,
                        headers=api_config.headers or {}
                    )
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": f"HTTP error: {e.response.status_code}", "detail": str(e)}
            except httpx.RequestError as e:
                return {"error": "Request failed", "detail": str(e)}
            except Exception as e:
                return {"error": "Unknown error", "detail": str(e)}
        
        # 3. 创建异步执行函数
        async def async_tool_func(**kwargs) -> dict:
            api_config = tool_def.api_config
            try:
                async with httpx.AsyncClient(timeout=api_config.timeout) as client:
                    response = await client.request(
                        method=api_config.method,
                        url=api_config.endpoint,
                        json=kwargs,
                        headers=api_config.headers or {}
                    )
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": f"HTTP error: {e.response.status_code}", "detail": str(e)}
            except httpx.RequestError as e:
                return {"error": "Request failed", "detail": str(e)}
            except Exception as e:
                return {"error": "Unknown error", "detail": str(e)}
        
        # 4. 返回 StructuredTool
        return StructuredTool.from_function(
            func=sync_tool_func,
            coroutine=async_tool_func,
            name=tool_def.name,
            description=tool_def.description,
            args_schema=InputModel
        )
