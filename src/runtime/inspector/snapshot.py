from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.runtime.inspector.models import (
    RequestInfo, ProviderInfo, PromptInfo, ContextInfo,
    MemoryLookupInfo, RAGRetrievalInfo, MetricsInfo, TimelineEventInfo
)

@dataclass
class InspectorSnapshot:
    request: RequestInfo
    provider_info: ProviderInfo
    prompt: PromptInfo
    context: ContextInfo
    memory: MemoryLookupInfo
    rag: RAGRetrievalInfo
    tools: List[Any] = field(default_factory=list)
    events: List[TimelineEventInfo] = field(default_factory=list)
    metrics: MetricsInfo = field(default_factory=MetricsInfo)
    response_text: str = ""
    status: str = "IDLE"
    error_message: Optional[str] = None

    def render_panel(self) -> str:
        """Randează panoul complet de Context Intelligence în Inspector."""
        lines = []
        lines.append("=" * 60)
        lines.append(" 🔍 INSPECTOR: CONTEXT INTELLIGENCE PANEL")
        lines.append("=" * 60)
        
        # 1. Execution / Request Context
        lines.append("\n[1] EXECUTION CONTEXT")
        lines.append(f"   Trace ID      : {self.request.trace_id}")
        lines.append(f"   Provider      : {self.provider_info.provider}")
        lines.append(f"   Model         : {self.provider_info.model}")
        lines.append(f"   Temperature   : {self.request.temperature}")
        lines.append(f"   System Prompt : '{self.request.system_prompt}'")
        lines.append(f"   Resolved Prom.: '{self.request.resolved_prompt}'")
        
        # 2. Memory Trace
        lines.append("\n[2] MEMORY TRACE")
        lines.append(f"   Enabled       : {'YES' if self.memory.enabled else 'NO'}")
        if self.memory.enabled:
            lines.append(f"   Strategy      : {self.memory.selection_strategy}")
            lines.append(f"   Reason        : {self.memory.selection_reason}")
            lines.append(f"   Loaded        : {len(self.memory.memories_loaded)} memories")
            for mem in self.memory.memories_loaded:
                lines.append(f"     • {mem}")
            lines.append(f"   Memory IDs    : {', '.join(self.memory.memory_ids)}")
        
        # 3. RAG Trace
        lines.append("\n[3] RAG TRACE")
        lines.append(f"   Enabled       : {'YES' if self.rag.enabled else 'NO'}")
        if self.rag.enabled:
            lines.append(f"   Query         : '{self.rag.query}'")
            lines.append(f"   Strategy      : {self.rag.retrieval_strategy}")
            lines.append(f"   Total Chunks  : {self.rag.total_chunks}")
            lines.append(f"   Selected IDs  : {', '.join(self.rag.selected_chunk_ids)}")
            lines.append("   Retrieved Chunks:")
            for i, chunk in enumerate(self.rag.retrieved_chunks, 1):
                lines.append(f"     {i}. [{chunk.source}] (Score: {chunk.score}) -> '{chunk.content_preview}'")

        # 4. Metrics & Status
        lines.append("\n[4] METRICS & STATUS")
        lines.append(f"   Status        : {self.status}")
        lines.append(f"   Elapsed Time  : {round(self.metrics.elapsed_ms, 2)} ms")
        lines.append(f"   Tokens / Sec  : {self.metrics.tokens_per_second}")
        lines.append(f"   Estimated Cost: ${self.metrics.estimated_cost}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
