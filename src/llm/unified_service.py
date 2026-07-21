from __future__ import annotations

import logging
from typing import Any, Iterable, List, Optional, Type, Union
from pydantic import BaseModel
from src.llm.provider_factory import ProviderFactory
from src.llm.base_client import LLMResponse, LLMStreamChunk
from src.llm.tools.executor_loop import ToolExecutorLoop
from src.llm.structured.models import StructuredResponse
from src.llm.structured.validator import StructuredOutputValidator

logger = logging.getLogger(__name__)


class UnifiedLLMService:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider_name = provider or "openai"
        self.default_model = model
        self._client = ProviderFactory.get_client(self.provider_name)

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Any = "auto",
        max_iterations: int = 5,
        response_schema: Optional[Type[BaseModel]] = None,
        **kwargs: Any
    ) -> Union[LLMResponse, StructuredResponse]:
        target_model = model or self.default_model

        if tools:
            response = ToolExecutorLoop.run_loop(
                client=self._client,
                prompt=prompt,
                model=target_model,
                tools=tools,
                tool_choice=tool_choice,
                max_iterations=max_iterations,
                response_schema=response_schema,
                **kwargs
            )
        else:
            response = self._client.generate(
                prompt=prompt,
                model=target_model,
                response_schema=response_schema,
                **kwargs
            )

        if response_schema:
            return StructuredOutputValidator.parse_and_validate(
                raw_content=response.content or "",
                schema_cls=response_schema,
                model=response.model,
                provider=response.provider,
                raw_response=response.raw_response
            )

        return response

    def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Any = "auto",
        **kwargs: Any
    ) -> Iterable[LLMStreamChunk]:
        target_model = model or self.default_model
        return self._client.stream(
            prompt=prompt,
            model=target_model,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        )
