from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ProviderConfig:
    """Configurația specifică pentru un anumit provider LLM."""
    provider_name: str
    default_model: str
    timeout: float = 30.0
    max_retries: int = 3
    base_url: str | None = None
    extra_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMConfig:
    """Configurația globală a sistemului LLM."""
    default_provider: str = "openai"
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)

    def get_provider_config(self, provider_name: str) -> ProviderConfig:
        normalized_name = provider_name.lower()
        if normalized_name not in self.providers:
            raise ValueError(f"Nu există o configurație definită pentru providerul: '{provider_name}'")
        return self.providers[normalized_name]

    @classmethod
    def default_config(cls) -> LLMConfig:
        """Returnează o configurație implicită standard pentru aplicație."""
        return cls(
            default_provider="openai",
            providers={
                "openai": ProviderConfig(
                    provider_name="openai",
                    default_model="gpt-4o",
                    timeout=30.0,
                    max_retries=3
                ),
                "anthropic": ProviderConfig(
                    provider_name="anthropic",
                    default_model="claude-3-5-sonnet-20241022",
                    timeout=30.0,
                    max_retries=3
                ),
                "gemini": ProviderConfig(
                    provider_name="gemini",
                    default_model="gemini-1.5-pro",
                    timeout=30.0,
                    max_retries=3
                )
            }
        )
