from typing import AsyncGenerator, Dict, Type, Tuple, Optional
import time
import uuid

from src.runtime.stream.models import (
    LLMStreamChunk, StreamChunkType, StreamMetrics, 
    RuntimeExecution, RuntimeStatus, TokenUsage, ExecutionContext, MemoryTrace
)
from src.runtime.stream.adapters import BaseStreamAdapter

class UnifiedStreamService:
    def __init__(self):
        self._adapters: Dict[str, Type[BaseStreamAdapter]] = {}

    def register_adapter(self, provider_name: str, adapter_cls: Type[BaseStreamAdapter]):
        self._adapters[provider_name] = adapter_cls

    async def execute_stream(
        self, 
        provider: str, 
        model: str, 
        prompt: str, 
        temperature: float = 0.7, 
        system_prompt: str = "",
        max_tokens: Optional[int] = None,
        memory_trace: Optional[MemoryTrace] = None,
        **kwargs
    ) -> AsyncGenerator[Tuple[RuntimeStatus, Optional[LLMStreamChunk], RuntimeExecution], None]:
        if provider not in self._adapters:
            raise ValueError(f"Provider necunoscut pentru streaming: {provider}")
        
        adapter_instance = self._adapters[provider]()
        trace_id = str(uuid.uuid4())
        metrics = StreamMetrics(started_at=time.time())
        
        exec_context = ExecutionContext(
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            user_prompt=prompt,
            resolved_prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            trace_id=trace_id
        )

        active_memory = memory_trace if memory_trace is not None else MemoryTrace()

        execution = RuntimeExecution(
            trace_id=trace_id,
            provider=provider,
            model=model,
            prompt=prompt,
            temperature=temperature,
            context=exec_context,
            memory=active_memory,
            status=RuntimeStatus.CONNECTING,
            metrics=metrics
        )
        
        execution.events.append({"timestamp": time.time(), "event_type": "REQUEST_CREATED", "details": {"trace_id": trace_id}})
        yield execution.status, None, execution

        execution.status = RuntimeStatus.WAITING_FIRST_TOKEN
        execution.events.append({"timestamp": time.time(), "event_type": "PROVIDER_CALLED", "details": {"provider": provider, "model": model}})
        yield execution.status, None, execution

        full_text = ""
        try:
            async for chunk in adapter_instance.stream(prompt=prompt, model=model, temperature=temperature, **kwargs):
                execution.chunks.append(chunk)
                
                if chunk.chunk_type == StreamChunkType.DELTA and chunk.text:
                    if metrics.first_token_at == 0.0:
                        metrics.first_token_at = time.time()
                        metrics.ttft_ms = (metrics.first_token_at - metrics.started_at) * 1000.0
                        execution.status = RuntimeStatus.STREAMING
                        execution.events.append({"timestamp": metrics.first_token_at, "event_type": "FIRST_TOKEN_RECEIVED", "details": {"ttft_ms": round(metrics.ttft_ms, 2)}})

                    full_text += chunk.text
                    execution.response_text = full_text

                if chunk.usage:
                    metrics.input_tokens = chunk.usage.input_tokens
                    metrics.output_tokens = chunk.usage.output_tokens

                yield execution.status, chunk, execution

            metrics.finished_at = time.time()
            metrics.elapsed_ms = (metrics.finished_at - metrics.started_at) * 1000.0
            
            duration_sec = metrics.elapsed_ms / 1000.0
            if duration_sec > 0 and metrics.output_tokens > 0:
                metrics.tokens_per_second = round(metrics.output_tokens / duration_sec, 2)
            
            metrics.estimated_cost = round((metrics.input_tokens * 0.00000015) + (metrics.output_tokens * 0.0000006), 6)
            
            execution.status = RuntimeStatus.FINISHED
            execution.events.append({"timestamp": metrics.finished_at, "event_type": "EXECUTION_FINISHED", "details": {"status": execution.status.value, "total_ms": round(metrics.elapsed_ms, 2)}})
            yield execution.status, None, execution

        except Exception as e:
            execution.status = RuntimeStatus.ERROR
            execution.error_message = str(e)
            metrics.finished_at = time.time()
            metrics.elapsed_ms = (metrics.finished_at - metrics.started_at) * 1000.0
            execution.events.append({"timestamp": metrics.finished_at, "event_type": "EXECUTION_ERROR", "details": {"error": str(e)}})
            yield execution.status, None, execution
