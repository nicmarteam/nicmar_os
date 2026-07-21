from typing import List, Tuple
from src.capabilities.models import TaskRequirements, ProviderCapabilities, SelectionResult
from src.capabilities.registry import CapabilityRegistry

class CapabilityMatcher:
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def match_and_rank(self, requirements: TaskRequirements, allowed_providers: List[str] = None) -> List[Tuple[ProviderCapabilities, float]]:
        """
        Filtrează providerii care îndeplinesc cerințele și calculează un scor de compatibilitate/ranking.
        """
        all_providers = self.registry.list_all_providers()
        scored_providers: List[Tuple[ProviderCapabilities, float]] = []

        for provider in all_providers:
            # 1. Verificăm lista de provideri permisi (dacă e dată de guvernanță)
            if allowed_providers and provider.provider_name not in allowed_providers:
                continue

            # 2. Verificăm fereastra de context minimă
            if provider.max_context_window < requirements.min_context_window:
                continue

            # 3. Verificăm dacă suportă toate capabilitățile cerute
            supported_set = set(provider.supported_capabilities)
            required_set = set(requirements.required_capabilities)
            if not required_set.issubset(supported_set):
                continue

            # 4. Calculăm un scor de ranking bazat pe preferințe (cost, latență)
            score = 100.0

            # Ajustare cost
            if requirements.max_cost_preference == "low":
                score -= (provider.cost_per_1k_tokens * 10000)
            
            # Ajustare latență
            if requirements.max_latency_preference == "low":
                score -= (provider.avg_latency_ms / 10.0)

            scored_providers.append((provider, max(0.0, score)))

        # Sortăm descrescător după scor
        scored_providers.sort(key=lambda x: x[1], reverse=True)
        return scored_providers

    def select_best_provider(self, requirements: TaskRequirements, allowed_providers: List[str] = None) -> SelectionResult:
        ranked = self.match_and_rank(requirements, allowed_providers)
        
        if not ranked:
            return SelectionResult(
                recommended_provider="openai", # fallback sigur
                compatibility_score=0.0,
                reason="No providers matched the strict requirements, falling back to default.",
                alternatives=[]
            )

        best_provider, best_score = ranked[0]
        alternatives = [p.provider_name for p, _ in ranked[1:]]

        return SelectionResult(
            recommended_provider=best_provider.provider_name,
            compatibility_score=best_score,
            reason=f"Provider {best_provider.provider_name} matched all requirements with score {best_score:.2f}",
            alternatives=alternatives
        )
