"""
Rate limiting minimal pentru login.

MVP: limita este per IP, in-memory, si se aplica doar incercarilor
nereusite. La depasirea limitei, login-ul raspunde cu HTTP 429.
Pentru un deployment multi-instance, acest mecanism va trebui mutat
intr-un store partajat (de ex. Redis).
"""

import time
from collections import defaultdict, deque
from threading import Lock


class LoginRateLimiter:
    def __init__(self, max_failures: int = 5, window_seconds: int = 60):
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self._failures: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def is_limited(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            failures = self._failures[key]
            self._prune(failures, now)
            return len(failures) >= self.max_failures

    def record_failure(self, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            failures = self._failures[key]
            self._prune(failures, now)
            failures.append(now)

    def clear(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)

    def reset(self) -> None:
        """Folosit de teste pentru izolarea cazurilor."""
        with self._lock:
            self._failures.clear()

    def retry_after(self, key: str) -> int:
        now = time.monotonic()
        with self._lock:
            failures = self._failures[key]
            self._prune(failures, now)
            if not failures:
                return self.window_seconds
            return max(1, int(self.window_seconds - (now - failures[0])))

    def _prune(self, failures: deque[float], now: float) -> None:
        cutoff = now - self.window_seconds
        while failures and failures[0] <= cutoff:
            failures.popleft()


login_rate_limiter = LoginRateLimiter(max_failures=5, window_seconds=60)
