from typing import Dict, Any, Callable
from src.agents.state import AgentState, AgentStep

class AgentExecutor:
    def __init__(self, tool_registry: Dict[str, Callable] = None):
        self.tool_registry = tool_registry or {}

    def register_tool(self, name: str, func: Callable):
        self.tool_registry[name] = func

    def execute_step(self, state: AgentState, step: AgentStep) -> AgentStep:
        """Execută acțiunea determinată de planner folosind tool-urile disponibile sau logica internă."""
        try:
            step.status = "running"
            
            # Logică de execuție flexibilă pe baza acțiunii
            if step.action == "analyze_goal":
                step.observation = f"Obiectiv analizat cu succes: {state.goal}"
                step.status = "success"
            elif step.action in self.tool_registry:
                tool_func = self.tool_registry[step.action]
                result = tool_func(**step.action_input)
                step.observation = str(result)
                step.status = "success"
            else:
                step.observation = f"Acțiune simulată executată pentru: {step.action}"
                step.status = "success"
                
        except Exception as e:
            step.observation = f"Eroare în timpul execuției: {str(e)}"
            step.status = "failed"
            
        return step
