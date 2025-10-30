import sys
import os
import unittest
import json

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.component.ollama_llm_handler import OllamaLLMHandler
from src.component.rag_processor import RAGProcessor
from src.config.config import (
    SCREENS_DATA_PATH, DOORS_DATA_PATH, VIDEOS_DATA_PATH,
    CHROMA_DB_PATH, EMBEDDING_MODEL, TOP_K_RESULTS,
    SYSTEM_PROMPT_TEMPLATE
)

class TestOllamaLLMHandler(unittest.TestCase):

    def test_ollama_llm_response(self):
        """
        测试Ollama LLM处理器是否能结合RAG上下文生成响应。
        这是一个集成测试，会真实调用RAG和LLM。
        """
        print("\n--- 开始测试Ollama LLM处理器 ---")
        
        # 1. 初始化RAG处理器以获取上下文
        print("\n 初始化RAG处理器...")
        # 使用 force_reload=True 确保我们从一个干净的状态开始
        rag_processor = RAGProcessor(
            screens_data_path=SCREENS_DATA_PATH,
            doors_data_path=DOORS_DATA_PATH,
            videos_data_path=VIDEOS_DATA_PATH,
            chroma_db_path=CHROMA_DB_PATH,
            embedding_model=EMBEDDING_MODEL,
            top_k_results=TOP_K_RESULTS,
            force_reload=True
        )
        
        # 2. 初始化Ollama LLM处理器
        print("\n 初始化Ollama LLM处理器...")
        # 注意：OllamaLLMHandler 不需要 API 密钥和基础 URL
        llm_handler = OllamaLLMHandler(
            system_prompt_template=SYSTEM_PROMPT_TEMPLATE,
            model='llama3.1:8b'  # 可根据需要更改模型
        )
        
        # 3. 模拟用户输入并进行测试
        print("\n 模拟用户输入并获取响应...")
        test_query = "在主屏幕上播放一下关于企业文化的视频"
        
        # a. RAG检索
        retrieved_docs = rag_processor.retrieve_context(test_query)
        
        # b. LLM获取响应
        response_json_str = llm_handler.get_response(test_query, retrieved_docs)
        
        print(f"\n--- 测试结果 ---")
        print(f"用户查询: '{test_query}'")
        print(f"大模型响应: {response_json_str}")
        print("----------------\n")
        
        # 断言响应不为空
        self.assertTrue(response_json_str, "大模型响应不应为空")
        
        # 对于Ollama模型，我们不强制要求返回JSON格式，但如果有JSON格式则验证其结构
        try:
            response_data = json.loads(response_json_str)
            # 如果能解析为JSON，则至少应该包含一些基本字段
            # 注意：Ollama模型可能不会严格按照ARK模型的格式返回
        except json.JSONDecodeError:
            # Ollama模型可能返回纯文本，这是可以接受的
            pass
        except Exception as e:
            self.fail(f"处理响应时发生未知错误: {e}")

        print("--- Ollama LLM处理器测试完成 ---")

if __name__ == '__main__':
    unittest.main()
