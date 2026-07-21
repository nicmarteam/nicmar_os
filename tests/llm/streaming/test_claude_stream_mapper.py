from __future__ import annotations

from typing import Any
import pytest

from src.llm.streaming.claude_mapper import ClaudeStreamMapper
from src.llm.streaming.models import LLMStreamChunk


# --- Clase Fake pentru simularea evenimentelor Anthropic ---

class FakeDelta:
    def __init__(self, delta_type: str, text: str = "", stop_reason: str | None = None):
        self.type = delta_type
        self.text = text
        self.stop_reason = stop_reason


class FakeAnthropicEvent:
    def __init__(self, event_type: str, model: str = "claude-3-5-sonnet-latest", delta: Any = None):
        self.type = event_type
        self.model = model
        self.delta = delta


# --- Testele unitare pentru ClaudeStreamMapper ---

def test_claude_mapper_normal_text_delta():
    # 1. Eveniment fals pentru o bucată normală de text
    delta_obj = FakeDelta(delta_type="text_delta", text="Salut")
    event = FakeAnthropicEvent(event_type="content_block_delta", model="claude-3-5-sonnet-latest", delta=delta_obj)
    
    mapper = ClaudeStreamMapper()
    chunk = mapper.map(event, sequence=1)

    assert isinstance(chunk, LLMStreamChunk)
    assert chunk.delta == "Salut"
    assert chunk.finished is False
    assert chunk.finish_reason is None
    assert chunk.sequence == 1
    assert chunk.provider == "anthropic"
    assert chunk.model == "claude-3-5-sonnet-latest"
    assert chunk.raw is event


def test_claude_mapper_empty_delta():
    # 2. Eveniment fals cu delta goală sau lipsă
    event = FakeAnthropicEvent(event_type="message_start", model="claude-3-5-sonnet-latest")
    
    mapper = ClaudeStreamMapper()
    chunk = mapper.map(event, sequence=5)

    assert chunk.delta == ""
    assert chunk.finished is False
    assert chunk.sequence == 5
    assert chunk.raw is event


def test_claude_mapper_message_stop():
    # 3. Eveniment de finalizare a mesajului
    event = FakeAnthropicEvent(event_type="message_stop", model="claude-3-5-sonnet-latest")
    
    mapper = ClaudeStreamMapper()
    chunk = mapper.map(event, sequence=12)

    assert chunk.delta == ""
    assert chunk.finished is True
    assert chunk.finish_reason == "end_turn"
    assert chunk.sequence == 12
    assert chunk.raw is event


def test_claude_mapper_custom_sequence():
    # 5 & 6 & 7. Verificăm că secvența, providerul și modelul sunt respectate riguros
    delta_obj = FakeDelta(delta_type="text_delta", text="Test")
    event = FakeAnthropicEvent(event_type="content_block_delta", model="claude-3-opus", delta=delta_obj)
    
    mapper = ClaudeStreamMapper()
    chunk = mapper.map(event, sequence=15)

    assert chunk.sequence == 15
    assert chunk.provider == "anthropic"
    assert chunk.model == "claude-3-opus"
