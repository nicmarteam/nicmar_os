from __future__ import annotations

from typing import Any
from src.llm.claude_client import ClaudeClient
from src.llm.openai_client import OpenAIClient
from src.llm.provider_registry import ProviderRegistry
from src.llm.config import LLMConfig, ProviderConfig
from src.llm.secrets import SecretProvider


class ProviderFactory:
    """Fabrică responsabilă cu instțierea clienților LLM folosind configurația centralizată și secretele."""

    _global_config: LLMConfig = LLMConfig.default_config()

    @classmethod
    def set_config(cls, config: LLMConfig) -> None:
        cls._global_config = config

    @classmethod
    def get_client(cls, provider_name: str, api_key: str | None = None, timeout: float | None = None) -> Any:
        normalized_name = provider_name.lower()

        # 1. Asigurăm înregistrarea providerilor cunoscuți
        if "anthropic" not in ProviderRegistry._registry:
            ProviderRegistry.register("anthropic", ClaudeClient)
        if "openai" not in ProviderRegistry._registry:
            ProviderRegistry.register("openai", OpenAIClient)

        client_class = ProviderRegistry.get(normalized_name)

        # 2. Preluăm cheia API via SecretProvider (dacă nu este pasată explicit)
        resolved_api_key = api_key or SecretProvider.get_api_key(normalized_name)

        # 3. Preluăm configurația providerului din config-ul centralizat (dacă există)
        try:
            prov_config: ProviderConfig = cls._global_config.get_provider_config(normalized_name)
            resolved_timeout = timeout if timeout is not None else prov_config.timeout
        except ValueError:
            resolved_timeout = timeout if timeout is not None else 30.0

        # 4. Instantiem clientul cu parametrii rezolvați
        # (Presupunem că OpenAIClient / ClaudeClient acceptă api_key și timeout)
        return client_class(api_key=resolved_api_key, timeout=resolved_timeout)
