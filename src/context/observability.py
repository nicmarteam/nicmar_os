import logging
from src.context.models import ContextDiagnostics, ResolvedContext

logger = logging.getLogger("NicMarOS.ContextObservability")

class ContextObservability:
    @staticmethod
    def log_diagnostics(diagnostics: ContextDiagnostics) -> None:
        """
        Înregistrează detaliile de diagnostic pentru a fi utilizate în viitorul dashboard de monitorizare.
        """
        logger.info(
            f"Context Diagnostics -> Available: {diagnostics.total_tokens_available} | "
            f"Used: {diagnostics.total_tokens_used} | Dropped: {diagnostics.tokens_dropped} | "
            f"Providers Used: {diagnostics.providers_used} | Providers Dropped: {diagnostics.providers_dropped} | "
            f"Estimated Cost: ${diagnostics.estimated_cost:.6f} | Latency: {diagnostics.latency_ms}ms"
        )

    @staticmethod
    def format_summary(resolved: ResolvedContext) -> str:
        d = resolved.diagnostics
        return (
            f"[Context Summary] Tokens: {d.total_tokens_used}/{d.total_tokens_available} | "
            f"Cost: ${d.estimated_cost:.6f} | Latency: {d.latency_ms}ms | "
            f"Providers: {', '.join(d.providers_used)}"
        )
