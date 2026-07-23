from dataclasses import dataclass, field
from typing import List, Dict, Any
from src.runtime.session.models import RuntimeSession

@dataclass
class SessionSummary:
    session_id: str
    user_id: str
    status: str
    started_at: float
    last_activity_at: float
    execution_count: int
    total_duration_ms: float
    total_input_tokens: int
    total_output_tokens: int
    estimated_total_cost: float
    providers_used: List[str] = field(default_factory=list)
    models_used: List[str] = field(default_factory=list)
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_session(cls, session: RuntimeSession) -> "SessionSummary":
        executions = session.executions
        
        total_duration = sum(getattr(e.metrics, 'elapsed_ms', 0.0) for e in executions)
        total_input = sum(getattr(e.metrics, 'input_tokens', 0) for e in executions)
        total_output = sum(getattr(e.metrics, 'output_tokens', 0) for e in executions)
        total_cost = sum(getattr(e.metrics, 'estimated_cost', 0.0) for e in executions)
        
        providers = sorted(list(set(e.provider for e in executions if e.provider)))
        models = sorted(list(set(e.model for e in executions if e.model)))
        errors = sum(1 for e in executions if getattr(e, 'status', 'success') == 'error')

        started_at = session.created_at
        last_activity = session.metadata.get("last_activity", started_at)

        return cls(
            session_id=session.session_id,
            user_id=session.user_id,
            status=session.status,
            started_at=started_at,
            last_activity_at=last_activity,
            execution_count=len(executions),
            total_duration_ms=total_duration,
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            estimated_total_cost=total_cost,
            providers_used=providers,
            models_used=models,
            error_count=errors,
            metadata=session.metadata
        )
