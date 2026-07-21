from __future__ import annotations

import logging
from typing import Any, Iterable, List, Optional
from src.llm.factory import LLMProviderFactory
from src.llm.base_client import LLMResponse, LLMStreamChunk
from src.llm.tools.executor_loop import ToolExecutorLoop

logger = logging.getLogger(__name__)


class UnifiedLLMService:
    """Serviciul unificat pentru interogarea modelelor LLM, cu suport complet pentru streaming si tool calling."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider_name = provider
        self.default_model = model
        self._client = LLMProviderFactory.create(provider)

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Any = "auto",
        max_iterations: int = 5,
        **kwargs: Any
    ) -> LLMResponse:
        """Generează un răspuns, incluzând suport pentru bucla automată de tool calling."""
        target_model = model or self.default_model

        if tools:
            logger.info("S-au detectat tool-uri; se activeaza ToolExecutorLoop.")
            return ToolExecutorLoop.run_loop(
                client=self._client,
                prompt=prompt,
                model=target_model,
                tools=tools,
                tool_choice=tool_choice,
                max_iterations=max_iterations,
                **kwargs
            )

        return self._client.generate(prompt=prompt, model=target_model, **kwargs)

    def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Any = "auto",
        **kwargs: Any
    ) -> Iterable[LLMStreamChunk]:
        """Transmite răspunsul în mod streaming."""
        target_model = model or self.default_model
        return self._client.stream(
            prompt=prompt,
            model=target_model,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        )
