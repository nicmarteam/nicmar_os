from typing import Dict, Any
from src.context.models import LLMContext
from src.context.enrichers import ContextEnricher
from src.rag.retriever import KnowledgeRetriever

class RAGEnricher(ContextEnricher):
    def __init__(self, retriever: KnowledgeRetriever, top_k: int = 3):
        self.retriever = retriever
        self.top_k = top_k

    def enrich(self, context: LLMContext, params: Dict[str, Any]) -> LLMContext:
        # Luăm cel mai recent mesaj al utilizatorului drept query pentru RAG
        user_messages = [msg for msg in context.messages if msg.role == "user"]
        if not user_messages:
            return context

        latest_query = user_messages[-1].content
        
        # Căutăm cunoștințele relevante
        search_result = self.retriever.retrieve(query=latest_query, top_k=self.top_k)

        if search_result.chunks:
            rag_context_str = "\n\n".join([f"[Sursă RAG - Doc {chunk.document_id}]:\n{chunk.content}" for chunk in search_result.chunks])
            context.metadata["rag_knowledge"] = rag_context_str
            
            # Opțional, putem injecta cunoștințele RAG ca un mesaj de sistem suplimentar sau în metadate
            from src.context.models import LLMMessage
            rag_system_msg = LLMMessage(
                role="system",
                content=f"Informații relevante din baza de cunoștințe (RAG):\n{rag_context_str}"
            )
            # Inserăm înainte de ultimul mesaj sau după promptul de sistem
            context.messages.insert(1, rag_system_msg)

        return context
