from __future__ import annotations

from typing import Any
import pytest

from src.llm.streaming.claude_mapper import ClaudeStreamMapper
from src.llm.streaming.openai_mapper import OpenAIStreamMapper
from src.llm.streaming.models import LLMStreamChunk


# --- Obiecte Fake dedicate pentru Contract Tests ---

class FakeClaudeDelta:
    def __init__(self, delta_type: str = "text_delta", text: str = ""):
        self.type = delta_type
        self.text = text


class FakeClaudeEvent:
    def __init__(self, event_type: str, model: str, delta: Any = None):
        self.type = event_type
        self.model = model
        self.delta = delta


class FakeOpenAIDelta:
    def __init__(self, content: str | None = None):
        self.content = content


class FakeOpenAIChoice:
    def __init__(self, delta: FakeOpenAIDelta, finish_reason: str | None = None):
        self.delta = delta
        self.finish_reason = finish_reason


class FakeOpenAIEvent:
    def __init__(self, choices: list[Any], model: str):
        self.choices = choices
        self.model = model


# --- Fixture-uri de date pentru fiecare mapper ---

@pytest.fixture(params=[
    "claude",
    "openai"
])
def mapper_setup(request):
    provider = request.param
    if provider == "claude":
        mapper = ClaudeStreamMapper()
        model_name = "claude-3-5-sonnet-latest"
        
        # Eveniment de text normal
        text_event = FakeClaudeEvent(
            event_type="content_block_delta",
            model=model_name,
            delta=FakeClaudeDelta(delta_type="text_delta", text="Hello contract")
        )
        # Eveniment gol
        empty_event = FakeClaudeEvent(
            event_type="message_start",
            model=model_name
        )
        # Eveniment final
        stop_event = FakeClaudeEvent(
            event_type="message_stop",
            model=model_name
        )
        
        return {
            "provider": "anthropic",
            "mapper": mapper,
            "model": model_name,
            "text_event": text_event,
            "empty_event": empty_event,
            "stop_event": stop_event,
            "expected_finish_reason": "end_turn"
        }
        
    else:
        mapper = OpenAIStreamMapper()
        model_name = "gpt-4o"
        
        # Eveniment de text normal
        text_event = FakeOpenAIEvent(
            choices=[FakeOpenAIChoice(delta=FakeOpenAIDelta(content="Hello contract"), finish_reason=None)],
            model=model_name
        )
        # Eveniment gol
        empty_event = FakeOpenAIEvent(
            choices=[FakeOpenAIChoice(delta=FakeOpenAIDelta(content=None), finish_reason=None)],
            model=model_name
        )
        # Eveniment final
        stop_event = FakeOpenAIEvent(
            choices=[FakeOpenAIChoice(delta=FakeOpenAIDelta(content=None), finish_reason="stop")],
            model=model_name
        )
        
        return {
            "provider": "openai",
            "mapper": mapper,
            "model": model_name,
            "text_event": text_event,
            "empty_event": empty_event,
            "stop_event": stop_event,
            "expected_finish_reason": "stop"
        }


# --- Testele de Contract Unificate ---

def test_contract_returns_llm_stream_chunk(mapper_setup):
    mapper = mapper_setup["mapper"]
    event = mapper_setup["text_event"]
    
    chunk = mapper.map(event, model=mapper_setup["model"], sequence=1)
    assert isinstance(chunk, LLMStreamChunk)


def test_contract_provider_is_correct(mapper_setup):
    mapper = mapper_setup["mapper"]
    event = mapper_setup["text_event"]
    
    chunk = mapper.map(event, model=mapper_setup["model"], sequence=1)
    assert chunk.provider == mapper_setup["provider"]


def test_contract_model_is_preserved(mapper_setup):
    mapper = mapper_setup["mapper"]
    event = mapper_setup["text_event"]
    target_model = mapper_setup["model"]
    
    chunk = mapper.map(event, model=target_model, sequence=1)
    assert chunk.model == target_model


def test_contract_sequence_is_preserved(mapper_setup):
    mapper = mapper_setup["mapper"]
    event = mapper_setup["text_event"]
    
    chunk = mapper.map(event, model=mapper_setup["model"], sequence=77)
    assert chunk.sequence == 77


def test_contract_raw_is_preserved(mapper_setup):
    mapper = mapper_setup["mapper"]
    event = mapper_setup["text_event"]
    
    chunk = mapper.map(event, model=mapper_setup["model"], sequence=1)
    assert chunk.raw is event


def test_contract_text_event_produces_running_state(mapper_setup):
    mapper = mapper_setup["mapper"]
    event = mapper_setup["text_event"]
    
    chunk = mapper.map(event, model=mapper_setup["model"], sequence=1)
    assert chunk.delta == "Hello contract"
    assert chunk.finished is False


def test_contract_empty_event_produces_empty_delta_safe(mapper_setup):
    mapper = mapper_setup["mapper"]
    event = mapper_setup["empty_event"]
    
    chunk = mapper.map(event, model=mapper_setup["model"], sequence=1)
    assert chunk.delta == ""
    assert chunk.finished is False


def test_contract_final_event_produces_finished_state(mapper_setup):
    mapper = mapper_setup["mapper"]
    event = mapper_setup["stop_event"]
    
    chunk = mapper.map(event, model=mapper_setup["model"], sequence=1)
    assert chunk.finished is True
    assert chunk.finish_reason == mapper_setup["expected_finish_reason"]
