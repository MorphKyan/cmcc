
import pytest
from unittest.mock import MagicMock, patch
from src.config.config import AppSettings, VADSettings, FunASRSettings, RAGSettings, LLMSettings

# Test successful config retrieval
def test_get_current_config(client):
    """
    Test GET /config/current endpoint for successful config retrieval.
    Verifies that the response structure matches expected keys and values,
    and specifically ensures 'volcengine' is absent.
    """
    # Mock settings to return deterministic values
    mock_settings = MagicMock(spec=AppSettings)
    mock_settings.vad = VADSettings(
        chunk_size=1024,
        sample_rate=16000,
        model="test-vad-model",
        max_single_segment_time=1000,
        save_audio_segments=False
    )
    mock_settings.asr = FunASRSettings(
        model="test-asr-model",
        language="zh",
        use_itn=False,
        batch_size_s=300.0,
        merge_vad=False,
        merge_length_s=10.0
    )
    mock_settings.rag = RAGSettings(
        provider="mock-rag-provider",
        chroma_db_dir="/tmp/chroma",
        top_k_results=5,
        ollama_base_url="http://mock-ollama:11434",
        ollama_embedding_model="mock-embedding-model",
        modelscope_embedding_model="mock-ms-embedding",
        modelscope_base_url="http://mock-ms:8000",        
    )
    # Ensure data settings are mocked appropriately if needed, 
    # though we can rely on default DataSettings if we don't mock it explicitly.
    # But since we are mocking the whole settings object's fields, let's mock data too or at least the attribute.
    from src.config.config import DataSettings
    mock_settings.data = DataSettings(media_data_path="/tmp/videos.csv")

    mock_settings.llm = LLMSettings(
        provider="mock-llm-provider",
        ollama_model="mock-ollama-chat",
        ollama_base_url="http://mock-ollama:11434",
        modelscope_model="mock-ms-chat",
        modelscope_base_url="http://mock-ms:8000",
        max_validation_retries=2,
        retry_delay=0.5,
        request_timeout=5,
        connection_timeout=5,
    )

    # Patch the get_settings dependency
    with patch("src.api.routers.config.get_settings", return_value=mock_settings):
        response = client.get("/config/current")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        config_data = data["data"]
        
        # Verify top-level keys
        assert "vad" in config_data
        assert "asr" in config_data
        assert "rag" in config_data
        assert "llm" in config_data
        assert "volcengine" not in config_data  # Ensure this is gone

        # Verify specific values to ensure correct mapping
        assert config_data["vad"]["model"] == "test-vad-model"
        assert config_data["asr"]["model"] == "test-asr-model"
        assert config_data["rag"]["provider"] == "mock-rag-provider"
        assert config_data["llm"]["provider"] == "mock-llm-provider"


# Test error handling
def test_get_current_config_error(client):
    """
    Test GET /config/current endpoint when an internal error occurs.
    """
    with patch("src.api.routers.config.get_settings", side_effect=Exception("Config load failed")):
        response = client.get("/config/current")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Config load failed" in data["detail"]
