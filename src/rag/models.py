from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Document:
    document_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "manual"

@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SearchResult:
    query: str
    chunks: List[RetrievedChunk] = field(default_factory=list)
    total_found: int = 0
