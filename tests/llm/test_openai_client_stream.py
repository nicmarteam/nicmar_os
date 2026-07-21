from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from src.llm.openai_client import OpenAIClient
from src.llm.streaming.models import LLMStreamChunk


@patch("openai.OpenAI")
def test_openai_client_stream_yields_chunks(mock_openai_class):
    # Mockuim evenimentul brut returnat de SDK-ul OpenAI
    mock_delta = MagicMock()
    mock_delta.content = "Salut OpenAI"
    
    mock_choice = MagicMock()
    mock_choice.delta = mock_delta
    mock_choice.finish_reason = None

    mock_event = MagicMock()
    mock_event.choices = [mock_choice]
    mock_event.model = "gpt-4o"

    mock_sdk_instance = mock_openai_class.return_value
    mock_sdk_instance.chat.completions.create.return_value = [mock_event]

    client = OpenAIClient(api_key="fake-key")
    chunks = list(client.stream("Test prompt"))

    assert len(chunks) == 1
    assert isinstance(chunks[0], LLMStreamChunk)
    assert chunks[0].delta == "Salut OpenAI"
    assert chunks[0].sequence == 1
    assert chunks[0].provider == "openai"
    assert chunks[0].model == "gpt-4o"
