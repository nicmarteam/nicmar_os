from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

class ContextSourceType(str, Enum):
    SYSTEM_PROMPT = "system_prompt"
    USER_PROFILE = "user_profile"
    CONVERSATION_HISTORY = "conversation_history"
    MEMORY = "memory"
    RAG = "rag"
    WORKFLOW = "workflow"

@dataclass
class ContextBudget:
    max_tokens: int
    output_tokens_reserve: int
    min_system_tokens: int = 500

@dataclass
class ContextFragment:
    source_type: ContextSourceType
    content: str
    token_count: int
    priority: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextRequest:
    user_id: str
    session_id: str
    query: str
    budget: ContextBudget
    extra_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextDiagnostics:
    total_tokens_available: int
    total_tokens_used: int
    tokens_dropped: int = 0
    tokens_compressed: int = 0
    providers_used: List[str] = field(default_factory=list)
    providers_dropped: List[str] = field(default_factory=list)
    drop_reasons: Dict[str, str] = field(default_factory=dict)
    estimated_cost: float = 0.0
    latency_ms: float = 0.0

@dataclass
class ResolvedContext:
    system_prompt: str
    messages: List[Dict[str, str]]
    total_tokens: int
    diagnostics: ContextDiagnostics
