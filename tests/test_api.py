import requests
import sys

try:
    print("Testing TTS API...")
    resp = requests.post(
        "http://127.0.0.1:8000/api/tts/generate", 
        json={"text": "测试一下"}
    )
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        with open("test_api.wav", "wb") as f:
            f.write(resp.content)
        print("Success! Audio saved to test_api.wav")
    else:
        print(f"Error: {resp.text}")
except Exception as e:
    print(f"Request failed: {e}")
