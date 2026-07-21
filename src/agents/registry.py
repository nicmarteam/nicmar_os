from typing import Dict, Type
from src.agents.runtime import AgentRuntime

class AgentRegistry:
    def __init__(self):
        self._runtimes: Dict[str, AgentRuntime] = {}

    def register(self, name: str, runtime: AgentRuntime):
        self._runtimes[name] = runtime

    def get(self, name: str) -> AgentRuntime:
        if name not in self._runtimes:
            raise KeyError(f"Agentul {name} nu este înregistrat în AgentRegistry.")
        return self._runtimes[name]
