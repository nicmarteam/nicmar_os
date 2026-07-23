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
class RetrievedChunkInfo:
    chunk_id: str = ""
    document_id: str = ""
    source: str = ""
    score: float = 0.0
    content_preview: str = ""

@dataclass
class RAGRetrievalInfo:
    enabled: bool = False
    query: str = ""
    retrieval_strategy: str = ""
    total_chunks: int = 0
    retrieved_chunks: List[RetrievedChunkInfo] = field(default_factory=list)
    selected_chunk_ids: List[str] = field(default_factory=list)
    retrieval_time_ms: float = 0.0

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
