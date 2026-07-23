from typing import Dict, List, Optional
from src.runtime.inspector.snapshot import InspectorSnapshot

class InspectorRepository:
    def __init__(self):
        self._storage: Dict[str, InspectorSnapshot] = {}
        self._history_order: List[str] = []

    def save(self, snapshot: InspectorSnapshot):
        trace_id = snapshot.request.trace_id
        self._storage[trace_id] = snapshot
        if trace_id not in self._history_order:
            self._history_order.append(trace_id)

    def get_by_trace_id(self, trace_id: str) -> Optional[InspectorSnapshot]:
        return self._storage.get(trace_id)

    def get_latest(self) -> Optional[InspectorSnapshot]:
        if not self._history_order:
            return None
        return self._storage.get(self._history_order[-1])

    def get_recent(self, limit: int = 100) -> List[InspectorSnapshot]:
        recent_ids = self._history_order[-limit:]
        return [self._storage[tid] for tid in reversed(recent_ids) if tid in self._storage]

    def get_by_provider(self, provider: str) -> List[InspectorSnapshot]:
        return [s for s in self._storage.values() if s.provider_info.provider == provider]
