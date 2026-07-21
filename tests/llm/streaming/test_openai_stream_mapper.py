from __future__ import annotations

from typing import Any
import pytest

from src.llm.streaming.openai_mapper import OpenAIStreamMapper
from src.llm.streaming.models import LLMStreamChunk


# --- Clase Fake pentru simularea structurii OpenAI ---

class FakeDelta:
    def __init__(self, content: str | None = None):
        self.content = content


class FakeChoice:
    def __init__(self, delta: FakeDelta | None = None, finish_reason: str | None = None):
        self.delta = delta
        self.finish_reason = finish_reason


class FakeOpenAIChunk:
    def __init__(self, choices: list[Any], model: str = "gpt-4o"):
        self.choices = choices
        self.model = model


# --- Testele unitare pentru OpenAIStreamMapper ---

def test_maps_text_delta():
    delta = FakeDelta(content="Salut")
    choice = FakeChoice(delta=delta, finish_reason=None)
    event = FakeOpenAIChunk(choices=[choice], model="gpt-4o")

    chunk = OpenAIStreamMapper.map(event, model="gpt-4o", sequence=1)

    assert isinstance(chunk, LLMStreamChunk)
    assert chunk.delta == "Salut"
    assert chunk.finished is False
    assert chunk.finish_reason is None
    assert chunk.sequence == 1
    assert chunk.provider == "openai"
    assert chunk.model == "gpt-4o"
    assert chunk.raw is event


def test_maps_empty_delta():
    delta = FakeDelta(content=None)
    choice = FakeChoice(delta=delta, finish_reason=None)
    event = FakeOpenAIChunk(choices=[choice], model="gpt-4o")

    chunk = OpenAIStreamMapper.map(event, model="gpt-4o", sequence=2)

    assert chunk.delta == ""
    assert chunk.finished is False
    assert chunk.sequence == 2
    assert chunk.raw is event


def test_maps_finish_reason():
    choice = FakeChoice(delta=FakeDelta(content=None), finish_reason="stop")
    event = FakeOpenAIChunk(choices=[choice], model="gpt-4o")

    chunk = OpenAIStreamMapper.map(event, model="gpt-4o", sequence=3)

    assert chunk.delta == ""
    assert chunk.finished is True
    assert chunk.finish_reason == "stop"
    assert chunk.sequence == 3


def test_preserves_sequence():
    choice = FakeChoice(delta=FakeDelta(content="Test"), finish_reason=None)
    event = FakeOpenAIChunk(choices=[choice], model="gpt-4o")

    chunk = OpenAIStreamMapper.map(event, model="gpt-4o", sequence=42)

    assert chunk.sequence == 42


def test_preserves_raw_event():
    choice = FakeChoice(delta=FakeDelta(content="Raw"), finish_reason=None)
    event = FakeOpenAIChunk(choices=[choice], model="gpt-4o")

    chunk = OpenAIStreamMapper.map(event, model="gpt-4o", sequence=1)

    assert chunk.raw is event


def test_sets_provider_to_openai():
    choice = FakeChoice(delta=FakeDelta(content="A"), finish_reason=None)
    event = FakeOpenAIChunk(choices=[choice], model="gpt-4o")

    chunk = OpenAIStreamMapper.map(event, model="gpt-4o", sequence=1)

    assert chunk.provider == "openai"


def test_sets_model():
    choice = FakeChoice(delta=FakeDelta(content="A"), finish_reason=None)
    event = FakeOpenAIChunk(choices=[choice], model="gpt-4o-mini")

    chunk = OpenAIStreamMapper.map(event, model="gpt-4o-mini", sequence=1)

    assert chunk.model == "gpt-4o-mini"
