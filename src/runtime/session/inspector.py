from dataclasses import dataclass
from datetime import datetime
from src.runtime.session.models import RuntimeSession
from src.runtime.session.summary import SessionSummary

@dataclass
class SessionInspectorSnapshot:
    summary: SessionSummary
    executions: list

class SessionInspector:
    @staticmethod
    def inspect(session: RuntimeSession) -> SessionInspectorSnapshot:
        summary = SessionSummary.from_session(session)
        return SessionInspectorSnapshot(summary=summary, executions=session.executions)

    @staticmethod
    def render_console(session: RuntimeSession) -> str:
        summary = SessionSummary.from_session(session)
        
        def fmt_time(ts: float) -> str:
            return datetime.fromtimestamp(ts).strftime("%H:%M:%S")

        lines = [
            "══════════════════════════════════════",
            "🧠 Runtime Session",
            "",
            "Session:",
            f"{summary.session_id}",
            "",
            "Status:",
            f"{summary.status.upper()}",
            "",
            "Started:",
            f"{fmt_time(summary.started_at)}",
            "",
            "Last Activity:",
            f"{fmt_time(summary.last_activity_at)}",
            "",
            "Executions:",
            f"{summary.execution_count}",
            "──────────────────────────────",
            "Providers"
        ]
        
        for p in summary.providers_used:
            lines.append(f"{p:<15} {summary.execution_count}")
            
        lines.extend([
            "──────────────────────────────",
            "Models"
        ])
        
        for m in summary.models_used:
            lines.append(f"{m:<20} {summary.execution_count}")
            
        lines.extend([
            "──────────────────────────────",
            "Tokens",
            f"Input:  {summary.total_input_tokens:,}",
            f"Output: {summary.total_output_tokens:,}",
            "──────────────────────────────",
            "Estimated Cost",
            f"${summary.estimated_total_cost:.4f}",
            "──────────────────────────────",
            "Errors",
            f"{summary.error_count}",
            "══════════════════════════════════════"
        ])
        
        return "\n".join(lines)
