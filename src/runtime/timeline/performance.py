from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class PerformanceMetrics:
    ttft_ms: float = 0.0
    provider_latency_ms: float = 0.0
    stream_duration_ms: float = 0.0
    execution_duration_ms: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_per_second: float = 0.0
    estimated_cost: float = 0.0
    custom_durations: Dict[str, float] = field(default_factory=dict)

    @staticmethod
    def classify_metric(name: str, value: float) -> str:
        """Clasifică automat performanța după praguri standard DevTools."""
        if name == "ttft_ms":
            if value < 500: return "🟢 Excellent"
            if value <= 1000: return "🟡 Good"
            if value <= 2000: return "🟠 Slow"
            return "🔴 Critical"
        elif name == "tokens_per_second":
            if value > 50: return "🟢 Excellent"
            if value >= 25: return "🟡 Good"
            if value >= 10: return "🟠 Slow"
            return "🔴 Critical"
        elif name == "total_ms":
            if value < 1000: return "🟢 Excellent"
            if value <= 3000: return "🟡 Good"
            if value <= 6000: return "🟠 Slow"
            return "🔴 Critical"
        return "🟢 Normal"
