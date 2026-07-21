from __future__ import annotations

from typing import Iterator, Any
from src.llm.provider_factory import ProviderFactory
from src.llm.streaming.models import LLMStreamChunk


class UnifiedLLMService:
    """Serviciu de orchestrare unificat care expune o singură interfață către restul aplicației."""

    def __init__(self, default_provider: str = "openai", default_model: str | None = None):
        self.default_provider = default_provider
        self.default_model = default_model

    def generate(
        self,
        prompt: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        max_tokens: int = 1024,
    ) -> str:
        """Generează un răspuns text folosind providerul specificat sau cel implicit."""
        target_provider = provider or self.default_provider
        client = ProviderFactory.get_client(target_provider)
        
        # Dacă clientul suportă generate() cu model specificat
        kwargs: dict[str, Any] = {"max_tokens": max_tokens}
        if model:
            kwargs["model"] = model
        elif self.default_model:
            kwargs["model"] = self.default_model

        return client.generate(prompt, **kwargs)

    def stream(
        self,
        prompt: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        max_tokens: int = 1024,
    ) -> Iterator[LLMStreamChunk]:
        """Pornește un flux de streaming folosind providerul specificat sau cel implicit."""
        target_provider = provider or self.default_provider
        client = ProviderFactory.get_client(target_provider)

        kwargs: dict[str, Any] = {"max_tokens": max_tokens}
        if model:
            kwargs["model"] = model
        elif self.default_model:
            kwargs["model"] = self.default_model

        return client.stream(prompt, **kwargs)
