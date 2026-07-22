import datetime
from src.runtime.timeline.models import ExecutionTimeline, TimelineEvent, TimelineEventType

class TimelineRenderer:
    @staticmethod
    def render_html(timeline: ExecutionTimeline) -> str:
        """Randează Execution Explorer sub formă de HTML curat, stil DevTools."""
        
        status_colors = {
            "completed": {"dot": "🟢", "border": "#10b981", "badge": "#ecfdf5", "text": "#065f46"},
            "error": {"dot": "🔴", "border": "#ef4444", "badge": "#fef2f2", "text": "#991b1b"},
            "running": {"dot": "🟡", "border": "#f59e0b", "badge": "#fffbeb", "text": "#92400e"}
        }

        html = []
        html.append("<div style=\'font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; max-width: 750px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);\'>")
        
        # Header
        html.append("<div style=\'display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f3f4f6; padding-bottom: 12px; margin-bottom: 16px;\'>")
        html.append("<h3 style=\'margin: 0; color: #111827; font-size: 16px; font-weight: 700;\'>🧭 Execution Explorer (Timeline)</h3>")
        html.append(f"<span style=\'font-family: monospace; font-size: 12px; color: #6b7280; background: #f3f4f6; padding: 4px 8px; border-radius: 6px;\'>Trace: {timeline.trace_id[:8]}...</span>")
        html.append("</div>")

        # Metrics bar
        total_dur_sec = round(timeline.total_duration_ms, 2)
        html.append("<div style=\'display: flex; gap: 16px; margin-bottom: 20px; font-size: 13px; color: #374151;\'>")
        html.append(f"<div><b>Total Duration:</b> {total_dur_sec} ms</div>")
        html.append(f"<div><b>Total Events:</b> {len(timeline.events)}</div>")
        html.append("</div>")

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
