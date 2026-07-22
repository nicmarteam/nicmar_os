import uuid
from typing import Dict, Any, Optional
from src.runtime.session.models import RuntimeSession

class SessionBuilder:
    @staticmethod
    def create_session(user_id: str = "default_user", metadata: Optional[Dict[str, Any]] = None) -> RuntimeSession:
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        return RuntimeSession(
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {}
        )
