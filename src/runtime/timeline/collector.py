import time
from typing import Any, Dict, List, Optional
from src.runtime.timeline.models import TimelineEvent, TimelineEventType

class TimelineCollector:
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self._counter = 1

    def record(
        self,
        event_type: str,
        title: str,
        description: str = "",
        duration_ms: float = 0.0,
        status: str = "completed",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Înregistrează un eveniment în timp real cu timestamp exact."""
        timestamp = time.time()
        event_data = {
            "id": f"evt_{self._counter:03d}",
            "timestamp": timestamp,
            "event_type": event_type,
            "title": title,
            "description": description,
            "duration_ms": duration_ms,
            "status": status,
            "metadata": metadata or {}
        }
        self.events.append(event_data)
        self._counter += 1

    def get_events(self) -> List[Dict[str, Any]]:
        return self.events
