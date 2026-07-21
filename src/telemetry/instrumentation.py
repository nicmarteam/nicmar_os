from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import uuid
from src.events.bus import global_event_bus, SystemEvent, EventType

@dataclass
class CorrelationContext:
    conversation_id: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: Optional[str] = None
    execution_id: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))
    node_id: Optional[str] = None

class RuntimeInstrumenter:
    @staticmethod
    def emit(event_type: EventType, correlation: CorrelationContext, payload: Dict[str, Any] = None) -> None:
        """
        Emite un eveniment standardizat injectând automat contextul de corelație.
        """
        data = {
            "conversation_id": correlation.conversation_id,
            "request_id": correlation.request_id,
            "workflow_id": correlation.workflow_id,
            "execution_id": correlation.execution_id,
            "node_id": correlation.node_id,
        }
        if payload:
            data.update(payload)

        event = SystemEvent(event_type=event_type, payload=data)
        global_event_bus.publish(event)
