import time
from typing import Optional, Dict, Any
from src.runtime.session.models import RuntimeSession
from src.runtime.session.builder import SessionBuilder

class SessionError(Exception):
    pass

class SessionClosedError(SessionError):
    pass

class SessionNotFoundError(SessionError):
    pass

class RuntimeSessionManager:
    def __init__(self):
        self._sessions: Dict[str, RuntimeSession] = {}

    def create_session(self, user_id: str = "default_user", metadata: Optional[Dict[str, Any]] = None) -> RuntimeSession:
        session = SessionBuilder.create_session(user_id=user_id, metadata=metadata)
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> RuntimeSession:
        if session_id not in self._sessions:
            raise SessionNotFoundError(f"Sesiunea cu ID-ul {session_id} nu a fost găsită.")
        return self._sessions[session_id]

    def get_active_session(self, user_id: str) -> Optional[RuntimeSession]:
        """Caută și returnează prima sesiune activă pentru un anumit utilizator."""
        for session in self._sessions.values():
            if session.user_id == user_id and session.status == "active":
                return session
        return None

    def append_execution(self, session_id: str, execution: Any) -> None:
        session = self.get_session(session_id)
        
        if session.status != "active":
            raise SessionClosedError(f"Nu se poate adăuga execuția: sesiunea {session_id} este închisă.")
        
        session.add_execution(execution)
        session.metadata["last_activity"] = time.time()
        session.metadata["execution_count"] = len(session.executions)

    def close_session(self, session_id: str) -> None:
        session = self.get_session(session_id)
        session.close()
        session.metadata["closed_at"] = time.time()
