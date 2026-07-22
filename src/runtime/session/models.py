from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time

@dataclass
class RuntimeSession:
    session_id: str
    created_at: float = field(default_factory=time.time)
    user_id: str = "default_user"
    executions: List[Any] = field(default_factory=list)
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_execution(self, execution: Any) -> None:
        self.executions.append(execution)

    def close(self) -> None:
        self.status = "closed"
