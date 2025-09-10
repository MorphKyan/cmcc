#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import ollama
from .data_loader import format_docs_for_prompt
from config import SCREENS_INFO, DOORS_INFO

class OllamaLLMHandler:
    def __init__(self, system_prompt_template, model='qwen3:8b'):
        """
        初始化本地Ollama大语言模型处理器。
        
        Args:
            system_prompt_template (str): 系统提示模板。
            model (str): 要使用的Ollama模型名称。
        """
        self.system_prompt_template = system_prompt_template
        
        try:
            self.client = ollama.Client()
            # 检查与Ollama服务器的连接
            self.client.list()
        except Exception as e:
            print(f"[错误] 初始化Ollama客户端或连接Ollama服务器失败: {e}")
            # 如果客户端初始化失败，后续无法调用，直接退出
            exit(1)
            
        self.model = model
        self.conversation_history = []
        
        # 定义function schemas
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "play_video",
                    "description": "播放指定的视频文件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {
                                "type": "string",
                                "description": "要播放的视频文件名"
                            },
                            "device": {
                                "type": "string",
                                "description": "要在其上播放视频的屏幕名称"
                            }
                        },
                        "required": ["target", "device"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "control_door",
                    "description": "控制门的开关",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {
                                "type": "string",
                                "description": "门的全称"
                            },
                            "action": {
                                "type": "string",
                                "enum": ["open", "close"],
                                "description": "要执行的操作：open（打开）或close（关闭）"
                            }
                        },
                        "required": ["target", "action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "seek_video",
                    "description": "跳转到视频的指定时间点",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device": {
                                "type": "string",
                                "description": "要跳转进度的屏幕名称"
                            },
                            "value": {
                                "type": "integer",
                                "description": "跳转到的秒数"
                            }
                        },
                        "required": ["device", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_volume",
                    "description": "设置音量到指定的绝对值",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device": {
                                "type": "string",
                                "description": "要设置音量的屏幕名称"
                            },
                            "value": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100,
                                "description": "音量值（0-100）"
                            }
                        },
                        "required": ["device", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "adjust_volume",
                    "description": "相对提高或降低音量",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device": {
                                "type": "string",
                                "description": "要调整音量的屏幕名称"
                            },
                            "value": {
                                "type": "string",
                                "enum": ["up", "down"],
                                "description": "音量调整方向：up（提高）或down（降低）"
                            }
                        },
                        "required": ["device", "value"]
                    }
                }
            }
        ]
        
        print(f"Ollama大语言模型处理器初始化完成，使用模型: {self.model}")

    def _construct_prompt(self, user_input, rag_docs):
        """
        构建包含RAG上下文的系统提示，并嵌入screens和doors信息。
        """
        rag_context = format_docs_for_prompt(rag_docs)
        
        # 将屏幕和门的信息转换为JSON字符串，确保格式正确
        screens_info_json = json.dumps(SCREENS_INFO, ensure_ascii=False, indent=2)
        doors_info_json = json.dumps(DOORS_INFO, ensure_ascii=False, indent=2)
        
        system_prompt = self.system_prompt_template.format(
            SCREENS_INFO=screens_info_json,
            DOORS_INFO=doors_info_json,
            rag_context=rag_context,
            USER_INPUT=user_input
        )
        return system_prompt

    def get_response(self, user_input, rag_docs):
        """
        结合RAG上下文，获取大模型的响应。
        
        Args:
            user_input (str): 用户的原始输入文本。
            rag_docs (list[Document]): RAG检索器返回的文档列表。
            
        Returns:
            str: 大模型返回的JSON格式指令或错误信息。
        """
        system_prompt = self._construct_prompt(user_input, rag_docs)
        # print(system_prompt)
        self.conversation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # print("\n--- 发送给大模型的最终Prompt ---")
        # print(system_prompt.replace(user_input, f"{{{{USER_INPUT}}}}"))
        print(f"用户指令: {user_input}")
        # print("--------------------------------\n")

        try:
            # 使用function calling方式调用模型
            response = self.client.chat(
                model=self.model,
                messages=self.conversation_history,
                tools=self.tools,
                think=False
            )
            
            # 检查是否有工具调用
            if response['message'].get('tool_calls'):
                # 处理工具调用
                tool_calls = response['message']['tool_calls']
                function_call = tool_calls[0]['function']
                function_name = function_call['name']
                arguments = function_call['arguments']
                
                # 根据函数名构建相应的JSON响应
                if function_name == "play_video":
                    result = {
                        "action": "play",
                        "target": arguments["target"],
                        "device": arguments["device"],
                        "value": None
                    }
                elif function_name == "control_door":
                    result = {
                        "action": arguments["action"],
                        "target": arguments["target"],
                        "device": None,
                        "value": None
                    }
                elif function_name == "seek_video":
                    result = {
                        "action": "seek",
                        "target": None,
                        "device": arguments["device"],
                        "value": arguments["value"]
                    }
                elif function_name == "set_volume":
                    result = {
                        "action": "set_volume",
                        "target": None,
                        "device": arguments["device"],
                        "value": arguments["value"]
                    }
                elif function_name == "adjust_volume":
                    result = {
                        "action": "adjust_volume",
                        "target": None,
                        "device": arguments["device"],
                        "value": arguments["value"]
                    }
                else:
                    # 未知函数调用
                    result = {
                        "action": "error",
                        "reason": "unknown_function",
                        "target": None,
                        "device": None,
                        "value": None
                    }
                
                # 将结果添加到对话历史中
                self.conversation_history.append({
                    "role": "assistant",
                    "content": "",
                    "tool_calls": tool_calls
                })
                
                self.conversation_history.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "name": function_name
                })
                
                # 返回格式化的JSON字符串
                return json.dumps(result, ensure_ascii=False)
            else:
                # 没有工具调用，返回模型的直接响应
                assistant_message = response['message']['content']
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                # 尝试解析为JSON，如果失败则返回错误
                try:
                    parsed_response = json.loads(assistant_message)
                    if isinstance(parsed_response, dict) and "action" in parsed_response:
                        return json.dumps(parsed_response, ensure_ascii=False)
                    else:
                        print(f"[警告] LLM输出格式不正确，缺少action字段: {assistant_message}")
                        return '{"action": "error", "reason": "invalid_format", "target": null, "device": null, "value": null}'
                except json.JSONDecodeError:
                    print(f"[警告] LLM输出不是有效的JSON格式: {assistant_message}")
                    return '{"action": "error", "reason": "invalid_json", "target": null, "device": null, "value": null}'
            
        except Exception as api_error:
            error_message = f"[错误] 调用Ollama API出错: {api_error}"
            print(error_message)
            return '{"action": "error", "reason": "api_failure", "target": null, "device": null, "value": null}'
