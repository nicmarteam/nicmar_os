from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from src.runtime.session.models import RuntimeSession

@dataclass
class ConversationEvent:
    execution_id: str
    trace_id: str
    started_at: float
    duration_ms: float
    provider: str
    model: str
    status: str
    input_tokens: int
    output_tokens: int
    cost: float
    title: str

@dataclass
class ConversationTimeline:
    session_id: str
    started_at: float
    ended_at: Optional[float]
    duration_ms: float
    status: str
    events: List[ConversationEvent] = field(default_factory=list)

    @classmethod
    def from_session(cls, session: RuntimeSession) -> "ConversationTimeline":
        conv_events = []
        total_duration = 0.0

        for idx, execution in enumerate(session.executions, start=1):
            metrics = getattr(execution, 'metrics', None)
            duration = getattr(metrics, 'elapsed_ms', 0.0) if metrics else 0.0
            total_duration += duration

            in_tokens = getattr(metrics, 'input_tokens', 0) if metrics else 0
            out_tokens = getattr(metrics, 'output_tokens', 0) if metrics else 0
            cost = getattr(metrics, 'estimated_cost', 0.0) if metrics else 0.0

            prompt = getattr(execution, 'prompt', 'Execuție fără prompt')
            title = (prompt[:30] + '...') if len(prompt) > 30 else prompt

            event = ConversationEvent(
                execution_id=f"Execution #{idx}",
                trace_id=getattr(execution, 'trace_id', 'unknown'),
                started_at=session.created_at,
                duration_ms=duration,
                provider=getattr(execution, 'provider', 'unknown'),
                model=getattr(execution, 'model', 'unknown'),
                status=getattr(execution, 'status', 'success'),
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                cost=cost,
                title=title
            )
            conv_events.append(event)

        ended_at = session.metadata.get("closed_at", None) if session.status == "closed" else None

        return cls(
            session_id=session.session_id,
            started_at=session.created_at,
            ended_at=ended_at,
            duration_ms=total_duration,
            status=session.status,
            events=conv_events
        )

class ConversationTimelineRenderer:
    @staticmethod
    def render_console(timeline: ConversationTimeline) -> str:
        def fmt_time(ts: float) -> str:
            return datetime.fromtimestamp(ts).strftime("%H:%M:%S")

        lines = [
            "═══════════════════════════════════════",
            "Conversation Timeline",
            "",
            "🟢 Session Started",
            f"   ID: {timeline.session_id} | At: {fmt_time(timeline.started_at)}",
            "────────────────────────────"
        ]

        for ev in timeline.events:
            lines.extend([
                f"① {ev.execution_id}",
                f"   Prompt:  {ev.title}",
                f"   Model:   {ev.model}",
                f"   Duration: {ev.duration_ms} ms",
                "↓"
            ])

        if timeline.events and lines[-1] == "↓":
            lines.pop()

        lines.extend([
            "────────────────────────────",
            f"🔴 Session Closed ({timeline.status.upper()})" if timeline.status == "closed" else f"⚪ Session Active ({timeline.status.upper()})",
            "══════════════════════════════"
        ])

        return "\n".join(lines)
