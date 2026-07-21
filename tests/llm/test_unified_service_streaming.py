from __future__ import annotations

import os
import pytest
from unittest.mock import patch, MagicMock

from src.llm.unified_service import UnifiedLLMService
from src.llm.base_client import LLMResponse, LLMStreamChunk


@patch("src.llm.provider_factory.ProviderFactory.get_client")
def test_unified_service_generate_delegates(mock_get_client):
    mock_client = MagicMock()
    mock_response = LLMResponse(content="Hello from test", model="gpt-4o", provider="openai")
    mock_client.generate.return_value = mock_response
    mock_get_client.return_value = mock_client

    service = UnifiedLLMService(default_provider="openai")
    response = service.generate(prompt="Test prompt", model="gpt-4o")

    assert response.content == "Hello from test"
    mock_get_client.assert_called_once_with(provider_name="openai", api_key=None, timeout=None)
    mock_client.generate.assert_called_once_with(prompt="Test prompt", model="gpt-4o")


@patch("src.llm.provider_factory.ProviderFactory.get_client")
def test_unified_service_stream_delegates(mock_get_client):
    mock_client = MagicMock()
    chunks = [
        LLMStreamChunk(delta="Hello", model="claude-3-5-sonnet-20241022", provider="anthropic"),
        LLMStreamChunk(delta=" World", model="claude-3-5-sonnet-20241022", provider="anthropic")
    ]
    mock_client.stream.return_value = iter(chunks)
    mock_get_client.return_value = mock_client

    service = UnifiedLLMService(default_provider="anthropic")
    stream_generator = service.stream(prompt="Stream prompt")

    received_chunks = list(stream_generator)
    assert len(received_chunks) == 2
    assert received_chunks[0].delta == "Hello"
    assert received_chunks[1].delta == " World"
    
    mock_get_client.assert_called_once_with(provider_name="anthropic", api_key=None, timeout=None)
    mock_client.stream.assert_called_once_with(prompt="Stream prompt", model=None)
