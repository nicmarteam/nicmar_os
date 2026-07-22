from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class RequestInfo:
    trace_id: str
    prompt: str
    temperature: float
    timestamp: float
    system_prompt: str = ""
    resolved_prompt: str = ""

@dataclass
class ProviderInfo:
    provider: str
    model: str

@dataclass
class PromptInfo:
    raw_prompt: str
    rendered_prompt: str
    system_prompt: str = ""

@dataclass
class ContextInfo:
    active_context_keys: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MemoryLookupInfo:
    enabled: bool = False
    memories_loaded: List[str] = field(default_factory=list)
    memory_ids: List[str] = field(default_factory=list)
    selection_strategy: str = ""
    selection_reason: str = ""
    retrieval_time_ms: float = 0.0

@dataclass
class RAGRetrievalInfo:
    documents: List[str] = field(default_factory=list)
    chunks: List[str] = field(default_factory=list)

@dataclass
class MetricsInfo:
    ttft_ms: float = 0.0
    elapsed_ms: float = 0.0
    tokens_per_second: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0

@dataclass
class TimelineEventInfo:
    timestamp: float
    event_type: str
    details: Dict[str, Any] = field(default_factory=dict)
