import sys
import os
import unittest
import json

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.component.ark_llm_handler import LLMHandler
from src.component.rag_processor import RAGProcessor

class TestLLMHandler(unittest.TestCase):

    def test_llm_response(self):
        """
        测试LLM处理器是否能结合RAG上下文生成响应。
        这是一个集成测试，会真实调用RAG和LLM。
        """
        print("\n--- 开始测试LLM处理器 ---")
        
        # 1. 初始化RAG处理器以获取上下文
        print("\n 初始化RAG处理器...")
        # 使用 force_reload=True 确保我们从一个干净的状态开始
        rag_processor = RAGProcessor(force_reload=True) 
        
        # 2. 初始化LLM处理器
        print("\n 初始化LLM处理器...")
        llm_handler = LLMHandler()
        
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
        
        # 断言响应是有效的JSON
        try:
            response_data = json.loads(response_json_str)
            self.assertIn("action", response_data, "响应JSON中应包含 'action' 字段")
        except json.JSONDecodeError:
            self.fail("大模型的响应不是一个有效的JSON字符串")
        except Exception as e:
            self.fail(f"处理响应时发生未知错误: {e}")

        print("--- LLM处理器测试完成 ---")

if __name__ == '__main__':
    unittest.main()
