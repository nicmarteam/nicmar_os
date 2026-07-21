from __future__ import annotations

from typing import Any, Iterable, Optional
from src.llm.provider_factory import ProviderFactory
from src.llm.base_client import LLMResponse, LLMStreamChunk


class UnifiedLLMService:
    """Serviciu de orchestrare unificat pentru interacțiunea cu orice model LLM."""

    def __init__(self, default_provider: Optional[str] = None):
        self._default_provider = default_provider

    def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generează un răspuns complet delegând către providerul obținut din fabrică."""
        chosen_provider = provider or self._default_provider or ProviderFactory._global_config.default_provider
        
        # Instantiem clientul prin factory
        client = ProviderFactory.get_client(provider_name=chosen_provider, api_key=api_key, timeout=timeout)
        
        # Delegăm apelul către clientul concret
        return client.generate(prompt=prompt, model=model, **kwargs)

    def stream(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> Iterable[LLMStreamChunk]:
        """Returnează un flux de bucăți (stream) delegând direct iteratorul de la provider."""
        chosen_provider = provider or self._default_provider or ProviderFactory._global_config.default_provider
        
        # Instantiem clientul prin fabrică
        client = ProviderFactory.get_client(provider_name=chosen_provider, api_key=api_key, timeout=timeout)
        
        # Delegăm fluxul direct, fără transformări sau concatenări
        return client.stream(prompt=prompt, model=model, **kwargs)
