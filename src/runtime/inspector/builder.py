from src.runtime.stream.models import RuntimeExecution
from src.runtime.inspector.models import (
    RequestInfo, ProviderInfo, PromptInfo, ContextInfo,
    MemoryLookupInfo, RAGRetrievalInfo, MetricsInfo, TimelineEventInfo
)
from src.runtime.inspector.snapshot import InspectorSnapshot

class InspectorBuilder:
    @staticmethod
    def build_from_execution(execution: RuntimeExecution) -> InspectorSnapshot:
        req_info = RequestInfo(
            trace_id=execution.trace_id,
            prompt=execution.prompt,
            temperature=execution.temperature,
            timestamp=execution.metrics.started_at
        )

        prov_info = ProviderInfo(
            provider=execution.provider,
            model=execution.model
        )

        prompt_info = PromptInfo(
            raw_prompt=execution.prompt,
            rendered_prompt=execution.prompt
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

        events = [
            TimelineEventInfo(timestamp=ev["timestamp"], event_type=ev["event_type"], details=ev["details"])
            for ev in execution.events
        ]

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
