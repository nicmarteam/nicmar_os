from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class AgentStep:
    step_number: int
    thought: str
    action: str
    action_input: Dict[str, Any] = field(default_factory=dict)
    observation: Optional[str] = None
    status: str = "pending" # pending, success, failed

@dataclass
class AgentState:
    agent_id: str
    goal: str
    status: str = "initialized" # initialized, running, completed, failed, stopped
    steps: List[AgentStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    stop_reason: Optional[str] = None
    total_tokens_used: int = 0
    current_step_count: int = 0
