"""
Logica de autentificare — conectează verificarea hash-ului cu
interogarea reală în PostgreSQL.

Regulă de securitate (identică cu MissionAccessDeniedError etc.):
email inexistent, parolă greșită, și password_hash=NULL produc
EXACT același mesaj — previne enumerarea de conturi valide.
"""

from src.auth.security import verify_password, create_access_token
from src.data.db import get_connection


class InvalidCredentialsError(Exception):
    """
    Ridicată pentru orice combinație de login invalidă: email
    inexistent, parolă greșită, sau password_hash=NULL (utilizator
    creat prin seed/teste, fără autentificare reală configurată).
    Mesaj identic în toate 3 cazuri.
    """


def authenticate(email: str, password: str) -> str:
    """
    Verifică email+parolă față de PostgreSQL, returnează un access
    token JWT dacă e valid. Ridică InvalidCredentialsError altfel.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, password_hash FROM users WHERE email = %s", (email,)
            )
            row = cur.fetchone()

    if row is None:
        raise InvalidCredentialsError("Email sau parolă incorectă.")

    user_id, password_hash = row

    if password_hash is None:
        raise InvalidCredentialsError("Email sau parolă incorectă.")

    if not verify_password(password, password_hash):
        raise InvalidCredentialsError("Email sau parolă incorectă.")

    return create_access_token(user_id)
