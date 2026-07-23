from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ReplayStep:
    step_id: str
    component: str  # prompt, context, memory, rag, provider
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    metrics: Dict[str, Any]

@dataclass
class ReplayExecution:
    execution_id: str
    session_id: str
    timestamp: str
    steps: List[ReplayStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
