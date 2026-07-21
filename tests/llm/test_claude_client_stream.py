from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from src.llm.claude_client import ClaudeClient
from src.llm.streaming.models import LLMStreamChunk


class FakeStreamContextManager:
    def __init__(self, events):
        self.events = events

    def __enter__(self):
        return iter(self.events)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@patch("anthropic.Anthropic")
def test_claude_client_stream_yields_chunks(mock_anthropic_class):
    # Mockuim evenimentele brute returnate de SDK-ul Anthropic
    mock_event = MagicMock()
    mock_event.type = "content_block_delta"
    mock_event.delta.text = "Salut Claude"
    mock_event.model = "claude-3-5-sonnet-latest"

    mock_sdk_instance = mock_anthropic_class.return_value
    mock_sdk_instance.messages.stream.return_value = FakeStreamContextManager([mock_event])

    client = ClaudeClient(api_key="fake-key")
    chunks = list(client.stream("Test prompt"))

    assert len(chunks) == 1
    assert isinstance(chunks[0], LLMStreamChunk)
    assert chunks[0].delta == "Salut Claude"
    assert chunks[0].sequence == 1
    assert chunks[0].provider == "anthropic"
    assert chunks[0].model == "claude-3-5-sonnet-latest"
