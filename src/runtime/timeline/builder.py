from src.runtime.stream.models import RuntimeExecution
from src.runtime.timeline.models import TimelineEvent, ExecutionTimeline
from src.runtime.timeline.performance import PerformanceMetrics

class TimelineBuilder:
    @staticmethod
    def build_from_execution(execution: RuntimeExecution) -> ExecutionTimeline:
        m = execution.metrics
        started_at = getattr(m, "started_at", 0.0)
        finished_at = getattr(m, "finished_at", 0.0)
        total_duration = getattr(m, "elapsed_ms", 0.0)

        # Extragem sau construim metricile de performanță gata calculate
        perf = PerformanceMetrics(
            ttft_ms=getattr(m, "ttft_ms", 0.0),
            provider_latency_ms=getattr(m, "elapsed_ms", 0.0),
            stream_duration_ms=getattr(m, "elapsed_ms", 0.0),
            execution_duration_ms=total_duration,
            tokens_input=getattr(m, "input_tokens", 0),
            tokens_output=getattr(m, "output_tokens", 0),
            tokens_per_second=getattr(m, "tokens_per_second", 0.0),
            estimated_cost=getattr(m, "estimated_cost", 0.0)
        )

        events = []
        for raw_event in execution.events:
            events.append(TimelineEvent(
                id=raw_event.get("id", "evt_000"),
                timestamp=raw_event.get("timestamp", 0.0),
                event_type=raw_event.get("event_type", "UNKNOWN"),
                title=raw_event.get("title", "Event"),
                description=raw_event.get("description", ""),
                duration_ms=raw_event.get("duration_ms", 0.0),
                status=raw_event.get("status", "completed"),
                metadata=raw_event.get("metadata", {})
            ))

        return ExecutionTimeline(
            trace_id=execution.trace_id,
            started_at=started_at,
            finished_at=finished_at,
            total_duration_ms=total_duration,
            performance=perf,
            events=events
        )
