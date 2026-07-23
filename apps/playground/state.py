from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class PlaygroundRequest:
    provider: str
    model: str
    prompt: str
    streaming: bool = False
    temperature: float = 0.7
    max_tokens: int = 1000
    enable_memory: bool = False
    enable_rag: bool = False
    enable_tools: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
