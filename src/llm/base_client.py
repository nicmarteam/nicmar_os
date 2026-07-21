from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Optional, Type
from pydantic import BaseModel
from src.llm.tools.models import ToolCall, ToolResult


@dataclass
class LLMResponse:
    content: Optional[str]
    model: str
    provider: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    raw_response: Any = None

    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


@dataclass
class LLMStreamChunk:
    delta: str
    model: str
    provider: str
    raw_chunk: Any = None


class AbstractLLMClient(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Any = "auto",
        tool_results: Optional[List[ToolResult]] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        pass

    @abstractmethod
    def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Any = "auto",
        **kwargs: Any
    ) -> Iterable[LLMStreamChunk]:
        pass
