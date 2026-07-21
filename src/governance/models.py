from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

class GovernanceAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    RATE_LIMIT = "rate_limit"
    REQUIRE_APPROVAL = "require_approval"

class CapabilityType(str, Enum):
    STREAMING = "streaming"
    JSON_MODE = "json_mode"
    TOOL_CALLING = "tool_calling"
    VISION = "vision"
    EMBEDDINGS = "embeddings"

@dataclass
class GovernanceBudget:
    daily_cost_limit: float
    max_tokens_per_request: int
    max_tools_per_execution: int
    max_workflow_steps: int

@dataclass
class PolicyRule:
    rule_id: str
    target_role: str  # ex: "guest", "marketing", "accounting", "admin"
    allowed_providers: List[str]
    denied_capabilities: List[CapabilityType] = field(default_factory=list)
    memory_access_allowed: bool = True
    rag_categories_allowed: List[str] = field(default_factory=list)

@dataclass
class GovernanceContext:
    user_id: str
    role: str
    session_id: str
    requested_provider: Optional[str] = None
    required_capabilities: List[CapabilityType] = field(default_factory=list)
    estimated_cost: float = 0.0
    tool_count: int = 0
    workflow_steps: int = 0
    rag_category: Optional[str] = None

@dataclass
class GovernanceEvaluationResult:
    action: GovernanceAction
    reason: str
    selected_provider: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
