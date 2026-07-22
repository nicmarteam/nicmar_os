from dataclasses import dataclass, field
from typing import List, Optional
from src.runtime.inspector.models import (
    RequestInfo, ProviderInfo, PromptInfo, ContextInfo,
    MemoryLookupInfo, RAGRetrievalInfo, ToolExecutionInfo,
    TimelineEventInfo, MetricsInfo
)

@dataclass
class InspectorSnapshot:
    request: RequestInfo
    provider_info: ProviderInfo
    prompt: PromptInfo
    context: ContextInfo
    memory: MemoryLookupInfo
    rag: RAGRetrievalInfo
    tools: List[ToolExecutionInfo] = field(default_factory=list)
    events: List[TimelineEventInfo] = field(default_factory=list)
    metrics: MetricsInfo = field(default_factory=None)
    response_text: str = ""
    status: str = "UNKNOWN"
    error_message: Optional[str] = None
