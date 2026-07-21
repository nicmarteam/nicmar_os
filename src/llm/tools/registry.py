from __future__ import annotations

from typing import Dict, List, Optional
from src.llm.tools.models import ToolDefinition


class ToolRegistry:
    """Registru centralizat pentru gestionarea tool-urilor disponibile în sistem."""

    _registry: Dict[str, ToolDefinition] = {}

    @classmethod
    def register(cls, definition: ToolDefinition) -> None:
        """Înregistrează un tool nou în sistem."""
        if not definition.name:
            raise ValueError("Tool-ul trebuie să aibă un nume valid.")
        cls._registry[definition.name] = definition

    @classmethod
    def get(cls, name: str) -> ToolDefinition:
        """Returnează definiția unui tool după nume sau aruncă eroare dacă nu există."""
        if name not in cls._registry:
            raise KeyError(f"Tool-ul '{name}' nu este înregistrat în ToolRegistry.")
        return cls._registry[name]

    @classmethod
    def list_tools(cls) -> List[ToolDefinition]:
        """Returnează lista tuturor tool-urilor înregistrate."""
        return list(cls._registry.values())

    @classmethod
    def clear(cls) -> None:
        """Șterge toate tool-urile înregistrate (util pentru teste)."""
        cls._registry.clear()
