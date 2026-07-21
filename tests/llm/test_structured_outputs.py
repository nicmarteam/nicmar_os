from __future__ import annotations

import pytest
from pydantic import BaseModel, Field
from src.llm.base_client import AbstractLLMClient, LLMResponse
from src.llm.structured.validator import StructuredOutputValidator
from src.llm.unified_service import UnifiedLLMService
from src.llm.provider_factory import ProviderFactory


class LeadSample(BaseModel):
    name: str = Field(..., description="Numele lead-ului")
    score: int = Field(..., description="Scorul de calificare de la 1 la 10")
    qualified: bool = Field(..., description="Dacă lead-ul este calificat")


class MockClientForStructured(AbstractLLMClient):
    def generate(self, prompt, model=None, tools=None, tool_choice="auto", tool_results=None, response_schema=None, **kwargs):
        json_content = '{"name": "Maria Popescu", "score": 9, "qualified": true}'
        return LLMResponse(
            content=json_content,
            model="mock-structured-model",
            provider="mock"
        )

    def stream(self, prompt, model=None, tools=None, tool_choice="auto", **kwargs):
        yield []


def test_structured_output_validation():
    raw_json = '```json\n{"name": "Ion Ionescu", "score": 8, "qualified": true}\n```'
    
    result = StructuredOutputValidator.parse_and_validate(
        raw_content=raw_json,
        schema_cls=LeadSample,
        model="test-model",
        provider="mock"
    )

    assert isinstance(result.parsed_data, LeadSample)
    assert result.parsed_data.name == "Ion Ionescu"
    assert result.parsed_data.score == 8
    assert result.parsed_data.qualified is True


def test_unified_service_with_structured_output(monkeypatch):
    # Înlocuim clientul din ProviderFactory cu Mock-ul nostru
    monkeypatch.setattr(ProviderFactory, "get_client", lambda provider_name, api_key=None, timeout=None: MockClientForStructured())

    service = UnifiedLLMService(provider="openai")
    
    response = service.generate(
        prompt="Analizează acest lead.",
        response_schema=LeadSample
    )

    assert hasattr(response, "parsed_data")
    assert response.parsed_data.name == "Maria Popescu"
    assert response.parsed_data.score == 9
    assert response.parsed_data.qualified is True
