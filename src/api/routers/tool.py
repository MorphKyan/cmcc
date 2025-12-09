"""
Dynamic Tool API Router - 动态工具管理 API

提供动态 LLM 工具的增删查接口。
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from loguru import logger

from src.module.llm.tool.dynamic_tool_manager import (
    DynamicToolManager,
    DynamicToolDefinition,
    ToolApiConfig,
    ToolParameterDef
)


router = APIRouter(prefix="/tools", tags=["Dynamic Tools"])


# =============================================================================
# Response Models
# =============================================================================

class ToolListResponse(BaseModel):
    """工具列表响应"""
    count: int = Field(description="工具数量")
    tools: list[DynamicToolDefinition] = Field(description="工具列表")


class ToolOperationResponse(BaseModel):
    """工具操作响应"""
    success: bool = Field(description="操作是否成功")
    message: str = Field(description="操作结果消息")
    tool_name: str | None = Field(default=None, description="操作的工具名称")


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("", response_model=ToolListResponse)
async def list_dynamic_tools():
    """
    获取所有动态工具列表
    
    Returns:
        ToolListResponse: 包含工具数量和工具列表
    """
    manager = DynamicToolManager()
    tools = manager.get_all_tools()
    
    logger.debug("获取动态工具列表，共 {} 个", len(tools))
    return ToolListResponse(count=len(tools), tools=tools)


@router.post("", response_model=ToolOperationResponse, status_code=status.HTTP_201_CREATED)
async def add_dynamic_tool(tool_def: DynamicToolDefinition):
    """
    添加新的动态工具
    
    工具添加后会立即生效，所有 LLM Handler 实例会自动感知并更新。
    
    Args:
        tool_def: 工具定义
        
    Returns:
        ToolOperationResponse: 操作结果
        
    Raises:
        HTTPException: 如果工具名称已存在
    """
    manager = DynamicToolManager()
    
    # 检查工具名称是否已存在
    if manager.get_tool(tool_def.name) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"工具 '{tool_def.name}' 已存在"
        )
    
    success = manager.add_tool(tool_def)
    
    if success:
        logger.info("通过 API 添加动态工具: {}", tool_def.name)
        return ToolOperationResponse(
            success=True,
            message=f"工具 '{tool_def.name}' 添加成功",
            tool_name=tool_def.name
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加工具 '{tool_def.name}' 失败"
        )


@router.get("/{tool_name}", response_model=DynamicToolDefinition)
async def get_dynamic_tool(tool_name: str):
    """
    获取指定工具的详情
    
    Args:
        tool_name: 工具名称
        
    Returns:
        DynamicToolDefinition: 工具定义
        
    Raises:
        HTTPException: 如果工具不存在
    """
    manager = DynamicToolManager()
    tool = manager.get_tool(tool_name)
    
    if tool is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工具 '{tool_name}' 不存在"
        )
    
    return tool


@router.delete("/{tool_name}", response_model=ToolOperationResponse)
async def delete_dynamic_tool(tool_name: str):
    """
    删除指定的动态工具
    
    工具删除后会立即生效，所有 LLM Handler 实例会自动感知并更新。
    
    Args:
        tool_name: 工具名称
        
    Returns:
        ToolOperationResponse: 操作结果
        
    Raises:
        HTTPException: 如果工具不存在
    """
    manager = DynamicToolManager()
    
    # 检查工具是否存在
    if manager.get_tool(tool_name) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工具 '{tool_name}' 不存在"
        )
    
    success = manager.delete_tool(tool_name)
    
    if success:
        logger.info("通过 API 删除动态工具: {}", tool_name)
        return ToolOperationResponse(
            success=True,
            message=f"工具 '{tool_name}' 删除成功",
            tool_name=tool_name
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除工具 '{tool_name}' 失败"
        )
