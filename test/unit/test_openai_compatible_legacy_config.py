from unittest.mock import patch

from pydantic import SecretStr

from src.config.config import LLMSettings, RAGSettings
from src.module.llm.openai_compatible_llm_handler import OpenAICompatibleLLMHandler
from src.module.rag.openai_compatible_rag_processor import OpenAICompatibleRAGProcessor


def _llm_handler(settings: LLMSettings) -> OpenAICompatibleLLMHandler:
    handler = object.__new__(OpenAICompatibleLLMHandler)
    handler.settings = settings
    return handler


def _rag_processor(settings: RAGSettings) -> OpenAICompatibleRAGProcessor:
    processor = object.__new__(OpenAICompatibleRAGProcessor)
    processor.settings = settings
    return processor


def test_modelscope_llm_provider_uses_legacy_config_fields():
    settings = LLMSettings(
        provider="modelscope",
        modelscope_model="legacy-chat-model",
        modelscope_base_url="https://modelscope.example/v1",
        modelscope_api_key=SecretStr("modelscope-key"),
        openai_compatible_model="new-chat-model",
        openai_compatible_base_url="https://openai-compatible.example/v1",
        openai_compatible_api_key=SecretStr("openai-compatible-key"),
    )

    with patch(
        "src.module.llm.openai_compatible_llm_handler.ChatOpenAI"
    ) as chat_openai:
        _llm_handler(settings)._create_model()

    kwargs = chat_openai.call_args.kwargs
    assert kwargs["model"] == "legacy-chat-model"
    assert kwargs["base_url"] == "https://modelscope.example/v1"
    assert kwargs["api_key"].get_secret_value() == "modelscope-key"


def test_openai_compatible_llm_provider_uses_new_config_fields():
    settings = LLMSettings(
        provider="siliconflow",
        modelscope_model="legacy-chat-model",
        modelscope_base_url="https://modelscope.example/v1",
        modelscope_api_key=SecretStr("modelscope-key"),
        openai_compatible_model="new-chat-model",
        openai_compatible_base_url="https://openai-compatible.example/v1",
        openai_compatible_api_key=SecretStr("openai-compatible-key"),
    )

    with patch(
        "src.module.llm.openai_compatible_llm_handler.ChatOpenAI"
    ) as chat_openai:
        _llm_handler(settings)._create_model()

    kwargs = chat_openai.call_args.kwargs
    assert kwargs["model"] == "new-chat-model"
    assert kwargs["base_url"] == "https://openai-compatible.example/v1"
    assert kwargs["api_key"].get_secret_value() == "openai-compatible-key"


def test_modelscope_rag_provider_uses_legacy_fields_with_single_item_batches():
    settings = RAGSettings(
        provider="modelscope",
        modelscope_embedding_model="legacy-embedding-model",
        modelscope_base_url="https://modelscope.example/v1",
        modelscope_api_key=SecretStr("modelscope-key"),
        openai_compatible_embedding_model="new-embedding-model",
        openai_compatible_base_url="https://openai-compatible.example/v1",
        openai_compatible_api_key=SecretStr("openai-compatible-key"),
        openai_compatible_chunk_size=32,
    )

    with patch(
        "src.module.rag.openai_compatible_rag_processor.OpenAIEmbeddings"
    ) as embeddings:
        _rag_processor(settings)._create_embedding_model()

    kwargs = embeddings.call_args.kwargs
    assert kwargs["model"] == "legacy-embedding-model"
    assert kwargs["base_url"] == "https://modelscope.example/v1"
    assert kwargs["api_key"].get_secret_value() == "modelscope-key"
    assert kwargs["chunk_size"] == 1


def test_openai_compatible_rag_provider_uses_new_config_fields():
    settings = RAGSettings(
        provider="openai_compatible",
        modelscope_embedding_model="legacy-embedding-model",
        modelscope_base_url="https://modelscope.example/v1",
        modelscope_api_key=SecretStr("modelscope-key"),
        openai_compatible_embedding_model="new-embedding-model",
        openai_compatible_base_url="https://openai-compatible.example/v1",
        openai_compatible_api_key=SecretStr("openai-compatible-key"),
        openai_compatible_chunk_size=24,
    )

    with patch(
        "src.module.rag.openai_compatible_rag_processor.OpenAIEmbeddings"
    ) as embeddings:
        _rag_processor(settings)._create_embedding_model()

    kwargs = embeddings.call_args.kwargs
    assert kwargs["model"] == "new-embedding-model"
    assert kwargs["base_url"] == "https://openai-compatible.example/v1"
    assert kwargs["api_key"].get_secret_value() == "openai-compatible-key"
    assert kwargs["chunk_size"] == 24
