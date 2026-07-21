from __future__ import annotations

from src.llm.claude_client import ClaudeClient
from src.llm.openai_client import OpenAIClient
from src.llm.provider_registry import ProviderRegistry

class ProviderFactory:
    """Fabrică responsabilă cu instțierea clienților LLM pe baza registry-ului."""

    @staticmethod
    def get_client(provider_name: str, api_key: str | None = None):
        if "anthropic" not in ProviderRegistry._registry:
            ProviderRegistry.register("anthropic", ClaudeClient)
        if "openai" not in ProviderRegistry._registry:
            ProviderRegistry.register("openai", OpenAIClient)

        client_class = ProviderRegistry.get(provider_name)
        return client_class(api_key=api_key)
