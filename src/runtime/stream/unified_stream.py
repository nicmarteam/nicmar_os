from typing import AsyncGenerator, Dict, Type
import time
import uuid

from src.runtime.stream.models import LLMStreamChunk, StreamChunkType, StreamMetrics, StreamSession
from src.runtime.stream.adapters import BaseStreamAdapter

class UnifiedStreamService:
    def __init__(self):
        self._adapters: Dict[str, Type[BaseStreamAdapter]] = {}

    def register_adapter(self, provider_name: str, adapter_cls: Type[BaseStreamAdapter]):
        self._adapters[provider_name] = adapter_cls

    async def stream(self, provider: str, model: str, prompt: str, **kwargs) -> AsyncGenerator[LLMStreamChunk, None]:
        if provider not in self._adapters:
            raise ValueError(f"Provider necunoscut pentru streaming: {provider}")
        
        adapter_instance = self._adapters[provider]()
        request_id = str(uuid.uuid4())
        metrics = StreamMetrics(started_at=time.time())
        session = StreamSession(request_id=request_id, provider=provider, model=model, metrics=metrics)

        async for chunk in adapter_instance.stream(prompt=prompt, model=model, **kwargs):
            session.chunks.append(chunk)
            if chunk.chunk_type == StreamChunkType.DELTA and metrics.first_token_at == 0.0:
                metrics.first_token_at = time.time()
                metrics.ttft_ms = (metrics.first_token_at - metrics.started_at) * 1000.0

            yield chunk

        metrics.finished_at = time.time()
        metrics.elapsed_ms = (metrics.finished_at - metrics.started_at) * 1000.0
