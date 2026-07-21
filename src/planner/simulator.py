from src.planner.engine import ExecutionPlan

class PlannerSimulator:
    @staticmethod
    def simulate(plan: ExecutionPlan) -> str:
        """
        Simulează execuția planului și afișează un raport detaliat de diagnostic
        înainte de rularea efectivă, conform strategiei stabilite.
        """
        report = []
        report.append("=== NICMAR OS EXECUTION PLAN SIMULATION ===")
        report.append(f"Task Prompt: \"{plan.task_prompt}\"")
        report.append(f"User Role: {plan.user_role}")
        report.append(f"Total Steps (Nodes): {len(plan.nodes)}")
        report.append(f"Estimated Tokens: {plan.estimated_total_tokens}")
        report.append(f"Estimated Cost: ${plan.estimated_cost:.5f}")
        report.append("--- Execution Flow ---")
        
        for i, node in enumerate(plan.nodes, 1):
            prov_info = f" [Provider: {node.required_provider}]" if node.required_provider else ""
            report.append(f"  {i}. [{node.node_type.value.upper()}] {node.description}{prov_info}")
            
        report.append("===========================================")
        return "\n".join(report)
