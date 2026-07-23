from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class TimelineSelection:
    trace_id: str
    selected_event_id: Optional[str] = None
    selected_section: Optional[str] = None
    metadata_context: Dict[str, Any] = field(default_factory=dict)

    def is_event_selected(self) -> bool:
        return self.selected_event_id is not None
