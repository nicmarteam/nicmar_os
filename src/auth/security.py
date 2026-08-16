"""
Utilitare de securitate — hash parole (bcrypt, direct, fără passlib —
incompatibil confirmat) + JWT (PyJWT).

Sursă: decizia de azi — bcrypt==5.0.0, pyjwt==2.13.0, ambele testate
end-to-end înainte de scrierea acestui fișier.
"""

import datetime
import os
from uuid import UUID

import bcrypt
import jwt

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 1  # Decizie MVP — nu specificat de Nic, valoare rezonabilă implicită


def get_jwt_secret() -> str:
    """
    Citește JWT_SECRET_KEY din mediu — la fel ca DATABASE_URL în db.py,
    fără valoare implicită hardcodată. Eșuează explicit dacă lipsește.
    """
    secret = os.environ.get("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError(
            "JWT_SECRET_KEY nu este setat. "
            "Exemplu: export JWT_SECRET_KEY='o-cheie-lunga-si-secreta'"
        )
    return secret


def hash_password(password: str) -> str:
    """Hash bcrypt, direct — fără wrapper passlib (incompatibil confirmat)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verifică o parolă față de un hash bcrypt existent."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: UUID) -> str:
    """Generează un JWT cu sub=user_id și exp=acum+1h."""
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> UUID:
    """
    Decodează un JWT, verifică semnătura și expirarea.

    Ridică jwt.ExpiredSignatureError sau jwt.InvalidTokenError (sau
    subclase, ex. InvalidSignatureError) — nu le capturăm aici,
    apelantul (get_current_user) decide cum le mapează la HTTP.
    """
    payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
    return UUID(payload["sub"])
