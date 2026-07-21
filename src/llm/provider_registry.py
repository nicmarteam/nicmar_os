from __future__ import annotations

from typing import Type, Any

class ProviderRegistry:
    """Registry centralizat pentru înregistrarea și obținerea claselor de clienți LLM."""
    
    _registry: dict[str, Type[Any]] = {}

    @classmethod
    def register(cls, name: str, client_class: Type[Any]) -> None:
        cls._registry[name.lower()] = client_class

    @classmethod
    def get(cls, name: str) -> Type[Any]:
        normalized_name = name.lower()
        if normalized_name not in cls._registry:
            raise ValueError(f"Providerul LLM '{name}' nu este înregistrat în ProviderRegistry.")
        return cls._registry[normalized_name]
