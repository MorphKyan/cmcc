# VAD Processor Module Documentation

## Overview

The VAD (Voice Activity Detection) Processor module is a core component of the voice assistant system that detects speech activity in audio streams. It uses the FunASR library to provide real-time voice activity detection capabilities.

## Features

- Real-time voice activity detection
- Low coupling design
- Easy integration with existing audio processing pipelines
- Configurable chunk size and sample rate

## Installation

The VAD Processor module requires the following dependencies:

- funasr
- numpy

These dependencies are already included in the project's `requirements.txt` file.

## Usage

### Basic Usage

```python
from core.vad_processor import VADProcessor
import numpy as np

# Initialize the VAD processor
vad_processor = VADProcessor(chunk_size=200, sample_rate=16000)

# Process an audio stream
audio_data = np.random.rand(16000).astype(np.float32)  # Example audio data
speech_segments = vad_processor.process_audio_stream(audio_data)

# Check if speech was detected
if speech_segments:
    print(f"Detected {len(speech_segments)} speech segments")
    for segment in speech_segments:
        print(f"Start: {segment[0]}ms, End: {segment[1]}ms")
else:
    print("No speech detected")
```

### Integration with Audio Input

```python
from core.vad_processor import VADProcessor
from core.audio_input import AudioInputHandler
import numpy as np

# Initialize components
audio_handler = AudioInputHandler()
audio_handler.init_audio_stream()
vad_processor = VADProcessor()

# Get audio data from input handler
audio_data = audio_handler.get_audio_data()

# Process with VAD
if audio_data.dtype == np.int16:
    audio_data = audio_data.astype(np.float32) / 32768.0

speech_segments = vad_processor.process_audio_stream(audio_data)
```

## API Reference

### VADProcessor Class

#### `__init__(chunk_size: int = 200, sample_rate: int = 16000)`

Initializes the VAD processor.

**Parameters:**
- `chunk_size` (int): Audio chunk size in milliseconds. Default is 200ms.
- `sample_rate` (int): Audio sample rate in Hz. Default is 16000Hz.

#### `process_audio_chunk(audio_chunk: np.ndarray) -> list`

Processes a single audio chunk and detects voice activity. Uses an input buffer to handle variable-length audio chunks and accumulate data until processing requirements are met.

**Parameters:**
- `audio_chunk` (np.ndarray): Audio data chunk

**Returns:**
- list: List of detected speech segments, each element contains (start_time_ms, end_time_ms, audio_data)

#### `process_audio_stream(audio_data: np.ndarray) -> list`

Processes an entire audio stream by dividing it into chunks and detecting voice activity.

**Parameters:**
- `audio_data` (np.ndarray): Complete audio data

**Returns:**
- list: List of all detected speech segments in the audio stream

#### `reset_cache()`

Resets the VAD model cache.

## Integration with Voice Assistant

The VAD Processor is integrated into the Voice Assistant application to improve efficiency by only processing audio when speech is detected.

```python
# In voice_assistant.py
from core.vad_processor import VADProcessor

class VoiceAssistant:
    def __init__(self, ...):
        # Initialize VAD processor
        self.vad_processor = VADProcessor()
    
    def _asr_thread_loop(self):
        while not self.stop_event.is_set():
            try:
                # Get audio data
                frames = [self.audio_input_handler.get_audio_data(timeout=1) 
                         for _ in range(int(RATE / CHUNK * self.record_seconds))]
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                
                # Convert to float32 if needed
                if audio_data.dtype == np.int16:
                    audio_data = audio_data.astype(np.float32) / 32768.0

                # Use VAD to detect speech activity
                speech_segments = self.vad_processor.process_audio_stream(audio_data)
                
                # Only process with ASR if speech is detected
                if speech_segments:
                    print(f"[VAD] Detected speech activity: {speech_segments}")
                    # Proceed with ASR processing...
```

## Example Applications

1. **Voice-Controlled Systems**: Reduce processing overhead by only analyzing audio when speech is detected.
2. **Audio Recording**: Automatically start/stop recording based on voice activity.
3. **Noise Filtering**: Focus on segments with speech while ignoring silent periods.

## Performance Considerations

- The VAD processor is optimized for real-time processing
- Chunk size can be adjusted based on latency requirements
- The module works efficiently with both CPU and GPU inference
