import datetime
from src.runtime.timeline.models import ExecutionTimeline, TimelineEvent, TimelineEventType
from src.runtime.timeline.performance import PerformanceMetrics

class TimelineRenderer:
    @staticmethod
    def render_html(timeline: ExecutionTimeline) -> str:
        """Randează Execution Explorer cu Execution Summary și Performance Timeline."""
        
        status_colors = {
            "completed": {"dot": "🟢", "border": "#10b981", "badge": "#ecfdf5", "text": "#065f46"},
            "error": {"dot": "🔴", "border": "#ef4444", "badge": "#fef2f2", "text": "#991b1b"},
            "running": {"dot": "🟡", "border": "#f59e0b", "badge": "#fffbeb", "text": "#92400e"}
        }

        p = timeline.performance
        ttft_badge = PerformanceMetrics.classify_metric("ttft_ms", p.ttft_ms)
        tps_badge = PerformanceMetrics.classify_metric("tokens_per_second", p.tokens_per_second)
        total_badge = PerformanceMetrics.classify_metric("total_ms", timeline.total_duration_ms)

        html = []
        html.append("<div style=\'font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; max-width: 800px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);\'>")
        
        # Header
        html.append("<div style=\'display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f3f4f6; padding-bottom: 12px; margin-bottom: 16px;\'>")
        html.append("<h3 style=\'margin: 0; color: #111827; font-size: 16px; font-weight: 700;\'>🧭 Execution Explorer & Performance Timeline</h3>")
        html.append(f"<span style=\'font-family: monospace; font-size: 12px; color: #6b7280; background: #f3f4f6; padding: 4px 8px; border-radius: 6px;\'>Trace: {timeline.trace_id[:8]}...</span>")
        html.append("</div>")

        # Execution Summary Panel (DevTools Style)
        html.append("<div style=\'background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 20px;\'>")
        html.append("<div style=\'font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;\'>📊 Execution Summary</div>")
        
        html.append("<div style=\'display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; font-size: 12px;\'>")
        
        # Metric 1: TTFT
        html.append(f"<div style=\'background: #ffffff; padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1;\'>")
        html.append("<div style=\'color: #64748b;\'>TTFT</div>")
        html.append(f"<div style=\'font-weight: 600; color: #0f172a; font-size: 14px;\'>{round(p.ttft_ms, 1)} ms</div>")
        html.append(f"<div style=\'font-size: 10px; margin-top: 2px; color: #059669;\'>{ttft_badge}</div>")
        html.append("</div>")

        # Metric 2: Total Duration
        html.append(f"<div style=\'background: #ffffff; padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1;\'>")
        html.append("<div style=\'color: #64748b;\'>Total Duration</div>")
        html.append(f"<div style=\'font-weight: 600; color: #0f172a; font-size: 14px;\'>{round(timeline.total_duration_ms, 1)} ms</div>")
        html.append(f"<div style=\'font-size: 10px; margin-top: 2px; color: #059669;\'>{total_badge}</div>")
        html.append("</div>")

        # Metric 3: TPS
        html.append(f"<div style=\'background: #ffffff; padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1;\'>")
        html.append("<div style=\'color: #64748b;\'>Speed (TPS)</div>")
        html.append(f"<div style=\'font-weight: 600; color: #0f172a; font-size: 14px;\'>{round(p.tokens_per_second, 1)} tok/s</div>")
        html.append(f"<div style=\'font-size: 10px; margin-top: 2px; color: #059669;\'>{tps_badge}</div>")
        html.append("</div>")

        # Metric 4: Tokens / Cost
        html.append(f"<div style=\'background: #ffffff; padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1;\'>")
        html.append("<div style=\'color: #64748b;\'>Tokens (In / Out)</div>")
        html.append(f"<div style=\'font-weight: 600; color: #0f172a; font-size: 13px;\'>{p.tokens_input} / {p.tokens_output}</div>")
        html.append(f"<div style=\'font-size: 10px; margin-top: 2px; color: #64748b;\'>Cost: ${p.estimated_cost:.4f}</div>")
        html.append("</div>")

        html.append("</div>") # close grid
        html.append("</div>") # close summary panel

        # Timeline list container
        html.append("<div style=\'position: relative; border-left: 2px solid #e5e7eb; margin-left: 12px; padding-left: 20px;\'>")

        for ev in timeline.events:
            dt_str = datetime.datetime.fromtimestamp(ev.timestamp).strftime('%H:%M:%S.%f')[:-3] if ev.timestamp > 0 else "00:00:00.000"
            st_style = status_colors.get(ev.status, status_colors["completed"])

            html.append("<div style=\'position: relative; margin-bottom: 20px;\'>")
            html.append(f"<span style=\'position: absolute; left: -27px; top: 0px; font-size: 14px; background: #ffffff; padding: 2px 0;\'>{st_style['dot']}</span>")
            
            html.append("<div style=\'background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px;\'>")
            html.append("<div style=\'display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;\'>")
            html.append(f"<span style=\'font-weight: 600; font-size: 14px; color: #1f2937;\'>{ev.title}</span>")
            html.append(f"<span style=\'font-family: monospace; font-size: 11px; color: #9ca3af;\'>{dt_str}</span>")
            html.append("</div>")

            if ev.description:
                html.append(f"<p style=\'margin: 4px 0 8px 0; font-size: 13px; color: #4b5563;\'>{ev.description}</p>")

            meta_parts = []
            if ev.duration_ms > 0:
                meta_parts.append(f"Duration: {round(ev.duration_ms, 2)}ms")
            for k, v in ev.metadata.items():
                meta_parts.append(f"{k}: {v}")

            if meta_parts:
                html.append(f"<div style=\'font-family: monospace; font-size: 11px; background: {st_style['badge']}; color: {st_style['text']}; padding: 4px 8px; border-radius: 4px; display: inline-block; margin-top: 4px;\'>")
                html.append(" | ".join(meta_parts))
                html.append("</div>")

            html.append("</div>")
            html.append("</div>")

        html.append("</div>")
        html.append("</div>")

        return "".join(html)
