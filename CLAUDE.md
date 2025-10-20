# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a real-time voice control center for China Mobile's smart exhibition hall. The system converts natural language voice commands into structured JSON instructions using ASR (Automatic Speech Recognition), RAG (Retrieval-Augmented Generation), and LLM (Large Language Model) technologies.

## Directory Structure

```
.
├── src/
│   ├── __init__.py
│   ├── config.py               # All configuration: API keys, model paths, prompt templates
│   ├── data_loader.py          # Loads and formats documents from CSV
│   ├── ark_llm_handler.py      # Interface with VolcEngine's large model
│   ├── ollama_llm_handler.py   # Interface with local Ollama large model
│   ├── rag_processor.py        # Creates and queries local ChromaDB vector database
│   ├── audio_input.py          # Handles microphone audio input
│   ├── vad_processor.py        # Voice Activity Detection processor
│   ├── asr_processor.py        # Automatic Speech Recognition processor
│   └── app/
│       └── voice_assistant.py  # Core business logic integrating ASR, RAG and LLM
├── data/
│   ├── screens.csv             # Screen device information
│   ├── doors.csv               # Door device information
│   └── videos.csv              # Video information
├── chroma_db/
│   └── ...                     # (Auto-generated) Local vector database files
├── main.py                     # Project entry point
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Architecture

The system is modular with the following components:
- Voice Assistant (src/app/voice_assistant.py) - Main orchestrator
- Audio Input (src/core/audio_input.py) - Handles microphone audio streaming
- VAD Processor (src/core/vad_processor.py) - Voice Activity Detection to filter out silence
- ASR Processor (src/core/asr_processor.py) - Speech-to-text conversion using FunASR
- RAG Processor (src/core/rag_processor.py) - Context retrieval using ChromaDB
- Data Loader (src/core/data_loader.py) - Loads knowledge base from CSV files
- LLM Handlers (src/core/ark_llm_handler.py, src/core/ollama_llm_handler.py) - Interfaces with different LLM providers
- Configuration (src/config.py) - All system configuration and prompts

## Common Development Tasks

### Running the Application
```bash
python src/main_test.py
```

Options:
- `--device [auto|cpu|cuda:0]` - Select inference device
- `--force-rag-reload` - Rebuild vector database from CSV data
- `--llm-provider [ark|ollama]` - Select LLM provider

### Testing
Tests are run individually as Python scripts:
```bash
python tests/test_vad.py
python tests/test_audio_input.py
```

## Key Files and Directives

- Configuration: src/config.py contains all API keys, model paths, and system prompts
- Knowledge Base: data/*.csv files contain screens, doors, and video information
- Vector Database: chroma_db/ (auto-generated) stores embedded knowledge
- Entry Point: src/main.py
- Core Logic: src/app/voice_assistant.py

## Dependencies
Main dependencies include:
- funasr (for ASR and VAD)
- pyaudio (for audio input)
- torch (for ML inference)
- langchain, chromadb (for RAG)
- ollama (for local LLM)
- pandas (for data processing)

Install with: `pip install -r requirements.txt`