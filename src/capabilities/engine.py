from typing import List, Optional
from src.capabilities.models import TaskRequirements, SelectionResult, CapabilityName
from src.capabilities.registry import CapabilityRegistry
from src.capabilities.matcher import CapabilityMatcher
from src.governance.runtime import GovernanceRuntime
from src.governance.models import GovernanceContext

class CapabilityEngineFacade:
    def __init__(self, governance_runtime: Optional[GovernanceRuntime] = None):
        self.registry = CapabilityRegistry()
        self.matcher = CapabilityMatcher(self.registry)
        self.governance_runtime = governance_runtime

    def resolve_provider(self, requirements: TaskRequirements, governance_context: Optional[GovernanceContext] = None) -> SelectionResult:
        """
        Interoghează guvernanța pentru a afla providerii permisi, 
        apoi aplică motorul de capabilități și ranking pentru selecția finală.
        """
        allowed_providers = None

        if self.governance_runtime and governance_context:
            # Rulăm mai întâi regulile de guvernanță (rol, cost, etc.)
            # Dacă guvernanța permite, obținem providerii permiși din politica de rol
            policy = self.governance_runtime.policy_engine._policies.get(governance_context.role)
            if policy:
                allowed_providers = policy.allowed_providers

        # Apelăm Matcher-ul pentru a alege cel mai bun provider compatibil
        result = self.matcher.select_best_provider(requirements, allowed_providers=allowed_providers)
        return result
