from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

class NodeType(str, Enum):
    RETRIEVE_MEMORY = "retrieve_memory"
    RETRIEVE_RAG = "retrieve_rag"
    LLM_EXECUTION = "llm_execution"
    TOOL_EXECUTION = "tool_execution"
    SAVE_MEMORY = "save_memory"

@dataclass
class ExecutionNode:
    node_id: str
    node_type: NodeType
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_provider: Optional[str] = None

@dataclass
class ExecutionPlan:
    task_prompt: str
    user_role: str
    nodes: List[ExecutionNode] = field(default_factory=list)
    estimated_total_tokens: int = 0
    estimated_cost: float = 0.0

class TaskAnalyzer:
    @staticmethod
    def analyze(prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "istoric" in prompt_lower || "vorbit" in prompt_lower || "mai știi" in prompt_lower:
            return "conversational_memory_task"
        elif "caută" in prompt_lower || "produs" in prompt_lower || "document" in prompt_lower:
            return "rag_search_task"
        elif "calculează" in prompt_lower || "tool" in prompt_lower:
            return "tool_execution_task"
        return "standard_generation_task"

class PlanGenerator:
    @staticmethod
    def generate_plan(prompt: str, user_role: str) -> ExecutionPlan:
        task_type = TaskAnalyzer.analyze(prompt)
        nodes: List[ExecutionNode] = []
        
        # Politică bazată pe rol: Guest nu are acces la memorie
        allow_memory = (user_role != "guest")

        if task_type == "conversational_memory_task":
            if allow_memory:
                nodes.append(ExecutionNode("node_1", NodeType.RETRIEVE_MEMORY, "Preia preferințele și istoricul din memorie"))
            nodes.append(ExecutionNode("node_2", NodeType.RETRIEVE_RAG, "Preia contextul relevant din documentația NicMar"))
            nodes.append(ExecutionNode("node_3", NodeType.LLM_EXECUTION, "Generează răspunsul optimizat", required_provider="anthropic"))
            if allow_memory:
                nodes.append(ExecutionNode("node_4", NodeType.SAVE_MEMORY, "Salvează noua interacțiune în memorie"))

        elif task_type == "rag_search_task":
            nodes.append(ExecutionNode("node_1", NodeType.RETRIEVE_RAG, "Caută în baza de cunoștințe"))
            nodes.append(ExecutionNode("node_2", NodeType.LLM_EXECUTION, "Redactează sinteza", required_provider="openai"))

        else:
            nodes.append(ExecutionNode("node_1", NodeType.LLM_EXECUTION, "Execută generarea standard", required_provider="openai"))

        # Estimări simple pentru Simulator
        est_tokens = len(prompt.split()) * 15 + len(nodes) * 500
        est_cost = round(est_tokens * 0.000003, 5)

        return ExecutionPlan(
            task_prompt=prompt,
            user_role=user_role,
            nodes=nodes,
            estimated_total_tokens=est_tokens,
            estimated_cost=est_cost
        )
