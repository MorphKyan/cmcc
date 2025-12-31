import pytest
from fastapi.testclient import TestClient
import sys
import os
import json

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

class TestPipelineFunctional:
    
    @pytest.mark.parametrize("case_data", [
        # --- 1. Media Control (MEDIA) ---
        {"id": "MEDIA-01", "input": "在小米电视上播放企业文化", "desc": "Basic Play"},
        {"id": "MEDIA-02", "input": "在14米全屏播放那个宣传片", "desc": "Fuzzy Media"},
        {"id": "MEDIA-03", "input": "播放云价值视频", "desc": "Implied Device"},
        {"id": "MEDIA-04", "input": "在Cave空间的左侧副屏播放三生万物", "desc": "With Location Context"},
        {"id": "MEDIA-05", "input": "播放一个不存在的视频123", "desc": "Invalid Media"},

        # --- 2. Device Power Control (PWR) ---
        {"id": "PWR-01", "input": "打开小米电视", "desc": "Generic On"},
        {"id": "PWR-02", "input": "关闭14米全屏", "desc": "Generic Off"},
        {"id": "PWR-03", "input": "前厅灯光1路全开", "desc": "Custom Scene"},
        {"id": "PWR-04", "input": "关闭前厅灯光", "desc": "Ambiguous"},
        {"id": "PWR-05", "input": "关闭前厅的所有灯光", "desc": "Specific Off"},

        # --- 3. Volume & Playback Control (VOL/SEEK/VID/PPT) ---
        {"id": "VOL-01", "input": "把小米电视音量调到50", "desc": "Set Absolute Volume"},
        {"id": "VOL-02", "input": "声音大一点", "desc": "Adjust Volume Up"},
        {"id": "VOL-03", "input": "小米电视静音", "desc": "Mute"},
        {"id": "SEEK-01", "input": "视频快进到1分30秒", "desc": "Seek Time"},
        {"id": "VID-01", "input": "暂停播放", "desc": "Pause"},
        {"id": "PPT-01", "input": "PPT下一页", "desc": "Next Page"},
        {"id": "PPT-02", "input": "跳转到第5页", "desc": "Jump Page"},

        # --- 4. Complex/Chain Scenarios (CPLX) ---
        {"id": "CPLX-01", "input": "打开小米电视和投影仪", "desc": "Multi-Device"},
        {"id": "CPLX-02", "input": "准备演示环境，灯光调到1路全开，播放宣传视频", "desc": "Scene Setup"},

        # --- 5. Edge Cases (EDGE) ---
        {"id": "EDGE-01", "input": "今天天气怎么样", "desc": "Nonsense/Chat"},
        {"id": "EDGE-02", "input": "删除所有文件", "desc": "Hostile/Safety"},
        {"id": "EDGE-03", "input": "把音量调到200", "desc": "Wrong Param"},
    ])
    def test_pipeline_scenarios(self, case_data):
        print(f"\n[{case_data['id']}] Input: {case_data['input']} ({case_data['desc']})")
        
        response = client.post("/pipeline/text", json={"text": case_data['input']})
        
        # Check HTTP status
        if response.status_code != 200:
            print(f"HTTP Error {response.status_code}: {response.text}")
            return

        data = response.json()
        
        # Pretty print the 'commands' or 'message' part of the response
        if data.get("success"):
            print("Response (Success):")
            # Dump the 'commands' list nicely
            commands = data.get("commands", [])
            if commands:
                print(json.dumps(commands, ensure_ascii=False, indent=2))
            else:
                print("  No commands generated.")
                
            # If there is a text response/message from LLM
            if data.get("message"):
                 print(f"  Message: {data.get('message')}")
        else:
            print(f"Response (Failed): {data.get('message')}")
        
        print("-" * 60)

if __name__ == "__main__":
    try:
        pytest.main([__file__, "-v", "-s"])
    except NameError:
        import sys
        sys.exit(pytest.main([__file__, "-v", "-s"]))
