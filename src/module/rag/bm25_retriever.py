import os
import pickle
from typing import List

import jieba
from langchain_core.documents import Document
from loguru import logger
from rank_bm25 import BM25Okapi

class BM25Retriever:
    """基于 BM25 的稀疏检索器，用于精确关键词匹配"""
    
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self.index_path = os.path.join(persist_dir, "bm25_index.pkl")
        self.docs_path = os.path.join(persist_dir, "bm25_docs.pkl")
        self.bm25: BM25Okapi | None = None
        self.documents: List[Document] = []
        os.makedirs(persist_dir, exist_ok=True)
        
    def _tokenize(self, text: str) -> List[str]:
        """使用 jieba 进行中文分词"""
        return list(jieba.cut_for_search(text))
        
    def build_index(self, documents: List[Document]):
        """构建 BM25 索引并持久化"""
        logger.info(f"正在构建 BM25 索引，共 {len(documents)} 个文档...")
        self.documents = documents
        tokenized_corpus = [self._tokenize(doc.page_content) for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        # 序列化保存
        with open(self.index_path, "wb") as f:
            pickle.dump(self.bm25, f)
        with open(self.docs_path, "wb") as f:
            pickle.dump(self.documents, f)
        logger.info("BM25 索引构建并保存完成。")
            
    def load_index(self) -> bool:
        """加载已有的 BM25 索引"""
        if os.path.exists(self.index_path) and os.path.exists(self.docs_path):
            logger.info("正在加载本地 BM25 索引...")
            try:
                with open(self.index_path, "rb") as f:
                    self.bm25 = pickle.load(f)
                with open(self.docs_path, "rb") as f:
                    self.documents = pickle.load(f)
                return True
            except Exception as e:
                logger.error(f"加载 BM25 索引失败: {e}")
                return False
        return False
        
    def retrieve(self, query: str, top_k: int = 10, metadata_types: List[str] | None = None) -> List[tuple[Document, float]]:
        """检索文档，返回包含 (Document, score) 的列表"""
        if self.bm25 is None or not self.documents:
            logger.warning("BM25 索引未初始化！")
            return []
            
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # 组合 (doc, score)
        scored_docs = list(zip(self.documents, scores))
        
        # 过滤 metadata type
        if metadata_types is not None:
            scored_docs = [
                (doc, score) for doc, score in scored_docs
                if doc.metadata.get("type") in metadata_types
            ]
            
        # 根据得分降序排序并截取 top_k
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:top_k]
