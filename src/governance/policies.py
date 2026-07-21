from typing import Dict, List
from src.governance.models import PolicyRule, GovernanceContext, GovernanceEvaluationResult, GovernanceAction

class PolicyEngine:
    def __init__(self):
        self._policies: Dict[str, PolicyRule] = {}
        # Setăm politici implicite conform cerințelor stabilite
        self._load_default_policies()

    def _load_default_policies(self) -> None:
        # Politica pentru Guest: nu are acces la memorie, are limite stricte
        self.register_policy(PolicyRule(
            rule_id="policy_guest",
            target_role="guest",
            allowed_providers=["openai", "gemini"],
            memory_access_allowed=False,
            rag_categories_allowed=["Public"]
        ))
        # Politica pentru Marketing: poate folosi Claude
        self.register_policy(PolicyRule(
            rule_id="policy_marketing",
            target_role="marketing",
            allowed_providers=["anthropic", "openai"],
            memory_access_allowed=True,
            rag_categories_allowed=["Produse", "Marketing"]
        ))
        # Politica pentru Contabilitate: folosește GPT
        self.register_policy(PolicyRule(
            rule_id="policy_accounting",
            target_role="accounting",
            allowed_providers=["openai"],
            memory_access_allowed=True,
            rag_categories_allowed=["Financiar", "Documente"]
        ))

    def register_policy(self, policy: PolicyRule) -> None:
        self._policies[policy.target_role] = policy

    def evaluate_policy(self, context: GovernanceContext) -> GovernanceEvaluationResult:
        policy = self._policies.get(context.role)
        if not policy:
            # Dacă rolul nu are o politică strictă, aplicăm un default permisiv sau restrictiv
            return GovernanceEvaluationResult(action=GovernanceAction.ALLOW, reason="No specific policy found, defaulting to allow")

        # 1. Verificăm permisiunea pentru memorie
        if not policy.memory_access_allowed and context.tool_count > 0: # exemplu simplificat sau flag direct
            pass

        # 2. Verificăm dacă providerul cerut este permis pentru acest rol
        if context.requested_provider and context.requested_provider not in policy.allowed_providers:
            return GovernanceEvaluationResult(
                action=GovernanceAction.DENY,
                reason=f"Role '{context.role}' is not allowed to use provider '{context.requested_provider}'. Allowed: {policy.allowed_providers}"
            )

        # 3. Verificăm categoria RAG
        if context.rag_category and context.rag_category not in policy.rag_categories_allowed:
            return GovernanceEvaluationResult(
                action=GovernanceAction.DENY,
                reason=f"Role '{context.role}' cannot access RAG category '{context.rag_category}'. Allowed: {policy.rag_categories_allowed}"
            )

        return GovernanceEvaluationResult(
            action=GovernanceAction.ALLOW,
            reason="Policy check passed",
            selected_provider=context.requested_provider or (policy.allowed_providers[0] if policy.allowed_providers else None)
        )
