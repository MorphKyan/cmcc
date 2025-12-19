import asyncio
import json

import numpy as np
import numpy.typing as npt
from fastapi import WebSocket
from loguru import logger
from langchain_core.messages import HumanMessage

from src.api.context import Context
from src.core import dependencies
from src.module.llm.tool.definitions import ExecutableCommand, ExhibitionCommand, CommandAction
from src.services.performance_metrics_manager import MetricType
from src.services.aep_client import get_aep_client


async def receive_loop(websocket: WebSocket, context: Context) -> None:
    logger.info("WebSocket接收已启动")
    while True:
        try:
            data_bytes = await websocket.receive_bytes()
            logger.trace("WebSocket receive bytes size {size}", size=len(data_bytes))
            await context.audio_input_queue.put(data_bytes)
            logger.trace("WebSocket put audio_input_queue size {size}", size=len(data_bytes))
        except Exception as e:
            logger.error("WebSocket接收错误，{e}", e=e)
            break


async def run_decode_vad_appender(context: Context) -> None:
    """负责解码并直接推送到VAD处理器，合并了之前的decode_loop和vad_appender"""
    logger.info("解码与VAD输入处理器已启动")
    while True:
        try:
            data_bytes = await context.audio_input_queue.get()

            # 开始计时
            start_time = asyncio.get_running_loop().time()

            # 将bytes转换为int16数组，然后归一化到-1.0到1.0的float32范围
            int16_array = np.frombuffer(data_bytes, dtype=np.int16)
            float32_array = int16_array.astype(np.float32) / 32767.0

            # 直接推送到VAD处理器，跳过中间队列
            context.VADProcessor.append_audio(float32_array)

            # 计算耗时
            end_time = asyncio.get_running_loop().time()
            duration = end_time - start_time
            # 记录性能指标
            dependencies.metrics_manager.record(MetricType.VAD_INPUT, duration, context.context_id)
            if duration > 0.01:  # 仅记录超过10ms的日志
                logger.trace("[性能指标] VAD输入耗时: {duration:.4f}s", duration=duration)

        except Exception as e:
            logger.exception("解码与VAD输入处理错误")


async def run_vad_processor(context: Context) -> None:
    while True:
        try:
            # VAD处理是内部循环等待，这里测量每一轮的处理时间
            start_time = asyncio.get_running_loop().time()

            result = await context.VADProcessor.process_chunk()
            speech_segments = context.VADProcessor.process_result(result)

            end_time = asyncio.get_running_loop().time()
            duration = end_time - start_time
            # 记录性能指标
            dependencies.metrics_manager.record(MetricType.VAD_PROCESS, duration, context.context_id)
            if duration > 0.01:
                logger.debug("[性能指标] VAD处理耗时: {duration:.4f}s", duration=duration)

            for segment in speech_segments:
                start, end, audio_data = segment
                logger.info("[VAD] 检测到语音段: {start:.2f}s - {end:.2f}s, 长度: {length:.2f}s", start=start / 1000, end=end / 1000,
                            length=len(audio_data) / 16000)
                await context.audio_segment_queue.put(audio_data)
        except Exception as e:
            logger.exception("VAD处理错误")


async def run_asr_processor(context: Context) -> None:
    """ASR处理逻辑代码"""
    logger.info("ASR处理器已启动")
    while True:
        try:
            # 从VAD队列中获取分割好的语音片段
            segment: npt[np.float32] = await context.audio_segment_queue.get()
            # 使用ASR处理器处理音频数据
            start_time = asyncio.get_running_loop().time()
            recognized_text = await asyncio.to_thread(dependencies.asr_processor.process_audio_data, segment)

            end_time = asyncio.get_running_loop().time()
            duration = end_time - start_time
            # 记录性能指标
            dependencies.metrics_manager.record(MetricType.ASR_RECOGNIZE, duration, context.context_id)
            logger.info("[性能指标] ASR识别耗时: {duration:.3f}s", duration=duration)

            if recognized_text and recognized_text.strip():
                logger.info("[识别结果] {recognized_text}", recognized_text=recognized_text)
                await context.asr_output_queue.put(recognized_text)

        except Exception as e:
            logger.exception("[ASR错误]")
            # 可以选择是否继续处理或退出
            # break


