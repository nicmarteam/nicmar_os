from typing import Dict, Any
from src.runtime.replay.models import ReplayExecution

class ReplayCompare:
    @staticmethod
    def compare(exec_a: ReplayExecution, exec_b: ReplayExecution) -> Dict[str, Any]:
        return {
            "execution_a": exec_a.execution_id,
            "execution_b": exec_b.execution_id,
            "steps_count_diff": len(exec_b.steps) - len(exec_a.steps),
            "status": "Compared successfully"
        }
