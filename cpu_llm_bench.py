import time
import json
import os
import sys
from llama_cpp import Llama

# =================================================================
# 1. 配置与模型路径 (修复路径处理)
# =================================================================
MODEL_NAME = "Qwen3.5-0.8B-Q8_0.gguf"
# 获取脚本所在目录，确保路径正确
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", MODEL_NAME)

# 备选路径：如果 models 目录下没找到，尝试在当前目录找
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(BASE_DIR, MODEL_NAME)

if not os.path.exists(MODEL_PATH):
    print(f"❌ 错误: 找不到模型文件 {MODEL_PATH}")
    print("请确保模型文件放在 models 文件夹下或脚本同级目录。")
    sys.exit(1)

# =================================================================
# 2. 初始化模型 (针对 CPU 优化)
# =================================================================
print(f"🚀 正在加载模型: {MODEL_PATH}")
print("使用纯 CPU 模式 (n_gpu_layers=0)...")

try:
    start_load = time.time()
    llm = Llama(
        model_path=MODEL_PATH,
        n_gpu_layers=0,       # 强制 CPU
        n_ctx=1024,           # 上下文大小，足够解析指令即可
        n_threads=4,          # 可根据物理核心数调整
        verbose=False         # 为了 benchmark 结果整洁，设为 False
    )
    load_duration = time.time() - start_load
    print(f"✅ 模型加载成功，耗时: {load_duration:.2f} 秒\n")
except Exception as e:
    print(f"❌ 模型加载失败!")
    # 手动检查 GGUF 元数据中的架构进行故障提示
    try:
        with open(MODEL_PATH, "rb") as f:
            data = f.read(2048).decode('utf-8', errors='ignore')
            if "qwen35" in data:
                print("\n⚠️  检测到模型架构为 'qwen35' (Qwen3.5 系列专用)。")
                print("目前 llama-cpp-python 0.3.16 的预编译二进制文件可能尚未完整集成该架构支持。")
                print("建议: 1. 等待官方更新版本。")
                print("      2. 或者改用 Qwen2.5-0.5B/1.5B 等经典架构模型。")
    except:
        pass
    print(f"\n详情: {e}")
    sys.exit(1)

# =================================================================
# 3. 准备 Prompt 和 JSON Schema
# =================================================================
system_prompt = """你是一个展厅中控意图解析器。请提取用户的操作指令、设备描述和资源描述。
可用指令：[OPEN_MEDIA, SEEK, SET_VOLUME, CONTROL_PPT, POWER_CONTROL, ERROR]"""
user_input = "帮我把那个联通的大数据PPT投到走廊左边的屏幕上"

# 使用 Qwen2.5/3.5 的 ChatML 模版
prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"

json_schema = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["OPEN_MEDIA", "SEEK", "SET_VOLUME", "CONTROL_PPT", "POWER_CONTROL", "ERROR"]},
        "device_query": {"type": "string"},
        "media_query": {"type": "string"}
    },
    "required": ["action", "device_query", "media_query"]
}

# =================================================================
# 4. 执行推理 Benchmark
# =================================================================
print("🏃 正在执行 CPU 推理速度测试 (强制 JSON 格式)...")

start_infer = time.time()
first_token_time = None
output_text = ""
token_count = 0

try:
    stream = llm.create_completion(
        prompt=prompt,
        max_tokens=128,
        temperature=0.1,
        response_format={
            "type": "json_object",
            "schema": json_schema
        },
        stream=True
    )

    for chunk in stream:
        if first_token_time is None:
            first_token_time = time.time()
        
        # 提取生成的文本块
        if "choices" in chunk and len(chunk["choices"]) > 0:
            delta = chunk["choices"][0].get("text", "")
            output_text += delta
            if delta:
                token_count += 1

    end_infer = time.time()

    # =================================================================
    # 5. 计算并打印报告
    # =================================================================
    if not first_token_time:
        first_token_time = end_infer

    ttft = (first_token_time - start_infer) * 1000
    total_time = (end_infer - start_infer) * 1000
    decode_time = total_time - ttft
    tps = token_count / (end_infer - first_token_time) if (end_infer - first_token_time) > 0 else 0

    print("="*50)
    print("📊 CPU 推理性能报告 (Benchmark)")
    print("="*50)
    
    # 解析并格式化 JSON 输出
    try:
        parsed_json = json.loads(output_text)
        print(f"✅ 推理结果:\n{json.dumps(parsed_json, indent=2, ensure_ascii=False)}")
    except:
        print(f"⚠️ 解析失败 (模型输出非标准 JSON):\n{output_text}")

    print("-" * 50)
    print(f"⏱️ 首字延迟 (TTFT):   {ttft:8.2f} ms")
    print(f"⏱️ 生成速度 (TPS):    {tps:8.2f} tokens/sec")
    print(f"⏱️ 总计延迟 (Total):  {total_time:8.2f} ms")
    print(f"📦 生成 Token 数:     {token_count}")
    print("="*50)

except Exception as e:
    print(f"❌ 推理过程中发生错误: {e}")