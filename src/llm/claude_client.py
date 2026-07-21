from __future__ import annotations

from typing import Iterator, Any
import anthropic

from src.llm.streaming.claude_mapper import ClaudeStreamMapper
from src.llm.streaming.models import LLMStreamChunk


class ClaudeClient:
    """Client pentru interacțiunea cu modelele Claude de la Anthropic (generate și stream)."""

    def __init__(self, api_key: str | None = None, default_model: str = "claude-3-5-sonnet-latest"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.default_model = default_model

    def stream(
        self,
        prompt: str,
        *,
        model: str | None = None,
        max_tokens: int = 1024,
    ) -> Iterator[LLMStreamChunk]:
        """Pornește un flux de streaming și mapează evenimentele folosind ClaudeStreamMapper."""
        target_model = model or self.default_model

        with self.client.messages.stream(
            model=target_model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        ) as stream_response:
            
            sequence = 0
            for raw_event in stream_response:
                sequence += 1
                
                chunk = ClaudeStreamMapper.map(
                    raw_event,
                    sequence=sequence,
                    model=target_model,
                )
                
                yield chunk
