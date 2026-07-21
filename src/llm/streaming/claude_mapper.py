from __future__ import annotations

from typing import Any
from src.llm.streaming.models import LLMStreamChunk
from src.llm.streaming.protocol import StreamMapper


class ClaudeStreamMapper(StreamMapper):
    """
    Mapper concret pentru transformarea evenimentelor de streaming native Anthropic (Claude)
    în obiecte standardizate LLMStreamChunk.
    """

    def map(self, event: Any, sequence: int) -> LLMStreamChunk:
        event_type = getattr(event, "type", None)
        
        delta_text = ""
        finished = False
        finish_reason = None
        model_name = getattr(event, "model", "claude-model")

        # 1. Gestionăm blocurile de conținut (unde vine textul efectiv)
        if event_type == "content_block_delta":
            delta_obj = getattr(event, "delta", None)
            if delta_obj and getattr(delta_obj, "type", None) == "text_delta":
                delta_text = getattr(delta_obj, "text", "")

        # 2. Gestionăm finalizarea mesajului sau a pasului
        elif event_type == "message_delta":
            usage = getattr(event, "usage", None)
            # Putem extrage stop_reason dacă există în delta mesajului
            delta_obj = getattr(event, "delta", None)
            if delta_obj:
                finish_reason = getattr(delta_obj, "stop_reason", None)
            if finish_reason:
                finished = True

        elif event_type == "message_stop":
            finished = True
            finish_reason = "end_turn"

        return LLMStreamChunk(
            delta=delta_text,
            provider="anthropic",
            model=model_name,
            sequence=sequence,
            finished=finished,
            finish_reason=finish_reason,
            raw=event
        )
