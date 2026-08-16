"""
get_current_user() — dependency FastAPI care extrage identitatea reală
din header-ul Authorization, nu din request body.

Lanț: Authorization: Bearer <JWT> -> decode -> user_id -> SELECT users
-> CurrentUser.

Acesta e mecanismul care închide problema de impersonare: orice
owner_id trimis manual în request va fi IGNORAT de endpoint-urile
care folosesc get_current_user (integrare separată, nu în acest
fișier).
"""

from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.security import decode_access_token
from src.data.db import get_connection

_security_scheme = HTTPBearer(auto_error=False)


class CurrentUser:
    """Utilizatorul autentificat curent, citit din PostgreSQL după validarea JWT."""

    def __init__(self, id: UUID, email: str, full_name: str):
        self.id = id
        self.email = email
        self.full_name = full_name


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security_scheme),
) -> CurrentUser:
    """
    Extrage și validează identitatea din header-ul Authorization.

    401 pentru: header lipsă, token invalid (semnătură greșită sau
    malformat), token expirat, sau user_id din token care nu mai
    există în DB (cont șters după emiterea token-ului).
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header.")

    token = credentials.credentials

    try:
        user_id = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirat.")
    except jwt.InvalidTokenError:
        # Prinde InvalidSignatureError, DecodeError etc. — toate subclase
        raise HTTPException(status_code=401, detail="Token invalid.")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, full_name FROM users WHERE id = %s", (user_id,)
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=401, detail="Utilizator inexistent.")

    return CurrentUser(id=row[0], email=row[1], full_name=row[2])
