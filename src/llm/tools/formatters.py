from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.llm.tools.models import ToolDefinition
from src.llm.tools.mappers import OpenAIMapper, ClaudeMapper


class OpenAIFormatter:
    """Formatter responsabil cu pregătirea uneltelor pentru payload-ul OpenAI."""

    @staticmethod
    py_format_tools = lambda tools: [OpenAIMapper.definition_to_openai(t) for t in tools] if tools else None

    @staticmethod
    def format_tools(tools: Optional[List[ToolDefinition]]) -> Optional[List[Dict[str, Any]]]:
        if not tools:
            return None
        return [OpenAIMapper.definition_to_openai(tool) for tool in tools]

    @staticmethod
    def format_tool_choice(tool_choice: Any) -> Any:
        # OpenAI acceptă "auto", "none", "required" sau un dict specific pentru funcție
        return tool_choice


class ClaudeFormatter:
    """Formatter responsabil cu pregătirea uneltelor pentru payload-ul Anthropic Claude."""

    @staticmethod
    def format_tools(tools: Optional[List[ToolDefinition]]) -> Optional[List[Dict[str, Any]]]:
        if not tools:
            return None
        return [ClaudeMapper.definition_to_claude(tool) for tool in tools]

    @staticmethod
    def format_tool_choice(tool_choice: Any) -> Any:
        if tool_choice == "auto":
            return {"type": "auto"}
        elif tool_choice == "any" or tool_choice == "required":
            return {"type": "any"}
        elif tool_choice == "none":
            return None
        return tool_choice