async def run_llm_rag_processor(context: Context, websocket: WebSocket) -> None:
    """LLM/RAG处理逻辑代码"""
    logger.info("LLM/RAG处理器已启动")

    # 导入MetadataType用于分类检索
    from src.module.rag.base_rag_processor import MetadataType

    while True:
        try:
            recognized_text = await context.asr_output_queue.get()

            # 开始计时
            start_time = asyncio.get_running_loop().time()

            # 从配置中获取分类检索的 top_k 值
            rag_settings = dependencies.rag_processor.settings
            # 分别检索每种类型的文档
            door_docs = await dependencies.rag_processor.retrieve_context(
                recognized_text, metadata_types=[MetadataType.DOOR], top_k=rag_settings.door_top_k
            )
            video_docs = await dependencies.rag_processor.retrieve_context(
                recognized_text, metadata_types=[MetadataType.MEDIA], top_k=rag_settings.media_top_k
            )
            device_docs = await dependencies.rag_processor.retrieve_context(
                recognized_text, metadata_types=[MetadataType.DEVICE], top_k=rag_settings.device_top_k
            )

            # 构建分类后的RAG文档字典
            retrieved_docs_by_type = {
                "door": door_docs,
                "video": video_docs,
                "device": device_docs
            }

            # 获取聊天历史
            chat_history_messages = context.chat_history

            # 执行指令重试，获取AI消息和命令列表
            ai_message, commands, tool_messages = await dependencies.llm_processor.get_response_with_retries(
                user_input=recognized_text,
                rag_docs=retrieved_docs_by_type,
                user_location=context.location,
                chat_history=chat_history_messages
            )

            # 计算总耗时
            end_time = asyncio.get_running_loop().time()
            duration = end_time - start_time
            # 记录性能指标
            dependencies.metrics_manager.record(MetricType.LLM_GENERATE, duration, context.context_id)
            logger.info("[性能指标] LLM/RAG处理耗时: {duration:.3f}s", duration=duration)

            logger.info("[大模型响应] 返回 {count} 个命令", count=len(commands))

            # 自动保存对话到历史
            context.chat_history.append(HumanMessage(content=recognized_text))
            context.chat_history.append(ai_message)
            if tool_messages:
                context.chat_history.extend(tool_messages)

            # 当LLM未返回任何命令时，向前端发送提示
            if not commands:
                no_command_payload = json.dumps({
                    "type": "system_message",
                    "user_id": context.context_id,
                    "message": "抱歉，我无法理解您的指令。请尝试重新描述您的需求。"
                }, ensure_ascii=False)
                await websocket.send_text(no_command_payload)
                logger.info("[提示] 未识别到有效指令，已通知用户")
                continue

            # 构建可执行命令对象
            executable_cmd = ExecutableCommand(
                user_id=context.context_id,
                commands=commands
            )

            # 放入命令队列，由执行器异步处理
            await context.command_queue.put(executable_cmd)

        except Exception as e:
            logger.exception("[LLM/RAG错误]")
            # 可以选择是否继续处理或退出
            # break


async def run_command_executor(context: Context, websocket: WebSocket) -> None:
    """异步执行命令：本地执行或发送到前端"""
    logger.info("命令执行器已启动")
    while True:
        try:
            executable_cmd = await context.command_queue.get()

            start_time = asyncio.get_running_loop().time()
            execution_results: list[dict] = []

            # 1. 先执行本地命令（如更新位置）
            for cmd in executable_cmd.get_local_commands():
                result = await _execute_local_command(cmd, context)
                execution_results.append(result)
                # 发送本地命令执行结果到前端
                local_result_payload = json.dumps({
                    "type": "command_result",
                    "user_id": executable_cmd.user_id,
                    "command": cmd.model_dump(),
                    "result": result
                }, ensure_ascii=False)
                await websocket.send_text(local_result_payload)
                logger.info("[本地命令结果] action={action}, success={success}, message={message}",
                            action=cmd.action, success=result.get("success"), message=result.get("message"))

            # 2. 发送远程命令
            remote_commands = executable_cmd.get_remote_commands()
            for cmd in remote_commands:
                # control_device命令通过AEP HTTP API发送
                if cmd.action == CommandAction.CONTROL_DEVICE.value:
                    aep_result = await _execute_aep_command(cmd, context, websocket, executable_cmd.user_id)
                    execution_results.append(aep_result)
                else:
                    # 其他远程命令仍通过WebSocket发送到前端
                    single_cmd_payload = json.dumps({
                        "user_id": executable_cmd.user_id,
                        "commands": [cmd.model_dump()]
                    }, ensure_ascii=False)
                    logger.info("[发送命令] user={user_id}, action={action}, device={device}",
                                user_id=executable_cmd.user_id, action=cmd.action, device=cmd.device_name)
                    await websocket.send_text(single_cmd_payload)
                    execution_results.append({
                        "success": True,
                        "action": cmd.action,
                        "message": _get_command_description(cmd)
                    })

            # 3. 发送执行摘要到前端（用户友好的提示）
            summary_messages: list[str] = []
            for result in execution_results:
                if result.get("success"):
                    summary_messages.append(result.get("message", "操作成功"))

            if summary_messages:
                summary_payload = json.dumps({
                    "type": "execution_summary",
                    "user_id": executable_cmd.user_id,
                    "messages": summary_messages,
                    "summary": "正在执行：" + "；".join(summary_messages)
                }, ensure_ascii=False)
                await websocket.send_text(summary_payload)

            end_time = asyncio.get_running_loop().time()
            duration = end_time - start_time
            # 记录性能指标
            dependencies.metrics_manager.record(MetricType.CMD_EXECUTE, duration, context.context_id)
            logger.info("[性能指标] 命令执行耗时: {duration:.4f}s", duration=duration)

        except Exception as e:
            logger.exception("[命令执行错误]")


