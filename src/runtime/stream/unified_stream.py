from typing import AsyncGenerator, Dict, Type, Tuple, Optional
import time
import uuid

from src.runtime.stream.models import (
    LLMStreamChunk, StreamChunkType, StreamMetrics, 
    RuntimeExecution, RuntimeStatus, TokenUsage
)
from src.runtime.stream.adapters import BaseStreamAdapter

class UnifiedStreamService:
    def __init__(self):
        self._adapters: Dict[str, Type[BaseStreamAdapter]] = {}

    def register_adapter(self, provider_name: str, adapter_cls: Type[BaseStreamAdapter]):
        self._adapters[provider_name] = adapter_cls

    async def execute_stream(self, provider: str, model: str, prompt: str, **kwargs) -> AsyncGenerator[Tuple[RuntimeStatus, Optional[LLMStreamChunk], RuntimeExecution], None]:
        if provider not in self._adapters:
            raise ValueError(f"Provider necunoscut pentru streaming: {provider}")
        
        adapter_instance = self._adapters[provider]()
        trace_id = str(uuid.uuid4())
        metrics = StreamMetrics(started_at=time.time())
        execution = RuntimeExecution(
            trace_id=trace_id,
            provider=provider,
            model=model,
            status=RuntimeStatus.CONNECTING,
            metrics=metrics
        )

        yield execution.status, None, execution

        execution.status = RuntimeStatus.WAITING_FIRST_TOKEN
        yield execution.status, None, execution

        full_text = ""
        try:
            async for chunk in adapter_instance.stream(prompt=prompt, model=model, **kwargs):
                execution.chunks.append(chunk)
                
                if chunk.chunk_type == StreamChunkType.DELTA and chunk.text:
                    if metrics.first_token_at == 0.0:
                        metrics.first_token_at = time.time()
                        metrics.ttft_ms = (metrics.first_token_at - metrics.started_at) * 1000.0
                        execution.status = RuntimeStatus.STREAMING

                    full_text += chunk.text
                    execution.response_text = full_text

                if chunk.usage:
                    metrics.input_tokens = chunk.usage.input_tokens
                    metrics.output_tokens = chunk.usage.output_tokens

                yield execution.status, chunk, execution

            # Finalizare calcul metrici în Runtime
            metrics.finished_at = time.time()
            metrics.elapsed_ms = (metrics.finished_at - metrics.started_at) * 1000.0
            
            duration_sec = metrics.elapsed_ms / 1000.0
            if duration_sec > 0 and metrics.output_tokens > 0:
                metrics.tokens_per_second = round(metrics.output_tokens / duration_sec, 2)
            
            # Estimare cost centralizată în Runtime
            metrics.estimated_cost = round((metrics.input_tokens * 0.00000015) + (metrics.output_tokens * 0.0000006), 6)
            
            execution.status = RuntimeStatus.FINISHED
            yield execution.status, None, execution

        except Exception as e:
            execution.status = RuntimeStatus.ERROR
            execution.error_message = str(e)
            metrics.finished_at = time.time()
            metrics.elapsed_ms = (metrics.finished_at - metrics.started_at) * 1000.0
            yield execution.status, None, execution
