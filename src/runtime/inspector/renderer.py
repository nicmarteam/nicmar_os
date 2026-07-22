from src.runtime.stream.models import RuntimeExecution
from src.runtime.timeline.selection import TimelineSelection
from src.runtime.timeline.details import EventDetailsBuilder

class InspectorRenderer:
    @staticmethod
    def render_inspection_html(execution: RuntimeExecution, selection: TimelineSelection = None) -> str:
        """Randează Inspectorul în mod dinamic: Global Execution Mode sau Event Focus Mode."""
        
        html = []
        html.append("<div style=\'font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; max-width: 800px; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);\'>")
        
        # Verificăm dacă avem o selecție activă de la Timeline (Event Mode vs Execution Mode)
        if selection and selection.is_event_selected():
            target_event = None
            for ev in execution.events:
                if ev.get("id") == selection.selected_event_id:
                    target_event = ev
                    break
            
            if target_event:
                details = EventDetailsBuilder.build_for_event(
                    event_id=target_event.get("id", "unknown"),
                    event_type=target_event.get("event_type", "UNKNOWN"),
                    title=target_event.get("title", "Event Focus"),
                    metadata=target_event.get("metadata", {})
                )
                
                html.append("<div style=\'display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 16px;\'>")
                html.append("<h3 style=\'margin: 0; color: #0f172a; font-size: 16px; font-weight: 700;\'>🔍 Inspector [Event Focus Mode]</h3>")
                html.append(f"<span style=\'font-family: monospace; font-size: 11px; background: #e0f2fe; color: #0369a1; padding: 4px 8px; border-radius: 6px;\'>Event: {details.title}</span>")
                html.append("</div>")

                html.append(f"<div style=\'background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 14px; font-size: 13px;\'>")
                html.append(f"<div><b>Event ID:</b> <span style=\'font-family: monospace;\'>{details.event_id}</span></div>")
                html.append(f"<div><b>Event Type:</b> <span style=\'font-family: monospace;\'>{details.event_type}</span></div>")
                html.append("</div>")

                for section in details.summary_sections:
                    html.append(f"<div style=\'background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-bottom: 10px;\'>")
                    html.append(f"<div style=\'font-size: 12px; font-weight: 700; color: #334155; margin-bottom: 8px; text-transform: uppercase;\'>{section.title}</div>")
                    html.append("<div style=\'display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-size: 12px; font-family: monospace;\'>")
                    for k, v in section.data.items():
                        v_str = ", ".join(v) if isinstance(v, list) else str(v)
                        html.append(f"<div><span style=\'color: #64748b;\'>{k}:</span> <span style=\'color: #0f172a;\'>{v_str}</span></div>")
                    html.append("</div>")
                    html.append("</div>")
            else:
                html.append("<div style=\'color: #dc2626; font-size: 13px;\'>Selected event not found in execution trace.</div>")
        else:
            # Execution Mode (Global Overview)
            m = execution.metrics
            html.append("<div style=\'display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 16px;\'>")
            html.append("<h3 style=\'margin: 0; color: #0f172a; font-size: 16px; font-weight: 700;\'>🔍 Inspector [Execution Overview Mode]</h3>")
            html.append(f"<span style=\'font-family: monospace; font-size: 11px; background: #f1f5f9; color: #475569; padding: 4px 8px; border-radius: 6px;\'>Trace: {execution.trace_id[:8]}...</span>")
            html.append("</div>")

            html.append("<div style=\'display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; font-size: 13px;\'>")
            html.append(f"<div style=\'background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;\'><b>Provider:</b> {execution.provider}</div>")
            html.append(f"<div style=\'background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0;\'><b>Model:</b> {execution.model}</div>")
            html.append(f"<div style=\'background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0; grid-column: span 2;\'><b>Prompt:</b> {execution.prompt}</div>")
            html.append("</div>")

            if m:
                html.append("<div style=\'margin-top: 14px; background: #f8fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0; font-size: 12px; font-family: monospace;\'>")
                html.append("<div style=\'font-weight: 700; color: #334155; margin-bottom: 6px; text-transform: uppercase; font-family: sans-serif;\'>Execution Metrics</div>")
                html.append(f"<div>Elapsed Time: {getattr(m, 'elapsed_ms', 0.0)} ms | TTFT: {getattr(m, 'ttft_ms', 0.0)} ms</div>")
                html.append(f"<div>Tokens In: {getattr(m, 'input_tokens', 0)} | Tokens Out: {getattr(m, 'output_tokens', 0)}</div>")
                html.append("</div>")

        html.append("</div>")
        return "".join(html)
