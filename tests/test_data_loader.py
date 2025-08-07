import sys
import os
import unittest
import json

# 将项目根目录添加到 Python 路径，以便能够找到 src 目录下的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.component.data_loader import load_documents_from_csvs, format_docs_for_prompt
from src.config import SCREENS_DATA_PATH, DOORS_DATA_PATH, VIDEOS_DATA_PATH

class TestDataLoader(unittest.TestCase):

    def test_loading_and_formatting(self):
        """
        测试从CSV加载数据和格式化功能。
        """
        print("\n--- 开始测试数据加载与格式化 ---")
        try:
            # 1. 加载文档
            all_data_paths = [SCREENS_DATA_PATH, DOORS_DATA_PATH, VIDEOS_DATA_PATH]
            docs = load_documents_from_csvs(all_data_paths)
            print(f"成功加载 {len(docs)} 个文档。")
            
            self.assertTrue(len(docs) > 0, "应至少加载一个文档")

            # 2. 打印第一个文档以供验证
            if docs:
                print("\n--- 第一个文档示例 ---")
                print(f"内容: {docs[0].page_content}")
                print(f"元数据: {docs[0].metadata}")
                print("---------------------\n")
            
            # 3. 测试格式化函数
            formatted_context = format_docs_for_prompt(docs)
            print("--- 格式化后的上下文示例 ---")
            print(formatted_context)
            print("--------------------------\n")
            
            # 验证格式化输出是否为有效的JSON字符串
            self.assertIsInstance(formatted_context, str)
            json.loads(formatted_context) # 如果不是有效JSON会抛出异常

        except (FileNotFoundError, IOError) as e:
            self.fail(f"测试因文件错误失败: {e}")
        except json.JSONDecodeError:
            self.fail("格式化输出不是有效的JSON")

if __name__ == '__main__':
    unittest.main()
