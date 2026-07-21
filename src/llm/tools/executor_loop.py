from __future__ import annotations

import logging
from typing import Any, List, Optional
from src.llm.base_client import LLMResponse
from src.llm.tools.models import ToolResult
from src.llm.tools.executor import ToolExecutor

logger = logging.getLogger(__name__)


class ToolExecutorLoop:
    """Gestioneaza ciclul complet de executie in bucla pentru tool-uri (Tool Calling Loop)."""

    @staticmethod
    def run_loop(
        client: Any,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Any = "auto",
        max_iterations: int = 5,
        **kwargs: Any
    ) -> LLMResponse:
        """Ruleaza generate() si executa automat tool-urile cerute de LLM pana la raspunsul final."""
        
        tool_results: Optional[List[ToolResult]] = None
        current_response: Optional[LLMResponse] = None

        for iteration in range(max_iterations):
            logger.info(f"ToolExecutorLoop: Iteratia {iteration + 1} / {max_iterations}")
            
            current_response = client.generate(
                prompt=prompt,
                model=model,
                tools=tools,
                tool_choice=tool_choice,
                tool_results=tool_results,
                **kwargs
            )

            # Daca modelul nu cere niciun tool, ne oprim si returnam raspunsul
            if not current_response.has_tool_calls():
                return current_response

            # Executam fiecare tool cerut de model
            tool_results = []
            for tool_call in current_response.tool_calls:
                logger.info(f"Executare tool cerut de LLM: {tool_call.name} (ID: {tool_call.tool_call_id})")
                result = ToolExecutor.execute(tool_call)
                tool_results.append(result)

        logger.warning("ToolExecutorLoop a atins numarul maxim de iteratii fara a se incheia.")
        return current_response if current_response else LLMResponse(content="Max iterations reached without final response.", model=model or "unknown", provider="unknown")
