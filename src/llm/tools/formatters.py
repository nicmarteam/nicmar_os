from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.llm.tools.mappers import OpenAIMapper, ClaudeMapper


class OpenAIFormatter:
    """Formatează uneltele în formatul nativ acceptat de OpenAI API."""

    @staticmethod
    def format_tools(tools: Optional[List[Any]]) -> Optional[List[Dict[str, Any]]]:
        if not tools:
            return None
        return [OpenAIMapper.definition_to_openai(t) for t in tools]

    @staticmethod
    def format_tool_choice(tool_choice: Any) -> Any:
        return tool_choice


class ClaudeFormatter:
    """Formatează uneltele în formatul nativ acceptat de Anthropic Claude API."""

    @staticmethod
    def format_tools(tools: Optional[List[Any]]) -> Optional[List[Dict[str, Any]]]:
        if not tools:
            return None
        return [ClaudeMapper.definition_to_claude(t) for t in tools]

    @staticmethod
    def format_tool_choice(tool_choice: Any) -> Any:
        if tool_choice == "auto":
            return {"type": "auto"}
        elif tool_choice == "any":
            return {"type": "any"}
        return tool_choice
