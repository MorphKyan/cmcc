# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a real-time voice control center for China Mobile's smart exhibition hall. The system converts natural language voice commands into structured JSON instructions using ASR (Automatic Speech Recognition), RAG (Retrieval-Augmented Generation), and LLM (Large Language Model) technologies. The project is implemented as a FastAPI web service with RESTful APIs.

## Directory Structure

```
.
├── src/
│   ├── __init__.py
│   ├── config/                    # Configuration management
│   │   ├── __init__.py
│   │   ├── config.py              # All configuration: API keys, model paths, prompt templates
│   │   └── logging_config.py      # Logging configuration
│   ├── core/                      # Core application infrastructure
│   │   ├── __init__.py
│   │   ├── dependencies.py        # FastAPI dependency injection
│   │   └── lifespan.py            # Application lifecycle management
│   ├── module/                    # Core processing modules
│   │   ├── __init__.py
│   │   ├── input/                 # Audio input handling
│   │   │   ├── __init__.py
│   │   │   ├── audio_input.py     # Handles microphone audio input
│   │   │   └── stream_decoder.py  # Audio stream decoding
│   │   ├── vad/                   # Voice Activity Detection
│   │   │   ├── __init__.py
│   │   │   ├── vad_core.py        # Core VAD implementation
│   │   │   └── vad_processor.py   # VAD processor interface
│   │   ├── asr/                   # Automatic Speech Recognition
│   │   │   ├── __init__.py
│   │   │   └── asr_processor.py   # Speech-to-text conversion using FunASR
│   │   ├── rag/                   # Retrieval-Augmented Generation
│   │   │   ├── __init__.py
│   │   │   ├── base_rag_processor.py  # Base RAG processor interface
│   │   │   ├── modelscope_rag_processor.py  # ModelScope RAG implementation
│   │   │   └── rag_processor.py   # Main RAG processor
│   │   ├── llm/                   # Large Language Model handlers
│   │   │   ├── __init__.py
│   │   │   ├── base_llm_handler.py    # Base LLM handler interface
│   │   │   ├── ark_llm_handler.py     # Interface with VolcEngine's large model
│   │   │   ├── modelscope_llm_handler.py  # ModelScope LLM implementation
│   │   │   └── ollama_llm_handler.py  # Interface with local Ollama large model
│   │   └── data_loader.py         # Loads and formats documents from CSV
│   ├── services/                  # Business logic services
│   │   ├── __init__.py
│   │   └── audio_pipeline.py      # Core audio processing pipeline
│   └── api/                       # RESTful API endpoints
│       ├── __init__.py
│       ├── context.py             # API request context
│       ├── schemas.py             # API request/response schemas
│       └── routers/               # API route handlers
│           ├── __init__.py
│           ├── audio.py           # Audio processing API endpoints
│           └── rag.py             # RAG database management API endpoints
├── data/
│   ├── screens.csv                # Screen device information
│   ├── doors.csv                  # Door device information
│   └── videos.csv                 # Video information
├── chroma_db/
│   └── ...                        # (Auto-generated) Local vector database files
├── main.py                        # FastAPI application entry point
├── requirements.txt               # Project dependencies
└── README.md                      # Project documentation
```

## Architecture

The system follows a modular microservice architecture with the following key components:

- **FastAPI Application** (`main.py`) - Main web server with CORS middleware and API routing
- **Audio Pipeline Service** (`src/services/audio_pipeline.py`) - Core business logic orchestrating the voice processing pipeline
- **Audio Input Module** (`src/module/input/`) - Handles microphone audio streaming and decoding
- **VAD Processor** (`src/module/vad/`) - Voice Activity Detection to filter out silence using FunASR
- **ASR Processor** (`src/module/asr/`) - Speech-to-text conversion using FunASR models
- **RAG Processor** (`src/module/rag/`) - Context retrieval using ChromaDB vector database with multiple implementations
- **LLM Handlers** (`src/module/llm/`) - Interfaces with different LLM providers (VolcEngine Ark, Ollama, ModelScope)
- **Data Loader** (`src/module/data_loader.py`) - Loads knowledge base from CSV files in the `data/` directory
- **Configuration** (`src/config/`) - Centralized configuration management and logging setup
- **API Layer** (`src/api/`) - RESTful endpoints for audio processing and RAG database management

## Common Development Tasks

### Virtual Environment Setup
The project uses a `.venv` virtual environment. Always activate it before running commands:
- **Windows**: `.venv\Scripts\activate`
- **Linux/macOS**: `source .venv/bin/activate`

### Running the Application
```bash
# HTTP mode (default)
python main.py [--host HOST] [--port PORT]

# HTTPS/WSS mode (recommended for production and mixed content resolution)
python main.py --ssl-certfile frontend/vue-project/morph_icu.pem --ssl-keyfile frontend/vue-project/morph_icu.key [--host HOST] [--port PORT]
```

Default: `http://0.0.0.0:5000` (HTTP) or `https://0.0.0.0:5000` (HTTPS)

### HTTPS/WSS Support
The backend now supports HTTPS and WebSocket Secure (WSS) connections:
- Automatically detects SSL certificates in `frontend/vue-project/` directory
- Resolves mixed content issues when frontend is served over HTTPS
- Supports both局域网 and production deployments
- Maintains backward compatibility with HTTP/WS mode

### API Endpoints
The service provides the following RESTful endpoints:
- `GET /` - Health check
- Audio processing endpoints (via `src/api/routers/audio.py`)
- RAG management endpoints (via `src/api/routers/rag.py`)

API documentation is available at:
- Interactive docs: `[http|https]://localhost:5000/docs`
- ReDoc: `[http|https]://localhost:5000/redoc`

The protocol (HTTP/HTTPS) depends on whether SSL certificates were provided when starting the application.

### Testing
Currently, there are no dedicated test files in the project. Testing is performed by running the application and using the API endpoints directly.

### Configuration
- Edit `src/config/config.py` to configure API keys, model paths, and system prompts
- The application uses loguru for logging, configured in `src/config/logging_config.py`

### Configuration File Priority
The system loads configuration files in the following priority order:
1. **`config/config.toml`** - User's actual configuration (recommended)
2. **`config/config.example.toml`** - Fallback to example configuration
3. **Built-in defaults** - Code defaults if no config files exist

**Environment Variable Override**: Use `CONFIG_FILE` environment variable to specify a custom config file path.

## Key Files and Directives

- **Application Entry Point**: `main.py` - FastAPI application with lifespan management
- **Core Business Logic**: `src/services/audio_pipeline.py` - Main orchestration of the voice processing pipeline
- **Configuration**: `src/config/config.py` contains all API keys, model paths, and system prompts
- **Knowledge Base**: `data/*.csv` files contain screens, doors, and video information
- **Vector Database**: `chroma_db/` (auto-generated) stores embedded knowledge
- **API Routes**: `src/api/routers/` contains all RESTful endpoint implementations

## Dependencies
Main dependencies include:
- fastapi, uvicorn (for web API)
- funasr (for ASR and VAD)
- pyaudio (for audio input)
- torch (for ML inference)
- langchain, chromadb (for RAG)
- ollama (for local LLM)
- pandas (for data processing)
- loguru (for logging)

The project uses a pre-configured `.venv` virtual environment. If you need to recreate it:
1. Create virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/macOS)
3. Install dependencies: `pip install -r requirements.txt`