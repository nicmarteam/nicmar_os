from src.runtime.session.manager import RuntimeSessionManager
from src.runtime.stream.models import RuntimeExecution
from src.runtime.inspector.models import MetricsInfo
import uuid

class RuntimeSessionOrchestrator:
    def __init__(self, session_manager: RuntimeSessionManager):
        self.session_manager = session_manager

    def execute_in_session(self, user_id: str, prompt: str, provider: str = "gemini", model: str = "gemini-2.5-flash") -> tuple:
        session = self.session_manager.get_active_session(user_id)
        if not session:
            session = self.session_manager.create_session(user_id=user_id, metadata={"source": "runtime_orchestrator"})

        trace_id = f"exec-{uuid.uuid4().hex[:8]}"
        execution = RuntimeExecution(
            trace_id=trace_id,
            provider=provider,
            model=model,
            prompt=prompt,
            events=[],
            metrics=MetricsInfo(elapsed_ms=320.0, input_tokens=15, output_tokens=45)
        )

        self.session_manager.append_execution(session.session_id, execution)
        return session, execution
