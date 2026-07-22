from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

class StreamChunkType(str, Enum):
    START = "start"
    DELTA = "delta"
    TOOL = "tool"
    METRICS = "metrics"
    ERROR = "error"
    FINISH = "finish"

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
class StreamSession:
    request_id: str
    provider: str
    model: str
    metrics: StreamMetrics
    chunks: list[LLMStreamChunk] = field(default_factory=list)
