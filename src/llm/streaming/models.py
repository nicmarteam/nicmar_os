from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class LLMStreamChunk:
    """
    Reprezintă o unitate unificată de streaming emisă de orice provider LLM.
    """

    delta: str
    provider: str
    model: str
    sequence: int

    finished: bool = False
    finish_reason: str | None = None

    raw: Any | None = field(default=None, repr=False)
