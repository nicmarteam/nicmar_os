from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class RequestInfo:
    trace_id: str
    prompt: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timestamp: float = 0.0

@dataclass
class ProviderInfo:
    provider: str
    model: str
    api_endpoint: Optional[str] = None

@dataclass
class PromptInfo:
    raw_prompt: str
    rendered_prompt: str
    system_instruction: Optional[str] = None

@dataclass
class ContextInfo:
    items: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class MemoryLookupInfo:
    queries: List[str] = field(default_factory=list)
    retrieved_memories: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class RAGRetrievalInfo:
    query: str = ""
    documents: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ToolExecutionInfo:
    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    duration_ms: float = 0.0

@dataclass
class TimelineEventInfo:
    timestamp: float
    event_type: str
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricsInfo:
    ttft_ms: float = 0.0
    elapsed_ms: float = 0.0
    tokens_per_second: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
