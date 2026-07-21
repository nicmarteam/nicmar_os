from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ToolParameter:
    """Definiția unui parametru acceptat de un tool."""
    name: str
    type: str  # ex: "string", "integer", "number", "boolean", "array"
    description: str
    required: bool = True
    enum: Optional[List[Any]] = None


@dataclass
class ToolDefinition:
    """Contractul intern al unui tool, independent de providerul LLM."""
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    function: Optional[Callable[..., Any]] = field(default=None, repr=False)


@dataclass
class ToolCall:
    """Solicitarea venită din partea LLM-ului de a rula un anumit tool."""
    tool_call_id: str
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """Rezultatul returnat după execuția locală a unui tool."""
    tool_call_id: str
    name: str
    output: Any
    is_error: bool = False
