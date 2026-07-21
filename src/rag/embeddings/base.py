from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generează un vector embedding pentru un text dat."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generează vectori embedding pentru o listă de texte."""
        pass

class InMemoryEmbeddingProvider(BaseEmbeddingProvider):
    """Provider simplu pentru testare locală care generează vectori deterministici/pseudo-randomici."""
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        # Generare pseudo-randomică bazată pe lungimea textului și caractere pentru consistență în teste
        import random
        random.seed(hash(text))
        return [random.uniform(-1.0, 1.0) for _ in range(self.dimension)]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]
