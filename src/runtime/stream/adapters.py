from abc import ABC, abstractmethod
from typing import AsyncGenerator
from google import genai
from src.runtime.stream.models import LLMStreamChunk, StreamChunkType, TokenUsage

class BaseStreamAdapter(ABC):
    @abstractmethod
    async def stream(self, prompt: str, model: str, **kwargs) -> AsyncGenerator[LLMStreamChunk, None]:
        pass

class GeminiAdapter(BaseStreamAdapter):
    def __init__(self):
        self.client = genai.Client()

    async def stream(self, prompt: str, model: str = "gemini-2.5-flash", **kwargs) -> AsyncGenerator[LLMStreamChunk, None]:
        response = await self.client.aio.models.generate_content_stream(
            model=model,
            contents=prompt,
            **kwargs
        )

        async for chunk in response:
            text_delta = getattr(chunk, "text", "") or ""
            usage_obj = None
            if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
                usage_obj = TokenUsage(
                    input_tokens=getattr(chunk.usage_metadata, "prompt_token_count", 0),
                    output_tokens=getattr(chunk.usage_metadata, "candidates_token_count", 0)
                )

            yield LLMStreamChunk(
                chunk_type=StreamChunkType.DELTA,
                text=text_delta,
                provider="gemini",
                model=model,
                usage=usage_obj
            )

        yield LLMStreamChunk(
            chunk_type=StreamChunkType.FINISH,
            text="",
            provider="gemini",
            model=model
        )
