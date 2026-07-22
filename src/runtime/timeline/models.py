import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

class TimelineEventType:
    REQUEST_CREATED = "request_created"
    CONTEXT_BUILT = "context_built"
    MEMORY_LOADED = "memory_loaded"
    RAG_SEARCH = "rag_search"
    PROMPT_RENDERED = "prompt_rendered"
    PROVIDER_REQUEST = "provider_request"
    FIRST_TOKEN = "first_token"
    STREAM_STARTED = "stream_started"
    STREAM_FINISHED = "stream_finished"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_ERROR = "execution_error"

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
