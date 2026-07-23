from src.runtime.stream.models import RuntimeExecution
from src.runtime.inspector.models import (
    RequestInfo, ProviderInfo, PromptInfo, ContextInfo,
    MemoryLookupInfo, RetrievedChunkInfo, RAGRetrievalInfo, MetricsInfo, TimelineEventInfo
)
from src.runtime.inspector.snapshot import InspectorSnapshot

class InspectorBuilder:
    @staticmethod
    def build_from_execution(execution: RuntimeExecution, prompt_text: str = "") -> InspectorSnapshot:
        ctx = execution.context
        mem = execution.memory
        rag = execution.rag
        
        sys_prompt = ctx.system_prompt if ctx else ""
        res_prompt = ctx.resolved_prompt if ctx else (prompt_text or execution.prompt)

        req_info = RequestInfo(
            trace_id=execution.trace_id,
            prompt=prompt_text or execution.prompt,
            temperature=execution.temperature,
            timestamp=execution.metrics.started_at,
            system_prompt=sys_prompt,
            resolved_prompt=res_prompt
        )

        prov_info = ProviderInfo(
            provider=execution.provider,
            model=execution.model
        )

        prompt_info = PromptInfo(
            raw_prompt=prompt_text or execution.prompt,
            rendered_prompt=res_prompt,
            system_prompt=sys_prompt
        )

        memory_info = MemoryLookupInfo(
            enabled=mem.enabled if mem else False,
            memories_loaded=mem.memories_loaded if mem else [],
            memory_ids=mem.memory_ids if mem else [],
            selection_strategy=mem.selection_strategy if mem else "",
            selection_reason=mem.selection_reason if mem else "",
            retrieval_time_ms=mem.retrieval_time_ms if mem else 0.0
        )

        chunks_info = [
            RetrievedChunkInfo(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                source=c.source,
                score=c.score,
                content_preview=c.content_preview
            )
            for c in (rag.retrieved_chunks if rag else [])
        ]

        rag_info = RAGRetrievalInfo(
            enabled=rag.enabled if rag else False,
            query=rag.query if rag else "",
            retrieval_strategy=rag.retrieval_strategy if rag else "",
            total_chunks=rag.total_chunks if rag else 0,
            retrieved_chunks=chunks_info,
            selected_chunk_ids=rag.selected_chunk_ids if rag else [],
            retrieval_time_ms=rag.retrieval_time_ms if rag else 0.0
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
            memory=memory_info,
            rag=rag_info,
            tools=[],
            events=events,
            metrics=metrics_info,
            response_text=execution.response_text,
            status=execution.status.value,
            error_message=execution.error_message
        )
