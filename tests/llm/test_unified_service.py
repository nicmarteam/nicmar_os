from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from src.llm.unified_service import UnifiedLLMService
from src.llm.streaming.models import LLMStreamChunk


@patch("src.llm.provider_factory.ProviderFactory.get_client")
def test_unified_service_generate_delegates_to_client(mock_get_client):
    mock_client = MagicMock()
    mock_client.generate.return_value = "Răspuns unificat"
    mock_get_client.return_value = mock_client

    service = UnifiedLLMService(default_provider="openai")
    result = service.generate("Salut", provider="openai")

    assert result == "Răspuns unificat"
    mock_get_client.assert_called_once_with("openai")
    mock_client.generate.assert_called_once_with("Salut", max_tokens=1024)


@patch("src.llm.provider_factory.ProviderFactory.get_client")
def test_unified_service_stream_delegates_to_client(mock_get_client):
    mock_client = MagicMock()
    chunk = LLMStreamChunk(delta="Test", sequence=1, provider="openai", model="gpt-4o")
    mock_client.stream.return_value = iter([chunk])
    mock_get_client.return_value = mock_client

    service = UnifiedLLMService(default_provider="openai")
    chunks = list(service.stream("Salut stream"))

    assert len(chunks) == 1
    assert chunks[0].delta == "Test"
    mock_get_client.assert_called_once_with("openai")
    mock_client.stream.assert_called_once_with("Salut stream", max_tokens=1024)
