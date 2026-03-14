import time
import json
import requests
import sys

# =================================================================
# 1. 配置 (使用 Ollama 运行 Qwen3.5 以支持 Hybrid 架构)
# =================================================================
# 确保你的 Ollama 已经下载了模型：ollama pull qwen3.5:0.8b
MODEL_NAME = "qwen3.5:0.8b"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def check_ollama_service():
    """检查 Ollama 服务是否在线"""
    try:
        response = requests.get("http://localhost:11434/", timeout=3)
        return response.status_code == 200
    except:
        return False

# =================================================================
# 2. 准备测试数据
# =================================================================
system_prompt = """你是一个展厅中控意图解析器。请提取用户的操作指令、设备描述和资源描述。
可用指令：[OPEN_MEDIA, SEEK, SET_VOLUME, CONTROL_PPT, POWER_CONTROL, ERROR]"""
user_input = "帮我把那个联通的大数据PPT投到走廊左边的屏幕上"

# 构建 ChatML 格式或直接使用 system 参数
prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"

# =================================================================
# 3. 推理执行 (Benchmark)
# =================================================================
if not check_ollama_service():
    print("❌ 错误: 未检测到 Ollama 服务。")
    print("请确保已安装 Ollama 并启动 (访问 https://ollama.com)。")
    sys.exit(1)

print(f"🚀 正在通过 Ollama 执行 Qwen3.5 基准测试: {MODEL_NAME}")
print("注意: Ollama 会自动处理 Qwen3.5 的 CPU 和 GPU 推理。")

try:
    start_infer = time.time()
    first_token_time = None
    output_text = ""
    token_count = 0

    # 调用 Ollama 流式 API
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "format": "json", 
        "raw": True, # 使用原始 prompt 避免模版冲突
        "options": {
            "temperature": 0.0,
            "num_predict": 128,
            "seed": 42
        }
    }

    response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
    
    for line in response.iter_lines():
        if line:
            if first_token_time is None:
                first_token_time = time.time()
            
            chunk = json.loads(line)
            output_text += chunk.get("response", "")
            if not chunk.get("done", False):
                token_count += 1
            else:
                # 记录 Ollama 返回的总时长 (纳秒转毫秒)
                total_duration_ns = chunk.get("total_duration", 0)
                load_duration_ns = chunk.get("load_duration", 0)
                eval_duration_ns = chunk.get("eval_duration", 0)

    end_infer = time.time()

    # =================================================================
    # 4. 打印报告
    # =================================================================
    if not first_token_time:
        first_token_time = end_infer

    ttft_ms = (first_token_time - start_infer) * 1000
    total_time_ms = (end_infer - start_infer) * 1000
    tps = token_count / (end_infer - first_token_time) if (end_infer - first_token_time) > 0 else 0

    print("="*50)
    print("📊 Ollama 推理性能报告 (Benchmark)")
    print("="*50)
    
    try:
        parsed_json = json.loads(output_text)
        print(f"✅ 推理结果:\n{json.dumps(parsed_json, indent=2, ensure_ascii=False)}")
    except:
        print(f"⚠️ 解析结果 (非标准 JSON):\n{output_text}")

    print("-" * 50)
    print(f"⏱️ 首字延迟 (TTFT):   {ttft_ms:8.2f} ms")
    print(f"⏱️ 生成速度 (TPS):    {tps:8.2f} tokens/sec")
    print(f"⏱️ 总计耗时 (Total):  {total_time_ms:8.2f} ms")
    print(f"📦 生成 Token 数:     {token_count}")
    print("="*50)

    # 打印 Ollama 内部细分时长 (如果可用)
    if 'total_duration_ns' in locals() and total_duration_ns > 0:
        print(f"Ollama 内部耗时统计:")
        print(f" - 环境加载: {load_duration_ns/1e6:8.2f} ms")
        print(f" - 纯生成耗时: {eval_duration_ns/1e6:8.2f} ms")

except Exception as e:
    print(f"❌ 基准测试失败: {e}")
