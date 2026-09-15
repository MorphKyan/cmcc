import asyncio
import os
import sys
import time

# Ensure /root/cmcc is in sys.path
sys.path.insert(0, "/root/cmcc")

from loguru import logger
from src.config.config import get_settings
from src.core import dependencies
from src.services.data_service import DataService
from src.module.rag.openai_compatible_rag_processor import OpenAICompatibleRAGProcessor
from src.module.rag.base_rag_processor import MetadataType
from src.module.llm.openai_compatible_llm_handler import OpenAICompatibleLLMHandler
from langchain_core.messages import HumanMessage

async def main():
    print("=" * 70)
    print(" 1. 重建 RAG 数据库 (BAAI/bge-m3 @ SiliconFlow -> ./chroma_db)")
    print("=" * 70)

    # 1. 确保在 /root/cmcc 工作目录下
    os.chdir("/root/cmcc")
    settings = get_settings()

    print(f"RAG Provider: {settings.rag.provider}")
    print(f"Embedding Model: {settings.rag.openai_compatible_embedding_model}")
    print(f"Embedding Base URL: {settings.rag.openai_compatible_base_url}")
    print(f"Chroma DB Dir: {settings.rag.chroma_db_dir}")
    print(f"LLM Model: {settings.llm.openai_compatible_model}")
    print(f"LLM Base URL: {settings.llm.openai_compatible_base_url}")

    # 2. 初始化 DataService
    dependencies.data_service = DataService()
    docs = dependencies.data_service.get_all_doors_data()
    print(f"DataService 数据已加载 (门: {len(docs)}, 媒体: {len(dependencies.data_service.get_all_media_data())}, 设备: {len(dependencies.data_service.get_all_devices_data())}, 区域: {len(dependencies.data_service.get_all_areas_data())})")

    # 3. 初始化并构建 RAG 数据库
    t0 = time.time()
    rag_processor = OpenAICompatibleRAGProcessor(settings.rag)
    dependencies.rag_processor = rag_processor
    
    print("\n正在通过 SiliconFlow bge-m3 批量生成向量并写入 Chroma / BM25 ...")
    await rag_processor.initialize()
    t_rag_build = time.time() - t0

    # 验证重建结果
    chroma_count = rag_processor.vector_store._collection.count()
    bm25_count = len(rag_processor.bm25_retriever.documents) if rag_processor.bm25_retriever else 0
    print(f"\n[RAG 重建成功!]")
    print(f" - 构建耗时: {t_rag_build:.2f} 秒")
    print(f" - Chroma 向量文档数: {chroma_count}")
    print(f" - BM25 索引文档数: {bm25_count}")
    print(f" - 状态: {rag_processor.status}")

    # 4. 初始化 LLM 处理器 (已默认关闭思考模式)
    print("\n" + "=" * 70)
    print(" 2. 初始化 LLM 处理器 (qwen3.7-flash, 思考模式已默认关闭)")
    print("=" * 70)
    llm_processor = OpenAICompatibleLLMHandler(settings.llm)
    await llm_processor.initialize()
    dependencies.llm_processor = llm_processor
    print(f"LLM 处理器初始化完成，状态: {llm_processor.status}")

    # 5. 集成端到端测试 (RAG 检索 -> LLM 推理与工具调用)
    print("\n" + "=" * 70)
    print(" 3. 执行集成端到端性能基准测试 (Integrated Benchmark)")
    print("=" * 70)

    test_cases = [
        {
            "id": "MEDIA-01",
            "desc": "媒体精确播放",
            "input": "在小米电视上播放企业文化",
            "mtypes": [MetadataType.MEDIA, MetadataType.DEVICE]
        },
        {
            "id": "MEDIA-02",
            "desc": "媒体模糊匹配",
            "input": "在14米全屏播放那个宣传片",
            "mtypes": [MetadataType.MEDIA, MetadataType.DEVICE]
        },
        {
            "id": "PWR-01",
            "desc": "设备通用电源开机",
            "input": "打开小米电视",
            "mtypes": [MetadataType.DEVICE]
        },
        {
            "id": "PWR-02",
            "desc": "设备通用电源关机",
            "input": "关闭14米全屏",
            "mtypes": [MetadataType.DEVICE]
        },
        {
            "id": "PWR-03",
            "desc": "设备自定义场景指令",
            "input": "前厅灯光1路全开",
            "mtypes": [MetadataType.DEVICE]
        },
        {
            "id": "VOL-01",
            "desc": "指定音量调节",
            "input": "把小米电视音量调到50",
            "mtypes": [MetadataType.DEVICE]
        },
        {
            "id": "SEEK-01",
            "desc": "视频快进跳转",
            "input": "视频快进到1分30秒",
            "mtypes": [MetadataType.DEVICE]
        },
        {
            "id": "PPT-01",
            "desc": "PPT翻页控制",
            "input": "PPT下一页",
            "mtypes": [MetadataType.DEVICE]
        },
        {
            "id": "CPLX-01",
            "desc": "多设备复杂复合指令",
            "input": "准备演示环境，灯光调到1路全开，播放宣传视频",
            "mtypes": [MetadataType.MEDIA, MetadataType.DEVICE]
        },
        {
            "id": "EDGE-01",
            "desc": "日常闲聊/非控制指令 (静默/闲聊)",
            "input": "今天天气怎么样",
            "mtypes": [MetadataType.DEVICE, MetadataType.MEDIA]
        }
    ]

    results = []

    for case in test_cases:
        query = case["input"]
        mtypes = case["mtypes"]

        # Step A: RAG 混合检索 (Chroma + BM25 + RRF)
        t_rag_start = time.perf_counter()
        
        # 分别检索对应的类型
        rag_tasks = []
        if MetadataType.MEDIA in mtypes:
            rag_tasks.append(rag_processor.retrieve_context(query, metadata_types=[MetadataType.MEDIA], top_k=settings.rag.media_top_k))
        else:
            rag_tasks.append(asyncio.sleep(0, result=[]))
            
        if MetadataType.DEVICE in mtypes:
            rag_tasks.append(rag_processor.retrieve_context(query, metadata_types=[MetadataType.DEVICE], top_k=settings.rag.device_top_k))
        else:
            rag_tasks.append(asyncio.sleep(0, result=[]))
            
        door_docs_task = asyncio.sleep(0, result=[])
        
        media_docs, device_docs = await asyncio.gather(*rag_tasks)
        t_rag_end = time.perf_counter()
        rag_latency_ms = (t_rag_end - t_rag_start) * 1000

        retrieved_docs_by_type = {
            "door": [],
            "video": media_docs,
            "device": device_docs
        }

        # Step B: LLM 推理与工具调用
        t_llm_start = time.perf_counter()
        ai_msg, commands, tool_messages = await llm_processor.get_response_with_retries(
            user_input=query,
            rag_docs=retrieved_docs_by_type,
            user_location="智慧生活馆",
            chat_history=[]
        )
        t_llm_end = time.perf_counter()
        llm_latency_ms = (t_llm_end - t_llm_start) * 1000
        e2e_latency_ms = (t_llm_end - t_rag_start) * 1000

        # Token 消耗信息
        usage = getattr(ai_msg, "usage_metadata", {}) or {}
        in_tokens = usage.get("input_tokens", 0)
        out_tokens = usage.get("output_tokens", 0)
        
        cmd_summary = [f"{c.action}(device={c.device_name}, cmd={c.command}, param={c.params})" for c in commands] if commands else []
        if not cmd_summary and ai_msg.content:
            cmd_summary = [f"文本回复: {ai_msg.content[:40]}..."]

        res_item = {
            "id": case["id"],
            "desc": case["desc"],
            "input": query,
            "rag_docs_count": len(media_docs) + len(device_docs),
            "rag_ms": rag_latency_ms,
            "llm_ms": llm_latency_ms,
            "e2e_ms": e2e_latency_ms,
            "in_tokens": in_tokens,
            "out_tokens": out_tokens,
            "commands": cmd_summary
        }
        results.append(res_item)

        print(f"\n[{case['id']} - {case['desc']}]")
        print(f"  用户指令: '{query}'")
        print(f"  召回文档: {res_item['rag_docs_count']} 篇 (耗时: {rag_latency_ms:.1f} ms)")
        print(f"  LLM响应: {llm_latency_ms:.1f} ms | 端到端总计: {e2e_latency_ms:.1f} ms")
        print(f"  Token: 输入={in_tokens}, 输出={out_tokens}")
        print(f"  执行指令: {cmd_summary}")

    # 6. 统计报表
    avg_rag = sum(r["rag_ms"] for r in results) / len(results)
    avg_llm = sum(r["llm_ms"] for r in results) / len(results)
    avg_e2e = sum(r["e2e_ms"] for r in results) / len(results)
    min_e2e = min(r["e2e_ms"] for r in results)
    max_e2e = max(r["e2e_ms"] for r in results)

    print("\n" + "=" * 70)
    print(" 4. 性能指标总结与评估报表")
    print("=" * 70)
    print(f"测试用例总数: {len(results)}")
    print(f"平均 RAG 检索耗时 : {avg_rag:.1f} ms")
    print(f"平均 LLM 响应耗时 : {avg_llm:.1f} ms")
    print(f"平均端到端总延迟  : {avg_e2e:.1f} ms ({avg_e2e/1000:.2f} s)")
    print(f"最快端到端响应    : {min_e2e:.1f} ms")
    print(f"最慢端到端响应    : {max_e2e:.1f} ms")
    print("=" * 70)

    await rag_processor.close()

if __name__ == "__main__":
    asyncio.run(main())
