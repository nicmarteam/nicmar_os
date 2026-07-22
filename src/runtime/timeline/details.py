from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class EventDetailSection:
    title: str
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TimelineEventDetail:
    event_id: str
    event_type: str
    title: str
    summary_sections: List[EventDetailSection] = field(default_factory=list)

class EventDetailsBuilder:
    @staticmethod
    def build_for_event(event_id: str, event_type: str, title: str, metadata: Dict[str, Any]) -> TimelineEventDetail:
        sections = []

        if event_type == "memory_loaded":
            sections.append(EventDetailSection(
                title="Memory Retrieval Configuration",
                data={
                    "Strategy": metadata.get("strategy", "semantic"),
                    "Loaded Memories": metadata.get("loaded", 0),
                    "IDs": metadata.get("ids", ["mem_001", "mem_004", "mem_011"]),
                    "Selection Reason": "Top semantic similarity match against prompt context"
                }
            ))
        elif event_type == "rag_search":
            sections.append(EventDetailSection(
                title="RAG Knowledge Base Search",
                data={
                    "Query": metadata.get("query", "general context search"),
                    "Chunks Retrieved": metadata.get("chunks", 0),
                    "Sources": metadata.get("sources", ["guide.pdf", "faq.md", "testimonials.md"]),
                    "Embedding Engine": metadata.get("embedding", "text-embedding-004")
                }
            ))
        elif event_type == "provider_request":
            sections.append(EventDetailSection(
                title="LLM Provider Configuration",
                data={
                    "Provider": metadata.get("provider", "gemini"),
                    "Model": metadata.get("model", "gemini-2.5-flash"),
                    "Temperature": metadata.get("temperature", 0.7),
                    "Max Tokens": metadata.get("max_tokens", 2048)
                }
            ))
        elif event_type == "first_token":
            sections.append(EventDetailSection(
                title="Stream Latency Metrics",
                data={
                    "Time To First Token (TTFT)": f"{metadata.get('ttft_ms', 0.0)} ms",
                    "Status": "Stream channel opened successfully"
                }
            ))
        else:
            if metadata:
                sections.append(EventDetailSection(
                    title="Event Metadata",
                    data=metadata
                ))

        return TimelineEventDetail(
            event_id=event_id,
            event_type=event_type,
            title=title,
            summary_sections=sections
        )
