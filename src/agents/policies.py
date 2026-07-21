from dataclasses import dataclass
from src.agents.state import AgentState

@dataclass
class AgentPolicy:
    max_steps: int = 10
    max_tokens: int = 5000
    timeout_seconds: int = 60
    require_confirmation_for_sensitive_actions: bool = True

    def should_continue(self, state: AgentState) -> bool:
        if state.status in ["completed", "failed", "stopped"]:
            return False
        if state.current_step_count >= self.max_steps:
            state.status = "stopped"
            state.stop_reason = f"Atins numărul maxim de pași ({self.max_steps})."
            return False
        if state.total_tokens_used >= self.max_tokens:
            state.status = "stopped"
            state.stop_reason = f"Atins bugetul maxim de tokeni ({self.max_tokens})."
            return False
        return True
