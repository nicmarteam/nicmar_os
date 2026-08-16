"""
Teste pentru Auth — /auth/login și get_current_user().

Sarite (skip) daca DATABASE_URL nu e setat. JWT_SECRET_KEY setat
explicit aici, doar pentru teste — nu e valoare implicita de
productie (get_jwt_secret() tot esueaza fara el, in afara testelor).
"""

import os
from uuid import uuid4

import bcrypt
import jwt as pyjwt
import datetime
import pytest
from fastapi.testclient import TestClient

from src.data.db import get_connection

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-doar-pentru-teste-minim-32-bytes-lungime")

pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="Necesita DATABASE_URL (PostgreSQL real) — sarit fara DB configurat.",
)


@pytest.fixture(scope="module")
def client():
    from src.api.main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def reset_login_rate_limiter():
    from src.auth.rate_limit import login_rate_limiter
    login_rate_limiter.reset()
    yield
    login_rate_limiter.reset()


def _create_user_with_password(prefix: str, password: str) -> tuple[str, str]:
    """Returnează (user_id, email)."""
    email = f"{prefix}-{uuid4()}@nicmar.local"
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, full_name, role, password_hash) "
                "VALUES (%s, %s, 'LEADER', %s) RETURNING id",
                (email, f"Test {prefix}", password_hash),
            )
            user_id = str(cur.fetchone()[0])
    return user_id, email


def _create_user_without_password(prefix: str) -> str:
    """Utilizator fără password_hash (NULL) — la fel ca cei din seed/alte teste."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, full_name, role) VALUES (%s, %s, 'LEADER') RETURNING id",
                (f"{prefix}-{uuid4()}@nicmar.local", f"Test {prefix}"),
            )
            return str(cur.fetchone()[0])


def test_login_correct_returns_200_with_token(client):
    _, email = _create_user_with_password("login-ok", "parola_buna")
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "parola_buna"})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    _, email = _create_user_with_password("login-wrong-pw", "parola_corecta")
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "parola_gresita"})
    assert response.status_code == 401


def test_login_nonexistent_email_returns_401(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": f"nu-exista-{uuid4()}@nicmar.local", "password": "orice"},
    )
    assert response.status_code == 401


def test_login_user_without_password_returns_401(client):
    user_id = _create_user_without_password("no-password")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT email FROM users WHERE id = %s", (user_id,))
            email = cur.fetchone()[0]

    response = client.post("/api/v1/auth/login", json={"email": email, "password": "orice_parola"})
    assert response.status_code == 401


def test_valid_token_returns_correct_user(client):
    user_id, email = _create_user_with_password("valid-token", "parola123")
    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "parola123"})
    token = login_resp.json()["access_token"]

    from src.auth.security import decode_access_token
    decoded_user_id = str(decode_access_token(token))
    assert decoded_user_id == user_id


def test_expired_token_returns_401():
    user_id = str(uuid4())
    expired_payload = {
        "sub": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1),
    }
    expired_token = pyjwt.encode(expired_payload, os.environ["JWT_SECRET_KEY"], algorithm="HS256")

    from src.auth.dependencies import get_current_user
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=creds)
    assert exc_info.value.status_code == 401


def test_tampered_token_returns_401(client):
    user_id, email = _create_user_with_password("tampered", "parola123")
    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "parola123"})
    token = login_resp.json()["access_token"]
    tampered_token = token[:-5] + "XXXXX"

    from src.auth.dependencies import get_current_user
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=tampered_token)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=creds)
    assert exc_info.value.status_code == 401


def test_missing_authorization_returns_401():
    from src.auth.dependencies import get_current_user
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=None)
    assert exc_info.value.status_code == 401


def test_malformed_signed_token_returns_401():
    """Semnătură validă, dar sub invalid — nu trebuie să ajungă la 500."""
    malformed_token = pyjwt.encode(
        {"sub": "not-a-uuid", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)},
        os.environ["JWT_SECRET_KEY"],
        algorithm="HS256",
    )

    from src.auth.dependencies import get_current_user
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=malformed_token)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=creds)
    assert exc_info.value.status_code == 401


def test_login_rate_limit_returns_429_after_five_failed_attempts(client):
    email = f"rate-limit-{uuid4()}@nicmar.local"

    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "gresita"},
        )
        assert response.status_code == 401

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "gresita"},
    )
    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_successful_login_resets_rate_limit(client):
    _, email = _create_user_with_password("rate-reset", "parola_corecta")

    for _ in range(4):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "gresita"},
        )
        assert response.status_code == 401

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "parola_corecta"},
    )
    assert response.status_code == 200

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "gresita"},
    )
    assert response.status_code == 401