async def _execute_local_command(cmd: ExhibitionCommand, context: Context) -> dict:
    """执行本地命令，返回执行结果"""
    if cmd.action == "update_location" and cmd.value:
        old_location = context.location
        context.location = cmd.value
        logger.info("[位置更新] {old} -> {new}", old=old_location, new=cmd.value)
        return {
            "success": True,
            "action": cmd.action,
            "message": f"位置从「{old_location}」更新为「{cmd.value}」" if old_location else f"位置设置为「{cmd.value}」"
        }
    return {
        "success": False,
        "action": cmd.action,
        "message": f"未知的本地命令：{cmd.action}"
    }


def _get_command_description(cmd: ExhibitionCommand) -> str:
    """获取命令的用户友好描述"""
    action_descriptions = {
        "open_media": lambda c: f"在「{c.device_name}」上打开「{c.value}」",
        "open": lambda c: f"打开「{c.value}」",
        "close": lambda c: f"关闭「{c.value}」",
        "seek": lambda c: f"将「{c.device_name}」跳转到{c.value}秒",
        "set_volume": lambda c: f"将「{c.device_name}」音量设置为{c.value}",
        "adjust_volume": lambda c: f"{'提高' if c.value == 'up' else '降低'}「{c.device_name}」音量",
        "control_device": lambda c: f"控制设备「{c.device_name}」执行「{c.value}」",
    }

    if cmd.action in action_descriptions:
        return action_descriptions[cmd.action](cmd)
    return f"执行{cmd.action}操作"


async def _execute_aep_command(
    cmd: ExhibitionCommand,
    context: Context,
    websocket: WebSocket,
    user_id: str
) -> dict:
    """通过AEP HTTP API执行control_device命令
    
    Args:
        cmd: 要执行的命令
        context: 用户上下文
        websocket: WebSocket连接用于发送错误消息
        user_id: 用户ID
        
    Returns:
        执行结果字典，包含success、action、message字段
    """
    try:
        # 调用AEP API（cmd中已包含所有AEP字段，由工具函数填充）
        aep_client = get_aep_client()
        response = await aep_client.send_command(cmd)

        if response.success:
            # 保存device_name到context
            if response.device_name:
                context.last_device_name = response.device_name
                logger.info("[AEP] 保存设备名称: {name}", name=response.device_name)

            # 根据设备所属区域更新用户位置
            device_info = dependencies.data_service.get_device_info(cmd.device_name)
            if device_info:
                device_area = device_info.get("area", "")
                if device_area:
                    old_location = context.location
                    context.location = device_area
                    logger.info("[位置更新] 根据设备区域: {old} -> {new}", old=old_location, new=device_area)

            return {
                "success": True,
                "action": cmd.action,
                "message": f"设备「{cmd.device_name}」执行「{cmd.command}」"
            }
        else:
            # API返回失败，发送错误到前端
            await _send_command_error(websocket, user_id, cmd, response.message, response.code)
            return {
                "success": False,
                "action": cmd.action,
                "message": response.message
            }

    except Exception as e:
        error_msg = f"AEP API调用失败: {str(e)}"
        logger.exception("[AEP] 命令执行异常")
        await _send_command_error(websocket, user_id, cmd, error_msg, 500)
        return {
            "success": False,
            "action": cmd.action,
            "message": error_msg
        }


async def _send_command_error(
    websocket: WebSocket,
    user_id: str,
    cmd: ExhibitionCommand,
    message: str,
    code: int
) -> None:
    """发送命令错误到前端"""
    error_payload = json.dumps({
        "type": "command_error",
        "user_id": user_id,
        "command": cmd.model_dump(),
        "error": {
            "message": message,
            "code": code
        }
    }, ensure_ascii=False)
    await websocket.send_text(error_payload)
    logger.warning("[命令错误] user={user_id}, action={action}, error={error}",
                   user_id=user_id, action=cmd.action, error=message)
