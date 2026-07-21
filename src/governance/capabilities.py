from typing import List
from src.governance.models import CapabilityType, GovernanceContext, GovernanceEvaluationResult, GovernanceAction

class CapabilityEngine:
    @staticmethod
    def verify_capabilities(context: GovernanceContext, provider_capabilities: List[CapabilityType]) -> GovernanceEvaluationResult:
        """
        Verifică dacă providerul selectat suportă capabilitățile cerute de task.
        """
        for req_cap in context.required_capabilities:
            if req_cap not in provider_capabilities:
                return GovernanceEvaluationResult(
                    action=GovernanceAction.DENY,
                    reason=f"Provider does not support required capability: {req_cap.value}"
                )
        return GovernanceEvaluationResult(
            action=GovernanceAction.ALLOW,
            reason="All capabilities supported"
        )
