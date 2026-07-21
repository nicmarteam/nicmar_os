from __future__ import annotations

import pytest
from src.llm.tools.models import ToolDefinition, ToolParameter, ToolCall, ToolResult
from src.llm.tools.registry import ToolRegistry
from src.llm.tools.executor import ToolExecutor
from src.llm.tools.mappers import OpenAIMapper, ClaudeMapper


def sample_adder(a: int, b: int) -> int:
    return a + b


def test_registry_and_executor():
    ToolRegistry.clear()
    
    param_a = ToolParameter(name="a", type="integer", description="First number")
    param_b = ToolParameter(name="b", type="integer", description="Second number")
    
    definition = ToolDefinition(
        name="add",
        description="Adds two numbers",
        parameters=[param_a, param_b],
        function=sample_adder
    )
    
    ToolRegistry.register(definition)
    
    # Verificăm că registrul returnează tool-ul corect
    fetched = ToolRegistry.get("add")
    assert fetched.name == "add"
    
    # Testăm executarea tool-ului prin ToolExecutor
    tool_call = ToolCall(tool_call_id="call_123", name="add", arguments={"a": 10, "b": 32})
    result = ToolExecutor.execute(tool_call)
    
    assert result.tool_call_id == "call_123"
    assert result.name == "add"
    assert result.output == 42
    assert result.is_error is False

    ToolRegistry.clear()


def test_openai_mapper():
    param = ToolParameter(name="query", type="string", description="Search query")
    definition = ToolDefinition(name="search", description="Search the web", parameters=[param])
    
    openai_def = OpenAIMapper.definition_to_openai(definition)
    assert openai_def["type"] == "function"
    assert openai_def["function"]["name"] == "search"
    assert openai_def["function"]["parameters"]["properties"]["query"]["type"] == "string"


def test_claude_mapper():
    param = ToolParameter(name="location", type="string", description="City name")
    definition = ToolDefinition(name="get_weather", description="Get weather", parameters=[param])
    
    claude_def = ClaudeMapper.definition_to_claude(definition)
    assert claude_def["name"] == "get_weather"
    assert claude_def["input_schema"]["properties"]["location"]["type"] == "string"
