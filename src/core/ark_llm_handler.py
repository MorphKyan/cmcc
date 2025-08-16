#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from volcenginesdkarkruntime import Ark
from .data_loader import format_docs_for_prompt
from config import SCREENS_INFO, DOORS_INFO

class LLMHandler:
    def __init__(self, ark_api_key, ark_base_url, llm_model_name, system_prompt_template):
        """
        初始化大语言模型处理器。
        
        Args:
            ark_api_key (str): 火山引擎API密钥。
            ark_base_url (str): 火山引擎API基础URL。
            llm_model_name (str): 大语言模型名称。
            system_prompt_template (str): 系统提示模板。
        """
        self.system_prompt_template = system_prompt_template
        
        try:
            self.client = Ark(api_key=ark_api_key, base_url=ark_base_url)
        except Exception as e:
            print(f"[错误] 初始化火山引擎客户端失败: {e}")
            # 如果客户端初始化失败，后续无法调用，直接退出
            exit(1)
            
        self.llm_model_name = llm_model_name
        self.conversation_history = []
        print("大语言模型处理器初始化完成。")

    def _construct_prompt(self, user_input, rag_docs):
        """
        构建包含RAG上下文的系统提示，并嵌入screens和doors信息。
        """
        rag_context = format_docs_for_prompt(rag_docs)
        system_prompt = self.system_prompt_template.format(
            SCREENS_INFO=SCREENS_INFO,
            DOORS_INFO=DOORS_INFO,
            rag_context=rag_context,
            USER_INPUT=user_input  # 模板中也包含USER_INPUT占位符
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
        
        # 重置对话历史，每次都以新的RAG上下文作为系统提示
        self.conversation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        print("\n--- 发送给大模型的最终Prompt ---")
        print(system_prompt.replace(user_input, f"{{{{USER_INPUT}}}}")) # 打印模板
        print(f"用户指令: {user_input}")
        print("--------------------------------\n")

        try:
            response = self.client.chat.completions.create(
                model=self.llm_model_name,
                messages=self.conversation_history
            )
            
            assistant_message = response.choices[0].message.content
            
            # 将大模型的响应也添加到对话历史中（虽然当前是单轮，但保留此结构以备将来扩展）
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # 验证LLM输出是否为有效的JSON格式
            import json
            try:
                # 尝试解析LLM的输出
                parsed_response = json.loads(assistant_message)
                # 检查是否包含必需的action字段
                if isinstance(parsed_response, dict) and "action" in parsed_response:
                    # 返回格式化的JSON字符串
                    return json.dumps(parsed_response, ensure_ascii=False)
                else:
                    # 如果解析后的对象不包含action字段，返回错误
                    print(f"[警告] LLM输出格式不正确，缺少action字段: {assistant_message}")
                    return '{"action": "error", "reason": "invalid_format", "target": null, "device": null, "value": null}'
            except json.JSONDecodeError:
                # 如果无法解析为JSON，返回错误
                print(f"[警告] LLM输出不是有效的JSON格式: {assistant_message}")
                return '{"action": "error", "reason": "invalid_json", "target": null, "device": null, "value": null}'
            
        except Exception as api_error:
            error_message = f"[错误] 调用大模型API出错: {api_error}"
            print(error_message)
            # 返回一个标准的错误JSON
            return '{"action": "error", "reason": "api_failure", "target": null, "device": null, "value": null}'
