from typing import Dict, Any
from src.runtime.replay.models import ReplayExecution, ReplayStep

class ReplayBuilder:
    @staticmethod
    def from_execution(execution_id: str, session_id: str, raw_data: Dict[str, Any]) -> ReplayExecution:
        steps = [
            ReplayStep(
                step_id="step_prompt",
                component="prompt",
                input_data={"raw_prompt": raw_data.get("prompt", "")},
                output_data={"processed_prompt": raw_data.get("prompt", "")},
                metrics={}
            ),
            ReplayStep(
                step_id="step_provider",
                component="provider",
                input_data={"provider": raw_data.get("provider", "unknown")},
                output_data={"response": raw_data.get("response", "")},
                metrics=raw_data.get("metrics", {})
            )
        ]
        return ReplayExecution(
            execution_id=execution_id,
            session_id=session_id,
            timestamp=raw_data.get("timestamp", "2026-07-23"),
            steps=steps,
            metadata=raw_data.get("metadata", {})
        )
