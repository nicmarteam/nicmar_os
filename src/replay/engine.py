from typing import List, Dict, Any, Optional
from src.events.bus import global_event_bus, SystemEvent, EventType

class TraceStore:
    def __init__(self):
        # Stocăm evenimentele grupate după request_id sau conversation_id
        self._traces: Dict[str, List[SystemEvent]] = {}
        # Abonare automată la Event Bus pentru a intercepta tot ce mișcă în sistem
        global_event_bus.subscribe(EventType.PLAN_CREATED, self._capture_event)
        global_event_bus.subscribe(EventType.NODE_STARTED, self._capture_event)
        global_event_bus.subscribe(EventType.NODE_FINISHED, self._capture_event)
        global_event_bus.subscribe(EventType.PROVIDER_SELECTED, self._capture_event)
        global_event_bus.subscribe(EventType.LLM_STARTED, self._capture_event)
        global_event_bus.subscribe(EventType.LLM_COMPLETED, self._capture_event)
        global_event_bus.subscribe(EventType.TOOL_EXECUTED, self._capture_event)
        global_event_bus.subscribe(EventType.MEMORY_STORED, self._capture_event)
        global_event_bus.subscribe(EventType.WORKFLOW_FINISHED, self._capture_event)

    def _capture_event(self, event: SystemEvent) -> None:
        req_id = event.payload.get("request_id", "default_request")
        if req_id not in self._traces:
            self._traces[req_id] = []
        self._traces[req_id].append(event)

    def get_trace(self, request_id: str) -> List[SystemEvent]:
        return self._traces.get(request_id, [])

    def list_all_request_ids(self) -> List[str]:
        return list(self._traces.keys())

class ReplayEngine:
    def __init__(self, trace_store: TraceStore):
        self.trace_store = trace_store

    def replay_trace(self, request_id: str) -> str:
        """
        Reconstruiește și afișează cronologia completă a execuției pe baza evenimentelor înregistrate.
        """
        events = self.trace_store.get_trace(request_id)
        if not events:
            return f"No trace found for Request ID: {request_id}"

        report = []
        report.append(f"=== REPLAY TRACE FOR REQUEST: {request_id} ===")
        for i, ev in enumerate(events, 1):
            report.append(f"  {i}. [{ev.timestamp}] Event: {ev.event_type.value.upper()}")
            for k, v in ev.payload.items():
                report.append(f"     - {k}: {v}")
        report.append("===============================================")
        return "\n".join(report)

# Instanțe globale pentru Trace & Replay
global_trace_store = TraceStore()
global_replay_engine = ReplayEngine(global_trace_store)
