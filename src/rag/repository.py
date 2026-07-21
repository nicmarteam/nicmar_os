from abc import ABC, abstractmethod
from typing import List, Optional
from src.rag.models import Document, DocumentChunk, RetrievedChunk, SearchResult

class KnowledgeRepository(ABC):
    @abstractmethod
    def add_document(self, document: Document, chunks: List[DocumentChunk]) -> None:
        """Adaugă un document și chunk-urile sale în baza de cunoștințe."""
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5, min_score: float = 0.0) -> SearchResult:
        """Caută cele mai relevante chunk-uri pe baza embedding-ului query-ului."""
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Șterge un document și toate chunk-urile asociate după ID."""
        pass
