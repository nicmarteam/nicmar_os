from src.runtime.stream.models import RuntimeExecution
from src.runtime.timeline.models import TimelineEvent, ExecutionTimeline

class TimelineBuilder:
    @staticmethod
    def build_from_execution(execution: RuntimeExecution) -> ExecutionTimeline:
        started_at = execution.metrics.started_at
        finished_at = execution.metrics.finished_at
        total_duration = execution.metrics.elapsed_ms

        events: List[TimelineEvent] = []
        
        # Transformăm evenimentele brute din execution.events în TimelineEvent-uri structurate
        for i, raw_event in enumerate(execution.events):
            ev_type = raw_event.get("event_type", "UNKNOWN")
            timestamp = raw_event.get("timestamp", started_at)
            details = raw_event.get("details", {})
            
            # Mapare prietenoasă pentru titluri
            title_map = {
                "REQUEST_CREATED": "Request Created",
                "PROVIDER_CALLED": "Provider Request",
                "FIRST_TOKEN_RECEIVED": "First Token Received",
                "EXECUTION_FINISHED": "Execution Completed",
                "EXECUTION_ERROR": "Execution Error"
            }
            title = title_map.get(ev_type, ev_type.replace("_", " ").title())
            
            duration = details.get("ttft_ms", details.get("total_ms", 0.0))
            status = "error" if ev_type == "EXECUTION_ERROR" else "completed"

            events.append(TimelineEvent(
                id=f"evt_{i+1:03d}",
                timestamp=timestamp,
                event_type=ev_type,
                title=title,
                description=str(details),
                duration_ms=duration,
                status=status,
                metadata=details
            ))

        return ExecutionTimeline(
            trace_id=execution.trace_id,
            started_at=started_at,
            finished_at=finished_at,
            total_duration_ms=total_duration,
            events=events
        )
