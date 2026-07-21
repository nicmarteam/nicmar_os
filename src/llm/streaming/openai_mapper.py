from __future__ import annotations

from typing import Any
from src.llm.streaming.models import LLMStreamChunk


class OpenAIStreamMapper:
    """Mapează evenimentele de streaming brute de la OpenAI în structura internă LLMStreamChunk."""

    @staticmethod
    def map(
        raw_event: Any,
        *,
        model: str,
        sequence: int,
    ) -> LLMStreamChunk:
        delta_text = ""
        finished = False
        finish_reason = None

        # Extragem în siguranță opțiunile din evenimentul OpenAI (suportă dict sau obiecte cu atribute)
        choices = getattr(raw_event, "choices", None)
        if choices is None and isinstance(raw_event, dict):
            choices = raw_event.get("choices")

        if choices and len(choices) > 0:
            choice = choices[0]
            
            # Verificăm finish_reason
            reason = getattr(choice, "finish_reason", None)
            if reason is None and isinstance(choice, dict):
                reason = choice.get("finish_reason")
            
            if reason is not None:
                finish_reason = reason
                finished = True

            # Extragem delta și conținutul text
            delta = getattr(choice, "delta", None)
            if delta is None and isinstance(choice, dict):
                delta = choice.get("delta")

            if delta is not None:
                content = getattr(delta, "content", None)
                if content is None and isinstance(delta, dict):
                    content = delta.get("content")

                if content:
                    delta_text = content

        return LLMStreamChunk(
            delta=delta_text,
            finished=finished,
            finish_reason=finish_reason,
            sequence=sequence,
            provider="openai",
            model=model,
            raw=raw_event,
        )
