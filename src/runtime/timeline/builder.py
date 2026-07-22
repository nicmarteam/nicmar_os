from src.runtime.stream.models import RuntimeExecution
from src.runtime.timeline.models import TimelineEvent, ExecutionTimeline

class TimelineBuilder:
    @staticmethod
    def build_from_execution(execution: RuntimeExecution) -> ExecutionTimeline:
        m = execution.metrics
        started_at = getattr(m, "started_at", 0.0)
        finished_at = getattr(m, "finished_at", 0.0)
        total_duration = getattr(m, "elapsed_ms", 0.0)

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
            events=events
        )
