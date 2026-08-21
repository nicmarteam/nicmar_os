"""
ContactEngine (WRITE) — Decizia 31, `31-contact-create-contract.md`.

Separat, intenționat, de `ContactAgent` (`src/agents/contact/`), care
rămâne strict READ-ONLY, conform `20-contact-agent-contract.md`. Acel
contract anticipase explicit acest moment: "decizia de a introduce un
ContactEngine rămâne FOLLOW-UP explicit, nu implicit."
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from psycopg.types.json import Json

from src.data.db import get_connection


class InvalidRelationshipValueError(Exception):
    """Valoare în afara enum-urilor permise pentru câmpurile de relație (Decizia 47)."""


@dataclass(frozen=True)
class Contact:
    """Reprezentarea unui contact, așa cum e citit din `contacts`.

    Attributes:
        id: Identificatorul generat de PostgreSQL.
        owner_id: Liderul care deține contactul.
        full_name: Numele complet — obligatoriu.
        phone: Opțional.
        email: Opțional — fără `UNIQUE`, spre deosebire de `users.email`.
        status: Starea curentă — `'NEW'` la creare (contract secțiunea 1).
        source: Opțional (ex. `'facebook'`, `'referral'`).
        metadata: JSON liber, `{}` implicit dacă nu e transmis.
    """

    id: UUID
    owner_id: UUID
    full_name: str
    phone: Optional[str]
    email: Optional[str]
    status: str
    source: Optional[str]
    metadata: dict


class ContactEngine:
    """Proprietarul scrierii pentru `contacts` — `ContactAgent` rămâne read-only, separat."""

    def create_contact(
        self,
        owner_id: UUID,
        full_name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Contact:
        """Creează un contact nou, cu `status='NEW'` hardcodat, server-side.

        `status` NU e parametru — nu poate fi controlat de apelant.
        Precedent identic: `ConversationEngine.get_or_create_conversation()`
        hardcodează `status='INITIATED'` în `INSERT`.

        Args:
            owner_id: Liderul autentificat — din `CurrentUser.id` (JWT).
            full_name: Numele complet — obligatoriu (schema `NOT NULL`).
            phone: Opțional, fără validare de format (niciuna nu există
                azi, nicăieri în proiect).
            email: Opțional, fără validare de format, fără normalizare —
                consecvent cu decizia de a nu introduce reguli noi.
            source: Opțional.
            metadata: Opțional — `None` devine `{}` înainte de `INSERT`.

        Returns:
            `Contact` complet, construit din valorile `RETURNING`.
        """
        query = """
            INSERT INTO contacts (owner_id, full_name, phone, email, status, source, metadata)
            VALUES (%s, %s, %s, %s, 'NEW', %s, %s)
            RETURNING id, owner_id, full_name, phone, email, status, source, metadata
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id, full_name, phone, email, source, Json(metadata or {})))
                row = cur.fetchone()

        contact = Contact(
            id=row[0], owner_id=row[1], full_name=row[2], phone=row[3],
            email=row[4], status=row[5], source=row[6], metadata=row[7],
        )
        self._emit_event("ContactCreated", contact.id, {"owner_id": str(owner_id)})
        return contact

    def _emit_event(self, event_name: str, target_object_id: UUID, payload: dict) -> None:
        """Scrie evenimentul în tabelul generic `events` (pattern identic cu celelalte 4 engine-uri)."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO events (event_name, target_object, target_object_id, payload) "
                    "VALUES (%s, %s, %s, %s)",
                    (event_name, "contact", target_object_id, Json(payload)),
                )
