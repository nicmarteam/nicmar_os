from typing import List, Dict, Any
from src.governance.models import GovernanceContext, GovernanceEvaluationResult, GovernanceAction, GovernanceBudget, CapabilityType
from src.governance.budget import BudgetEngine
from src.governance.policies import PolicyEngine
from src.governance.evaluator import GovernanceEvaluator
from src.governance.exceptions import PolicyViolationError, BudgetExceededError

class GovernanceRuntime:
    def __init__(self, default_budget: GovernanceBudget):
        self.budget_engine = BudgetEngine(default_budget)
        self.policy_engine = PolicyEngine()
        self.evaluator = GovernanceEvaluator(self.budget_engine, self.policy_engine)

    def enforce(self, context: GovernanceContext, provider_caps: List[CapabilityType] = None) -> str:
        """
        Validează cererea prin motorul de guvernanță. 
        Aruncă excepții dacă regulile sunt încălcate sau returnează providerul validat.
        """
        result = self.evaluator.evaluate_request(context, provider_caps)
        
        if result.action == GovernanceAction.DENY:
            raise PolicyViolationError(f"Governance Denied: {result.reason}")
        
        if result.action == GovernanceAction.RATE_LIMIT:
            raise BudgetExceededError(f"Governance Rate Limit: {result.reason}")

        return result.selected_provider or "openai"
