from src.governance.models import GovernanceBudget, GovernanceContext, GovernanceEvaluationResult, GovernanceAction

class BudgetEngine:
    def __init__(self, default_budget: GovernanceBudget):
        self.default_budget = default_budget
        # În viitor aici putem conecta un storage real (Redis / SQLite) pentru consumul zilnic pe utilizator
        self._daily_usage: dict = {}

    def check_budget(self, context: GovernanceContext) -> GovernanceEvaluationResult:
        # Verificăm numărul maxim de tool-uri permise per execuție
        if context.tool_count > self.default_budget.max_tools_per_execution:
            return GovernanceEvaluationResult(
                action=GovernanceAction.DENY,
                reason=f"Exceeded max tools allowed per execution: {context.tool_count} > {self.default_budget.max_tools_per_execution}"
            )

        # Verificăm pașii de workflow
        if context.workflow_steps > self.default_budget.max_workflow_steps:
            return GovernanceEvaluationResult(
                action=GovernanceAction.DENY,
                reason=f"Exceeded max workflow steps allowed: {context.workflow_steps} > {self.default_budget.max_workflow_steps}"
            )

        # Verificăm costul estimat vs limita zilnică
        current_spent = self._daily_usage.get(context.user_id, 0.0)
        if current_spent + context.estimated_cost > self.default_budget.daily_cost_limit:
            return GovernanceEvaluationResult(
                action=GovernanceAction.RATE_LIMIT,
                reason=f"Daily cost limit reached for user {context.user_id} (${current_spent:.4f} / ${self.default_budget.daily_cost_limit})"
            )

        return GovernanceEvaluationResult(
            action=GovernanceAction.ALLOW,
            reason="Budget check passed"
        )

    def record_spend(self, user_id: str, cost: float) -> None:
        current = self._daily_usage.get(user_id, 0.0)
        self._daily_usage[user_id] = current + cost
