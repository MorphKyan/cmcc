import os
import urllib.request
import ssl

def download_file(url, filepath):
    print(f"Downloading from {url} to {filepath}")
    
    # Try using HF mirror first
    url = url.replace("huggingface.co", "hf-mirror.com")
    
    context = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=context, timeout=60) as response, open(filepath, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print("Download complete via hf-mirror.")
    except Exception as e:
        print(f"Failed via mirror {url}, trying direct: {e}")
        try:
            url_direct = url.replace("hf-mirror.com", "huggingface.co")
            req_direct = urllib.request.Request(url_direct, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_direct, context=context, timeout=60) as response, open(filepath, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
            print("Download direct complete.")
        except Exception as e2:
            print(f"Direct download failed: {e2}")

def main():
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "models")
    os.makedirs(model_dir, exist_ok=True)
    
    # WeSpeaker Model
    wespeaker_url = "https://huggingface.co/Wespeaker/wespeaker-voxceleb-resnet34-LM/resolve/main/voxceleb_resnet34_LM.onnx"
    wespeaker_path = os.path.join(model_dir, "wespeaker_resnet34.onnx")
    if not os.path.exists(wespeaker_path) or os.path.getsize(wespeaker_path) == 0:
        download_file(wespeaker_url, wespeaker_path)
    else:
        print("wespeaker_resnet34.onnx already exists.")

    # Silero VAD Model
    silero_vad_url = "https://huggingface.co/FunAudioLLM/SenseVoiceSmall/resolve/main/silero_vad.onnx"
    silero_vad_path = os.path.join(model_dir, "silero_vad.onnx")
    if not os.path.exists(silero_vad_path) or os.path.getsize(silero_vad_path) == 0:
        download_file(silero_vad_url, silero_vad_path)
    else:
        print("silero_vad.onnx already exists.")

    # SenseVoiceSmall Models
    sense_voice_dir = os.path.join(model_dir, "sense-voice-small")
    os.makedirs(sense_voice_dir, exist_ok=True)
    sense_voice_files = {
        "model.onnx": "https://huggingface.co/FunAudioLLM/SenseVoiceSmall/resolve/main/model.onnx",
        "model.int8.onnx": "https://huggingface.co/FunAudioLLM/SenseVoiceSmall/resolve/main/model.int8.onnx",
        "tokens.txt": "https://huggingface.co/FunAudioLLM/SenseVoiceSmall/resolve/main/tokens.txt"
    }
    for filename, url in sense_voice_files.items():
        filepath = os.path.join(sense_voice_dir, filename)
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            download_file(url, filepath)
        else:
            print(f"{filename} already exists.")

if __name__ == "__main__":
    main()
