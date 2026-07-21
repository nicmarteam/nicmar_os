from typing import Optional
from src.agents.state import AgentState
from src.agents.policies import AgentPolicy
from src.agents.planner import AgentPlanner
from src.agents.executor import AgentExecutor

class AgentRuntime:
    def __init__(self, planner: AgentPlanner, executor: AgentExecutor, policy: Optional[AgentPolicy] = None):
        self.planner = planner
        self.executor = executor
        self.policy = policy or AgentPolicy()

    def run(self, state: AgentState) -> AgentState:
        """Execută bucla agentului (Loop) până la atingerea obiectivului sau oprirea prin politici."""
        state.status = "running"
        
        while self.policy.should_continue(state):
            # 1. Planificare pas
            step = self.planner.plan_next_step(state)
            
            # 2. Execuție pas
            executed_step = self.executor.execute_step(state, step)
            
            # 3. Actualizare stare
            state.steps.append(executed_step)
            state.current_step_count += 1
            
            # Condiție simplă de finalizare pentru test/demo (dacă s-au făcut 2 pași sau s-a atins scopul)
            if state.current_step_count >= 2 and state.status == "running":
                state.status = "completed"
                state.stop_reason = "Obiectiv îndeplinit cu succes."
                break

        if state.status == "running":
            state.status = "completed"
            
        return state
