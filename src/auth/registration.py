"""
Auth Registration v1 — src/auth/registration.py.

Sursă: 30-auth-register-contract.md.

`/login` rămâne complet neschimbat — acest fișier e nou, izolat, nu
modifică `service.py`/`security.py`/`dependencies.py`.
"""

from dataclasses import dataclass
from uuid import UUID

from src.auth.security import hash_password
from src.data.db import get_connection


@dataclass(frozen=True)
class RegisteredUser:
    """Utilizatorul nou creat, așa cum e citit din `RETURNING`.

    Attributes:
        id: Identificatorul generat de PostgreSQL.
        email: Emailul, exact cum a fost primit — fără normalizare
            (contract secțiunea 1, decizia 2).
        full_name: Numele complet.
        role: Rolul aplicat de `DEFAULT 'LEADER'` al coloanei — nu
            setat explicit de acest cod (contract secțiunea 1B).
    """

    id: UUID
    email: str
    full_name: str
    role: str


def register_user(email: str, password: str, full_name: str) -> RegisteredUser:
    """Creează un utilizator nou, cu parolă hash-uită bcrypt.

    `role` NU e inclus în coloanele `INSERT` — PostgreSQL aplică
    `DEFAULT 'LEADER'` (contract secțiunea 1B, garanție de securitate:
    clientul nu poate controla rolul, pentru că nu există canal prin
    care să-l transmită).

    `password_hash` e generat aici, obligatoriu — parola în clar nu
    e persistată niciodată.

    Args:
        email: Emailul, folosit exact cum e primit (fără normalizare).
        password: Parola în clar — deja validată (8-72 bytes UTF-8) de
            `RegisterRequest` înainte să ajungă aici.
        full_name: Numele complet, obligatoriu (schema `users.full_name
            NOT NULL`, fără `DEFAULT`).

    Returns:
        `RegisteredUser` cu valorile citite din `RETURNING`.

    Raises:
        psycopg.errors.UniqueViolation: emailul există deja — propagă
            neprinsă. Query-ul rulează în interiorul blocului
            `get_connection()`, care face `rollback()` automat pe orice
            excepție (contract secțiunea 1A) — nu se adaugă
            try/except suplimentar aici.
    """
    password_hash = hash_password(password)

    query = """
        INSERT INTO users (email, full_name, password_hash)
        VALUES (%s, %s, %s)
        RETURNING id, email, full_name, role
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (email, full_name, password_hash))
            row = cur.fetchone()

    return RegisteredUser(id=row[0], email=row[1], full_name=row[2], role=row[3])
