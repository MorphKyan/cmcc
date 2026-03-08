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
    
    archive_url = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2"
    archive_path = os.path.join(model_dir, "sense-voice.tar.bz2")
    
    # Define expected files after extraction
    expected_files = ["model.onnx", "model.int8.onnx", "tokens.txt"]
    all_exist = all(os.path.exists(os.path.join(sense_voice_dir, f)) and os.path.getsize(os.path.join(sense_voice_dir, f)) > 0 for f in expected_files)
    
    if not all_exist:
        try:
            print(f"Downloading SenseVoice from {archive_url}")
            context = ssl._create_unverified_context()
            req = urllib.request.Request(archive_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=context) as response, open(archive_path, 'wb') as out_file:
                # Read chunks to avoid memory issues
                import shutil
                shutil.copyfileobj(response, out_file)
            print("Download complete. Extracting...")
            
            import tarfile
            with tarfile.open(archive_path, "r:bz2") as tar:
                # Extract specifically the required files and place them in sense-voice-dir directly
                for member in tar.getmembers():
                    for expected in expected_files:
                        if member.name.endswith(expected):
                            member.name = expected # Flatten the extraction
                            tar.extract(member, path=sense_voice_dir)
            print("Extraction complete.")
            
            # Clean up archive
            if os.path.exists(archive_path):
                os.remove(archive_path)
                
        except Exception as e:
            print(f"Failed to download or extract SenseVoice models: {e}")
    else:
        print("SenseVoice models already exist.")

if __name__ == "__main__":
    main()
