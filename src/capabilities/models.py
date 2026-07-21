from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

class CapabilityName(str, Enum):
    STREAMING = "streaming"
    JSON_MODE = "json_mode"
    TOOL_CALLING = "tool_calling"
    VISION = "vision"
    LONG_CONTEXT = "long_context"
    REASONING = "reasoning"

class UsageProfileType(str, Enum):
    CONVERSATIONAL_CHAT = "conversational_chat"
    CONTENT_GENERATION = "content_generation"
    DOCUMENT_ANALYSIS = "document_analysis"
    TOOL_AUTOMATION = "tool_automation"

@dataclass
class ProviderCapabilities:
    provider_name: str
    supported_capabilities: List[CapabilityName] = field(default_factory=list)
    max_context_window: int = 128000
    cost_per_1k_tokens: float = 0.002
    avg_latency_ms: float = 300.0

@dataclass
class TaskRequirements:
    required_capabilities: List[CapabilityName] = field(default_factory=list)
    min_context_window: int = 4000
    max_cost_preference: str = "medium" # low, medium, high
    max_latency_preference: str = "medium" # low, medium, high
    usage_profile: Optional[UsageProfileType] = None

@dataclass
class SelectionResult:
    recommended_provider: str
    compatibility_score: float
    reason: str
    alternatives: List[str] = field(default_factory=list)
