from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class TimelineEvent:
    id: str
    timestamp: float
    event_type: str
    title: str
    description: str = ""
    duration_ms: float = 0.0
    status: str = "completed"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionTimeline:
    trace_id: str
    started_at: float = 0.0
    finished_at: float = 0.0
    total_duration_ms: float = 0.0
    events: List[TimelineEvent] = field(default_factory=list)
