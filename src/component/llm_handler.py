#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from volcenginesdkarkruntime import Ark
from config import (
    ARK_API_KEY,
    ARK_BASE_URL,
    LLM_MODEL_NAME,
    SYSTEM_PROMPT_TEMPLATE
)
from .data_loader import format_docs_for_prompt

class LLMHandler:
    def __init__(self):
        """
        初始化大语言模型处理器。
        """
        try:
            self.client = Ark(api_key=ARK_API_KEY, base_url=ARK_BASE_URL)
        except Exception as e:
            print(f"[错误] 初始化火山引擎客户端失败: {e}")
            # 如果客户端初始化失败，后续无法调用，直接退出
            exit(1)
            
        self.conversation_history = []
        print("大语言模型处理器初始化完成。")

    def _construct_prompt(self, user_input, rag_docs):
        """
        构建包含RAG上下文的系统提示。
        """
        rag_context = format_docs_for_prompt(rag_docs)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
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
                model=LLM_MODEL_NAME,
                messages=self.conversation_history
            )
            
            assistant_message = response.choices[0].message.content
            
            # 将大模型的响应也添加到对话历史中（虽然当前是单轮，但保留此结构以备将来扩展）
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as api_error:
            error_message = f"[错误] 调用大模型API出错: {api_error}"
            print(error_message)
            # 返回一个标准的错误JSON
            return '{"action": "error", "reason": "api_failure"}'

if __name__ == '__main__':
    # 测试代码
    from .rag_processor import RAGProcessor

    print("--- 测试LLM处理器 ---")
    
    # 1. 初始化RAG处理器以获取上下文
    print("\n[1] 初始化RAG处理器...")
    rag_processor = RAGProcessor()
    
    # 2. 初始化LLM处理器
    print("\n[2] 初始化LLM处理器...")
    llm_handler = LLMHandler()
    
    # 3. 模拟用户输入并进行测试
    print("\n[3] 模拟用户输入并获取响应...")
    test_query = "在主屏幕上播放一下关于企业文化的视频"
    
    # a. RAG检索
    retrieved_docs = rag_processor.retrieve_context(test_query)
    
    # b. LLM获取响应
    response_json = llm_handler.get_response(test_query, retrieved_docs)
    
    print(f"\n--- 测试结果 ---")
    print(f"用户查询: '{test_query}'")
    print(f"大模型响应: {response_json}")
    print("----------------\n")
    
    print("--- LLM处理器测试完成 ---")
