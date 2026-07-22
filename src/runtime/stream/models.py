from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

class StreamChunkType(str, Enum):
    START = "start"
    DELTA = "delta"
    TOOL = "tool"
    METRICS = "metrics"
    ERROR = "error"
    FINISH = "finish"

class RuntimeStatus(str, Enum):
    IDLE = "IDLE"
    CONNECTING = "CONNECTING"
    WAITING_FIRST_TOKEN = "WAITING_FIRST_TOKEN"
    STREAMING = "STREAMING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"
    CANCELLED = "CANCELLED"

@dataclass
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0

@dataclass
class LLMStreamChunk:
    chunk_type: StreamChunkType
    text: str = ""
    provider: str = ""
    model: str = ""
    usage: Optional[TokenUsage] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StreamMetrics:
    started_at: float = 0.0
    first_token_at: float = 0.0
    finished_at: float = 0.0
    ttft_ms: float = 0.0
    elapsed_ms: float = 0.0
    tokens_per_second: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0

@dataclass
class ExecutionContext:
    provider: str
    model: str
    system_prompt: str = ""
    user_prompt: str = ""
    resolved_prompt: str = ""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    session_id: str = ""
    trace_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MemoryTrace:
    enabled: bool = False
    memories_loaded: List[str] = field(default_factory=list)
    memory_ids: List[str] = field(default_factory=list)
    selection_strategy: str = ""
    selection_reason: str = ""
    retrieval_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RuntimeExecution:
    trace_id: str
    provider: str
    model: str
    prompt: str
    temperature: float = 0.7
    context: Optional[ExecutionContext] = None
    memory: Optional[MemoryTrace] = field(default_factory=MemoryTrace)
    status: RuntimeStatus = RuntimeStatus.IDLE
    metrics: StreamMetrics = field(default_factory=StreamMetrics)
    response_text: str = ""
    error_message: Optional[str] = None
    chunks: List[LLMStreamChunk] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
