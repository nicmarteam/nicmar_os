from typing import Dict, List, Optional
from src.capabilities.models import ProviderCapabilities, CapabilityName

class CapabilityRegistry:
    def __init__(self):
        self._providers: Dict[str, ProviderCapabilities] = {}
        self._load_default_providers()

    def _load_default_providers(self) -> None:
        # Înregistrăm providerii principali ai platformei
        self.register_provider(ProviderCapabilities(
            provider_name="anthropic",
            supported_capabilities=[
                CapabilityName.STREAMING,
                CapabilityName.JSON_MODE,
                CapabilityName.TOOL_CALLING,
                CapabilityName.VISION,
                CapabilityName.LONG_CONTEXT
            ],
            max_context_window=200000,
            cost_per_1k_tokens=0.003,
            avg_latency_ms=400.0
        ))

        self.register_provider(ProviderCapabilities(
            provider_name="openai",
            supported_capabilities=[
                CapabilityName.STREAMING,
                CapabilityName.JSON_MODE,
                CapabilityName.TOOL_CALLING,
                CapabilityName.VISION,
                CapabilityName.REASONING,
                CapabilityName.LONG_CONTEXT
            ],
            max_context_window=128000,
            cost_per_1k_tokens=0.002,
            avg_latency_ms=250.0
        ))

        self.register_provider(ProviderCapabilities(
            provider_name="gemini",
            supported_capabilities=[
                CapabilityName.STREAMING,
                CapabilityName.JSON_MODE,
                CapabilityName.TOOL_CALLING,
                CapabilityName.VISION,
                CapabilityName.LONG_CONTEXT
            ],
            max_context_window=1000000,
            cost_per_1k_tokens=0.001,
            avg_latency_ms=350.0
        ))

    def register_provider(self, provider: ProviderCapabilities) -> None:
        self._providers[provider.provider_name] = provider

    def get_provider(self, name: str) -> Optional[ProviderCapabilities]:
        return self._providers.get(name)

    def list_all_providers(self) -> List[ProviderCapabilities]:
        return list(self._providers.values())
