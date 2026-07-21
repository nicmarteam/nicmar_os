from __future__ import annotations

from typing import Iterator, Any
import openai

from src.llm.streaming.openai_mapper import OpenAIStreamMapper
from src.llm.streaming.models import LLMStreamChunk


class OpenAIClient:
    """Client pentru interacțiunea cu modelele OpenAI (generate și stream)."""

    def __init__(self, api_key: str | None = None, default_model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.default_model = default_model

    def stream(
        self,
        prompt: str,
        *,
        model: str | None = None,
        max_tokens: int = 1024,
    ) -> Iterator[LLMStreamChunk]:
        """Pornește un flux de streaming OpenAI și mapează evenimentele folosind OpenAIStreamMapper."""
        target_model = model or self.default_model

        # 1. Pornim stream-ul folosind SDK-ul OpenAI
        stream_response = self.client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            stream=True,
        )

        sequence = 0
        # 2. Iterăm evenimentele brute primite de la SDK
        for raw_event in stream_response:
            sequence += 1
            
            # 3. Delegăm transformarea către OpenAIStreamMapper
            chunk = OpenAIStreamMapper.map(
                raw_event,
                sequence=sequence,
                model=target_model,
            )
            
            # 4. Facem yield pentru chunk-ul normalizat
            yield chunk
