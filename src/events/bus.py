from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

class EventType(str, Enum):
    PLAN_CREATED = "plan_created"
    NODE_STARTED = "node_started"
    NODE_FINISHED = "node_finished"
    PROVIDER_SELECTED = "provider_selected"
    LLM_STARTED = "llm_started"
    LLM_COMPLETED = "llm_completed"
    TOOL_EXECUTED = "tool_executed"
    MEMORY_STORED = "memory_stored"
    WORKFLOW_FINISHED = "workflow_finished"

@dataclass
class SystemEvent:
    event_type: EventType
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)

class EventBus:
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable[[SystemEvent], None]]] = {}

    def subscribe(self, event_type: EventType, listener: Callable[[SystemEvent], None]) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def publish(self, event: SystemEvent) -> None:
        """
        Publică un eveniment către toți ascultătorii înregistrați (logging, dashboard, analytics).
        """
        listeners = self._listeners.get(event.event_type, [])
        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                # Evităm ca o eroare într-un listener să oprească fluxul principal
                print(f"[EventBus Error] Listener failed for {event.event_type}: {e}")

# Instanță globală unică pentru Event Bus în întreaga platformă
global_event_bus = EventBus()
