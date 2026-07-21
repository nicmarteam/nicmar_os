from typing import List
import uuid
from src.rag.models import Document, DocumentChunk

class DocumentChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        content = document.content
        chunks = []
        
        if len(content) <= self.chunk_size:
            chunk_id = f"{document.document_id}-chunk-0"
            return [
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document.document_id,
                    content=content,
                    metadata=document.metadata.copy()
                )
            ]

        start = 0
        counter = 0
        while start < len(content):
            end = start + self.chunk_size
            chunk_text = content[start:end]
            chunk_id = f"{document.document_id}-chunk-{counter}"
            
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document.document_id,
                    content=chunk_text,
                    metadata=document.metadata.copy()
                )
            )
            
            start += self.chunk_size - self.chunk_overlap
            counter += 1

        return chunks
