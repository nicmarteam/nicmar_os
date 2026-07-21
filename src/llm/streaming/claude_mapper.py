from __future__ import annotations

from typing import Any
from src.llm.streaming.models import LLMStreamChunk


class ClaudeStreamMapper:
    """Mapează evenimentele de streaming brute de la Anthropic/Claude în structura internă LLMStreamChunk."""

    @staticmethod
    def map(
        raw_event: Any,
        *,
        sequence: int,
        model: str | None = None,
    ) -> LLMStreamChunk:
        delta_text = ""
        finished = False
        finish_reason = None

        # Extragem modelul din eveniment dacă nu a fost pasat explicit ca argument
        event_model = model or getattr(raw_event, "model", "claude-3-5-sonnet-latest")

        event_type = getattr(raw_event, "type", "")

        # Verificăm dacă este eveniment de final de mesaj
        if event_type == "message_stop":
            finished = True
            finish_reason = "end_turn"
        else:
            # Verificăm delta-ul de conținut
            delta = getattr(raw_event, "delta", None)
            if delta is not None:
                text = getattr(delta, "text", "")
                if text:
                    delta_text = text

        return LLMStreamChunk(
            delta=delta_text,
            finished=finished,
            finish_reason=finish_reason,
            sequence=sequence,
            provider="anthropic",
            model=event_model,
            raw=raw_event,
        )
