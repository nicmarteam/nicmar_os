from typing import List, Dict, Any
from src.agents.state import AgentState, AgentStep

class AgentPlanner:
    def plan_next_step(self, state: AgentState) -> AgentStep:
        """Analizează starea curentă și decide următorul pas în vederea atingeri obiectivului."""
        next_step_num = state.current_step_count + 1
        
        # Dacă este primul pas și nu există pași executați
        if not state.steps:
            thought = f"Am primit obiectivul: '{state.goal}'. Trebuie să încep prin a analiza cerința și a extrage informațiile necesare."
            action = "analyze_goal"
        else:
            # Planificare bazată pe istoricul pașilor anteriori
            last_step = state.steps[-1]
            thought = f"Pasul anterior ({last_step.action}) s-a încheiat cu statusul {last_step.status}. Calculez următorul pas."
            action = "execute_task_action"

        return AgentStep(
            step_number=next_step_num,
            thought=thought,
            action=action,
            action_input={"goal": state.goal, "variables": state.variables},
            status="pending"
        )
