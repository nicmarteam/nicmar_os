from __future__ import annotations

import pytest
from src.llm.tools.models import ToolDefinition, ToolParameter, ToolCall
from src.llm.tools.registry import ToolRegistry
from src.llm.tools.executor import ToolExecutor
from src.llm.tools.executor_loop import ToolExecutorLoop
from src.llm.base_client import AbstractLLMClient, LLMResponse


class MockClientWithTool(AbstractLLMClient):
    """Client mock care simulează cererea unui tool la prima iterație și răspunsul final la a doua."""
    
    def __init__(self):
        self.call_count = 0

    def generate(self, prompt, model=None, tools=None, tool_choice="auto", tool_results=None, **kwargs):
        self.call_count += 1
        if tool_results:
            return LLMResponse(
                content=f"Rezultatul prelucrat cu succes pe baza tool-ului. Input: {prompt}",
                model="mock-model",
                provider="mock"
            )
        
        # Prima interogare: modelul cere executarea tool-ului "calc_sum"
        tc = ToolCall(tool_call_id="call_999", name="calc_sum", arguments={"x": 5, "y": 7})
        return LLMResponse(
            content=None,
            model="mock-model",
            provider="mock",
            tool_calls=[tc]
        )

    def stream(self, prompt, model=None, tools=None, tool_choice="auto", **kwargs):
        yield []


def sample_calc(x: int, y: int) -> int:
    return x + y


def test_tool_executor_loop_integration():
    ToolRegistry.clear()
    
    # Înregistrăm tool-ul în registru
    param_x = ToolParameter(name="x", type="integer", description="First arg")
    param_y = ToolParameter(name="y", type="integer", description="Second arg")
    definition = ToolDefinition(
        name="calc_sum",
        description="Calculates sum",
        parameters=[param_x, param_y],
        function=sample_calc
    )
    ToolRegistry.register(definition)

    mock_client = MockClientWithTool()
    
    # Rulăm bucla prin ToolExecutorLoop
    final_response = ToolExecutorLoop.run_loop(
        client=mock_client,
        prompt="Cat fac 5 plus 7?",
        tools=[definition]
    )

    assert final_response.content is not None
    assert "Rezultatul prelucrat" in final_response.content
    assert mock_client.call_count == 2

    ToolRegistry.clear()
