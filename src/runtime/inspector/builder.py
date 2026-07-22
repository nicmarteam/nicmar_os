from src.runtime.stream.models import RuntimeExecution
from src.runtime.inspector.models import (
    RequestInfo, ProviderInfo, PromptInfo, ContextInfo,
    MemoryLookupInfo, RAGRetrievalInfo, MetricsInfo, TimelineEventInfo
)
from src.runtime.inspector.snapshot import InspectorSnapshot

class InspectorBuilder:
    @staticmethod
    def build_from_execution(execution: RuntimeExecution, prompt_text: str, temperature: float = 0.7) -> InspectorSnapshot:
        req_info = RequestInfo(
            trace_id=execution.trace_id,
            prompt=prompt_text,
            temperature=temperature,
            timestamp=execution.metrics.started_at
        )

        prov_info = ProviderInfo(
            provider=execution.provider,
            model=execution.model
        )

        prompt_info = PromptInfo(
            raw_prompt=prompt_text,
            rendered_prompt=prompt_text
        )

        m = execution.metrics
        metrics_info = MetricsInfo(
            ttft_ms=m.ttft_ms,
            elapsed_ms=m.elapsed_ms,
            tokens_per_second=m.tokens_per_second,
            input_tokens=m.input_tokens,
            output_tokens=m.output_tokens,
            estimated_cost=m.estimated_cost
        )

        # Timeline events complet generate din stările runtime-ului
        events = [
            TimelineEventInfo(timestamp=m.started_at, event_type="REQUEST_STARTED", details={"trace_id": execution.trace_id}),
        ]
        if m.first_token_at > 0:
            events.append(TimelineEventInfo(timestamp=m.first_token_at, event_type="FIRST_TOKEN_RECEIVED", details={"ttft_ms": round(m.ttft_ms, 2)}))
        if m.finished_at > 0:
            events.append(TimelineEventInfo(timestamp=m.finished_at, event_type="EXECUTION_FINISHED", details={"status": execution.status.value, "total_ms": round(m.elapsed_ms, 2)}))

        return InspectorSnapshot(
            request=req_info,
            provider_info=prov_info,
            prompt=prompt_info,
            context=ContextInfo(),
            memory=MemoryLookupInfo(),
            rag=RAGRetrievalInfo(),
            tools=[],
            events=events,
            metrics=metrics_info,
            response_text=execution.response_text,
            status=execution.status.value,
            error_message=execution.error_message
        )
