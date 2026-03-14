import time
import json
import requests
import sys

# =================================================================
# 1. 配置 (强行指定 CPU 模式)
# =================================================================
MODEL_NAME = "qwen3.5:0.8b"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def check_ollama_service():
    try:
        response = requests.get("http://localhost:11434/", timeout=3)
        return response.status_code == 200
    except:
        return False

# =================================================================
# 2. 准备 Prompt
# =================================================================
system_prompt = """你是一个展厅中控意图解析器。请提取用户要控制的设备和资源，并以 JSON 格式输出：
1. device: 目标设备
2. media_content_name: 媒体/资源"""
user_input = "帮我把那个联通的大数据PPT投到左边的avb屏幕上"
prompt = f"System: {system_prompt}\nUser: {user_input}\nAssistant: "

# =================================================================
# 3. 压测执行
# =================================================================
if not check_ollama_service():
    print("❌ 错误: 未检测到 Ollama 服务。")
    sys.exit(1)

print(f"🖥️  启动 Qwen3.5 纯 CPU 推理性能测试...")
print(f"模型规格: {MODEL_NAME} | 模式: 纯 CPU (num_gpu=0)")

try:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "format": "json",
        "raw": True,
        "options": {
            "num_gpu": 0,       # 核心参数：强制禁用 GPU 推理
            "num_thread": 4,    # 指定线程数
            "temperature": 0.0,
            "seed": 42
        }
    }

    start_all = time.time()
    first_token_time = None
    output_text = ""

    response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
    
    for line in response.iter_lines():
        if line:
            if first_token_time is None:
                first_token_time = time.time()
            chunk = json.loads(line)
            output_text += chunk.get("response", "")
            if chunk.get("done"):
                eval_count = chunk.get("eval_count", 0) 
                eval_duration = chunk.get("eval_duration", 1)
                ttft_duration = chunk.get("prompt_eval_duration", 1)
                break

    end_all = time.time()

    # =================================================================
    # 4. 打印 CPU 性能报告
    # =================================================================
    print("\n" + "="*50)
    print("🚀 Qwen3.5 [纯 CPU] 性能压测报告")
    print("="*50)
    
    official_tps = (eval_count / (eval_duration / 1e9)) if eval_duration > 0 else 0
    official_ttft = ttft_duration / 1e6
    
    print(f"✅ 生成结果: {output_text.strip()}")
    print("-" * 50)
    print(f"⏱️  首字延迟 (TTFT):   {official_ttft:8.2f} ms")
    print(f"⚡  生成速度 (TPS):    {official_tps:8.2f} tokens/sec")
    print(f"📦  生成 Token 数:     {eval_count}")
    print(f"🧬  解码总耗时:        {eval_duration/1e6:8.2f} ms")
    print(f"💻  硬件配置:         num_gpu=0 (Pure CPU)")
    print("="*50)

except Exception as e:
    print(f"❌ 测试失败: {e}")
