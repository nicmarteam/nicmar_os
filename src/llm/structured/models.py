from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Type
from pydantic import BaseModel


@dataclass
class StructuredResponse:
    """Wrapper pentru răspunsul structurat și tipizat returnat de LLM."""
    parsed_data: BaseModel
    raw_content: str
    model: str
    provider: str
    raw_response: Any = None
