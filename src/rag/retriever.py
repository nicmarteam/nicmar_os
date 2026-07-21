from typing import List
from src.rag.models import SearchResult
from src.rag.repository import KnowledgeRepository
from src.rag.embeddings.base import BaseEmbeddingProvider

class KnowledgeRetriever:
    def __init__(self, repository: KnowledgeRepository, embedding_provider: BaseEmbeddingProvider):
        self.repository = repository
        self.embedding_provider = embedding_provider

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.0) -> SearchResult:
        # 1. Generăm embedding-ul pentru query
        query_embedding = self.embedding_provider.embed_text(query)
        
        # 2. Căutăm în repository
        search_result = self.repository.search(
            query_embedding=query_embedding,
            top_k=top_k,
            min_score=min_score
        )
        search_result.query = query
        return search_result
