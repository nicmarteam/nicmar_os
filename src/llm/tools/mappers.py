from __future__ import annotations

from typing import Any, Dict, List
from src.llm.tools.models import ToolDefinition, ToolCall, ToolResult


class OpenAIMapper:
    """Mapper pentru conversia între obiectele de tool calling și formatul OpenAI."""

    @staticmethod
    def definition_to_openai(definition: ToolDefinition) -> Dict[str, Any]:
        properties = {}
        required = []
        
        for param in definition.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.enum:
                properties[param.name]["enum"] = param.enum
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": definition.name,
                "description": definition.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    @staticmethod
    def tool_call_from_openai(openai_tool_call: Any) -> ToolCall:
        import json
        args = openai_tool_call.function.arguments
        if isinstance(args, str):
            args = json.loads(args)

        return ToolCall(
            tool_call_id=openai_tool_call.id,
            name=openai_tool_call.function.name,
            arguments=args
        )

    @staticmethod
    def tool_result_to_openai_message(result: ToolResult) -> Dict[str, Any]:
        return {
            "role": "tool",
            "tool_call_id": result.tool_call_id,
            "content": str(result.output)
        }


class ClaudeMapper:
    """Mapper pentru conversia între obiectele de tool calling și formatul Anthropic Claude."""

    @staticmethod
    def definition_to_claude(definition: ToolDefinition) -> Dict[str, Any]:
        properties = {}
        required = []
        
        for param in definition.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            if param.enum:
                properties[param.name]["enum"] = param.enum
            if param.required:
                required.append(param.name)

        return {
            "name": definition.name,
            "description": definition.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    @staticmethod
    def tool_call_from_claude(claude_block: Any) -> ToolCall:
        return ToolCall(
            tool_call_id=claude_block.id,
            name=claude_block.name,
            arguments=claude_block.input
        )

    @staticmethod
    def tool_result_to_claude_message(result: ToolResult) -> Dict[str, Any]:
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": result.tool_call_id,
                    "content": str(result.output),
                    "is_error": result.is_error
                }
            ]
        }
