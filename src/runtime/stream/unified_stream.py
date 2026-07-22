from typing import AsyncGenerator, Dict, Type
import time
import uuid

from src.runtime.stream.models import LLMStreamChunk, StreamChunkType, StreamMetrics, StreamSession, TokenUsage
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
            
            # Detectăm primul token pentru TTFT (Time To First Token)
            if chunk.chunk_type == StreamChunkType.DELTA and chunk.text and metrics.first_token_at == 0.0:
                metrics.first_token_at = time.time()
                metrics.ttft_ms = (metrics.first_token_at - metrics.started_at) * 1000.0

            # Colectăm token usage dacă este prezent în chunk
            if chunk.usage:
                metrics.input_tokens = chunk.usage.input_tokens
                metrics.output_tokens = chunk.usage.output_tokens

            yield chunk

        # Finalizăm măsurătorile la încheierea stream-ului
        metrics.finished_at = time.time()
        metrics.elapsed_ms = (metrics.finished_at - metrics.started_at) * 1000.0
        
        # Calculăm Tokens per Second (TPS)
        duration_sec = metrics.elapsed_ms / 1000.0
        if duration_sec > 0 and metrics.output_tokens > 0:
            metrics.tokens_per_second = round(metrics.output_tokens / duration_sec, 2)
            
        # Estimare simplă de cost (orientativă pentru flash)
        metrics.estimated_cost = round((metrics.input_tokens * 0.00000015) + (metrics.output_tokens * 0.0000006), 6)
