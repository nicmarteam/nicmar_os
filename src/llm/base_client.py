from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Optional


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    raw_response: Any = None


@dataclass
class LLMStreamChunk:
    delta: str
    model: str
    provider: str
    raw_chunk: Any = None


class AbstractLLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: Optional[str] = None, **kwargs: Any) -> LLMResponse:
        pass

    @abstractmethod
    def stream(self, prompt: str, model: Optional[str] = None, **kwargs: Any) -> Iterable[LLMStreamChunk]:
        pass
