from __future__ import annotations

import logging
from typing import Any
from src.llm.tools.models import ToolCall, ToolResult
from src.llm.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executor responsabil cu rularea sigură a unui ToolCall folosind ToolRegistry."""

    @staticmethod
    def execute(tool_call: ToolCall) -> ToolResult:
        """Execută funcția asociată unui ToolCall și returnează rezultatul."""
        try:
            definition = ToolRegistry.get(tool_call.name)
        except KeyError as e:
            logger.error(f"Eroare execuție tool: {e}")
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                name=tool_call.name,
                output=str(e),
                is_error=True
            )

        if not definition.function:
            error_msg = f"Tool-ul '{tool_call.name}' nu are nicio funcție atașată pentru execuție."
            logger.error(error_msg)
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                name=tool_call.name,
                output=error_msg,
                is_error=True
            )

        try:
            # Apelăm funcția Python mapând argumentele primite din dicționar
            output = definition.function(**tool_call.arguments)
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                name=tool_call.name,
                output=output,
                is_error=False
            )
        except Exception as e:
            logger.exception(f"Excepție în timpul execuției tool-ului '{tool_call.name}': {e}")
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                name=tool_call.name,
                output=str(e),
                is_error=True
            )
