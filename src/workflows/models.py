from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable

@dataclass
class WorkflowContext:
    workflow_id: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    status: str = "pending" # pending, running, completed, failed

@dataclass
class WorkflowStepResult:
    step_name: str
    status: str # success, failed, skipped
    output: Any = None
    error: Optional[str] = None
