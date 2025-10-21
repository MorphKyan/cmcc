#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import threading
import os
import sys
import shutil
import pandas as pd

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# 使用绝对导入而不是相对导入
from src.module.rag.rag_processor import RAGProcessor
from src.config import VIDEOS_DATA_PATH, CHROMA_DB_PATH, EMBEDDING_MODEL, TOP_K_RESULTS

app = FastAPI(title="API Service", description="RESTful API for assistant", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量存储RAG处理器实例
rag_processor = None
rag_lock = threading.Lock()  # 用于线程安全

# Pydantic模型定义
class HealthResponse(BaseModel):
    status: str
    service: str

class RefreshResponse(BaseModel):
    status: str
    message: str

class StatusResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    message: Optional[str] = None

class QueryRequest(BaseModel):
    query: str

class QueryResult(BaseModel):
    content: str
    metadata: dict

class QueryResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    message: Optional[str] = None

class UploadResponse(BaseModel):
    status: str
    message: str

def initialize_rag_processor():
    """初始化RAG处理器"""
    global rag_processor
    try:
        rag_processor = RAGProcessor(
            videos_data_path=VIDEOS_DATA_PATH,
            chroma_db_path=CHROMA_DB_PATH,
            embedding_model=EMBEDDING_MODEL,
            top_k_results=TOP_K_RESULTS
        )
        return True
    except Exception as e:
        print(f"初始化RAG处理器失败: {e}")
        return False

def refresh_rag_database():
    """刷新RAG数据库"""
    global rag_processor
    with rag_lock:
        try:
            if rag_processor is None:
                # 如果处理器未初始化，则创建新的
                success = initialize_rag_processor()
                if not success:
                    return False
            
            # 使用RAG处理器的刷新方法
            success = rag_processor.refresh_database()
            return success
        except Exception as e:
            print(f"刷新RAG数据库失败: {e}")
            return False

def validate_csv_structure(file_path):
    """验证CSV文件结构是否正确"""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['type', 'name', 'aliases', 'description', 'filename']
        
        # 检查是否包含所有必需的列
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"缺少必需的列: {missing_columns}"
        
        # 检查type列是否都是'video'
        if not all(df['type'] == 'video'):
            return False, "type列必须全部为'video'"
        
        # 检查是否有空值
        if df.isnull().any().any():
            return False, "CSV文件中不能包含空值"
            
        return True, "CSV文件结构正确"
    except Exception as e:
        return False, f"验证CSV文件时发生错误: {str(e)}"

# 初始化RAG处理器
if not initialize_rag_processor():
    print("警告: RAG处理器初始化失败")

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(status="healthy", service="RAG API Service")

@app.post("/api/rag/refresh", response_model=RefreshResponse)
async def refresh_rag():
    """刷新RAG数据库端点"""
    try:
        success = refresh_rag_database()
        if success:
            return RefreshResponse(status="success", message="RAG数据库已成功刷新")
        else:
            raise HTTPException(status_code=500, detail="刷新RAG数据库失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新RAG数据库时发生异常: {str(e)}")

@app.get("/api/rag/status", response_model=StatusResponse)
async def rag_status():
    """获取RAG状态"""
    global rag_processor
    try:
        if rag_processor is None:
            raise HTTPException(status_code=500, detail="RAG处理器未初始化")
        
        # 检查数据库是否存在
        db_exists = os.path.exists(CHROMA_DB_PATH)
        
        data = {
            "initialized": rag_processor is not None,
            "database_exists": db_exists,
            "database_path": CHROMA_DB_PATH,
            "embedding_model": EMBEDDING_MODEL,
            "top_k_results": TOP_K_RESULTS
        }
        
        return StatusResponse(status="success", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取RAG状态时发生异常: {str(e)}")

@app.post("/api/rag/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """查询RAG数据库"""
    global rag_processor
    try:
        if rag_processor is None:
            raise HTTPException(status_code=500, detail="RAG处理器未初始化")
        
        query_text = request.query
        if not query_text:
            raise HTTPException(status_code=400, detail="查询参数 'query' 不能为空")
        
        # 执行查询
        retrieved_docs = rag_processor.retrieve_context(query_text)
        
        # 格式化结果
        results = []
        for doc in retrieved_docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        data = {
            "query": query_text,
            "results": results,
            "count": len(results)
        }
        
        return QueryResponse(status="success", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询RAG数据库时发生异常: {str(e)}")

@app.post("/api/rag/upload-videos", response_model=UploadResponse)
async def upload_videos_csv(file: UploadFile = File(...)):
    """上传videos.csv文件并更新RAG数据库"""
    global rag_processor
    try:
        # 检查文件类型
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="只支持上传CSV文件")
        
        # 保存上传的文件到临时位置
        temp_file_path = os.path.join(os.path.dirname(VIDEOS_DATA_PATH), 'temp_videos.csv')
        
        # 读取上传的文件内容
        contents = await file.read()
        with open(temp_file_path, 'wb') as f:
            f.write(contents)
        
        # 验证CSV文件结构
        is_valid, message = validate_csv_structure(temp_file_path)
        if not is_valid:
            # 删除临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise HTTPException(status_code=400, detail=message)
        
        # 备份原文件
        backup_path = VIDEOS_DATA_PATH + '.backup'
        if os.path.exists(VIDEOS_DATA_PATH):
            shutil.copy2(VIDEOS_DATA_PATH, backup_path)
        
        # 替换原文件
        shutil.move(temp_file_path, VIDEOS_DATA_PATH)
        
        # 刷新RAG数据库
        success = refresh_rag_database()
        if not success:
            # 如果刷新失败，恢复备份文件
            if os.path.exists(backup_path):
                shutil.move(backup_path, VIDEOS_DATA_PATH)
            raise HTTPException(status_code=500, detail="上传成功但刷新RAG数据库失败，已恢复原文件")
        
        # 删除备份文件
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        return UploadResponse(status="success", message="videos.csv文件上传成功，RAG数据库已更新")
        
    except Exception as e:
        # 删除可能存在的临时文件
        temp_file_path = os.path.join(os.path.dirname(VIDEOS_DATA_PATH), 'temp_videos.csv')
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"上传videos.csv文件时发生异常: {str(e)}")

def run_api(host='0.0.0.0', port=5000):
    """运行API服务"""
    import uvicorn
    uvicorn.run("src.api.main:app", host=host, port=port, reload=False)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='RAG API Service')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    args = parser.parse_args()
    
    print(f"启动RAG API服务: http://{args.host}:{args.port}")
    run_api(host=args.host, port=args.port)