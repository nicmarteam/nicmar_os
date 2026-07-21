from src.telemetry.instrumentation import RuntimeInstrumenter, CorrelationContext
from src.events.bus import EventType, global_event_bus
from src.capabilities.models import TaskRequirements
from src.planner.engine import PlanGenerator

class InstrumentedRuntimeRunner:
    def __init__(self):
        # Înregistrăm un listener global de telemetrie pentru a vedea evenimentele în consolă/loguri
        global_event_bus.subscribe(EventType.PLAN_CREATED, self._on_event)
        global_event_bus.subscribe(EventType.PROVIDER_SELECTED, self._on_event)
        global_event_bus.subscribe(EventType.NODE_STARTED, self._on_event)

    def _on_event(self, event):
        print(f"[TELEMETRY EVENT] -> {event.event_type.value.upper()} | Data: {event.payload}")

    def execute_task_with_telemetry(self, prompt: str, user_role: str):
        correlation = CorrelationContext()
        
        # 1. Generăm planul și emitem evenimentul
        plan = PlanGenerator.generate_plan(prompt, user_role)
        RuntimeInstrumenter.emit(
            EventType.PLAN_CREATED, 
            correlation, 
            {"prompt": prompt, "role": user_role, "nodes_count": len(plan.nodes)}
        )

        # 2. Simulăm execuția fiecărui nod din plan cu instrumentare completă
        for node in plan.nodes:
            correlation.node_id = node.node_id
            RuntimeInstrumenter.emit(
                EventType.NODE_STARTED,
                correlation,
                {"node_type": node.node_type.value, "description": node.description}
            )

        return plan
