from typing import List
from src.governance.models import GovernanceContext, GovernanceEvaluationResult, GovernanceAction, CapabilityType
from src.governance.budget import BudgetEngine
from src.governance.policies import PolicyEngine
from src.governance.capabilities import CapabilityEngine

class GovernanceEvaluator:
    def __init__(self, budget_engine: BudgetEngine, policy_engine: PolicyEngine):
        self.budget_engine = budget_engine
        self.policy_engine = policy_engine

    def evaluate_request(self, context: GovernanceContext, provider_caps: List[CapabilityType] = None) -> GovernanceEvaluationResult:
        # 1. Verificare Politici (Rol, Provider, RAG, Memorie)
        policy_res = self.policy_engine.evaluate_policy(context)
        if policy_res.action != GovernanceAction.ALLOW:
            return policy_res

        # 2. Verificare Buget (Cost, Tool-uri, Pași workflow)
        budget_res = self.budget_engine.check_budget(context)
        if budget_res.action != GovernanceAction.ALLOW:
            return budget_res

        # 3. Verificare Capabilități (dacă sunt furnizate capabilitățile providerului)
        if provider_caps:
            caps_res = CapabilityEngine.verify_capabilities(context, provider_caps)
            if caps_res.action != GovernanceAction.ALLOW:
                return caps_res

        return GovernanceEvaluationResult(
            action=GovernanceAction.ALLOW,
            reason="All governance checks passed successfully",
            selected_provider=policy_res.selected_provider
        )
