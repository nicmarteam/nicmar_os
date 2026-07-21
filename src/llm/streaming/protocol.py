from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from src.llm.streaming.models import LLMStreamChunk


@runtime_checkable
class StreamMapper(Protocol):
    """
    Protocol unificat pentru conversia evenimentelor native de streaming 
    într-un obiect standardizat LLMStreamChunk.
    """

    def map(self, event: Any, sequence: int) -> LLMStreamChunk:
        """Convertește un eveniment brut primit de la SDK într-un chunk unificat."""
        ...
