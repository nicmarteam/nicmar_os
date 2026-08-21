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


# Decizia 47 (Competența 18) — enum-uri validate la nivel de aplicație,
# ÎNAINTE de DB (tipar identic InvalidDiagnosticTypeError de la Partner).
# CHECK-ul din schemă rămâne plasă de siguranță, nu singura barieră.
_VALID_RELATIONSHIP_CATEGORIES = {
    "FAMILIE", "PRIETENI", "COLEGI", "VECINI",
    "FOSTI_COLEGI", "CUNOSTINTE", "ALTA",
}
_VALID_RELATIONSHIP_LEVELS = {
    "FOARTE_APROPIATA", "BUNA", "OCAZIONALA", "DE_RELUAT",
}
_VALID_LAST_CONTACT_APPROX = {
    "ASTAZI", "SAPTAMANA_ACEASTA", "LUNA_ACEASTA",
    "MAI_DEMULT", "NU_IMI_AMINTESC",
}
_VALID_PERCEIVED_INTEREST = {
    "FOARTE_DESCHISA", "PROBABIL", "NU_STIU_INCA",
}


def _validate_relationship_value(value, allowed, field_name: str) -> None:
    """Ridică `InvalidRelationshipValueError` dacă valoarea nu e permisă.

    `None` e întotdeauna acceptat — toate cele 5 câmpuri sunt opționale
    (contract 47, §4: coloane nullable, zero breaking change).
    """
    if value is not None and value not in allowed:
        raise InvalidRelationshipValueError(
            f"{field_name} invalid: {value!r}. Valori permise: {sorted(allowed)}."
        )


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
        relationship_category: Decizia 47 — categoria din care face parte
            persoana (Ecranul 2, Competența 18). `None` pentru contactele
            create fără acest context.
        relationship_level: Decizia 47 — cât de apropiată e relația azi.
        last_contact_approx: Decizia 47 — aproximare declarată de lider,
            NU timestamp (sursa cere exact "Astăzi/Săptămâna aceasta/...").
        significant_context: Decizia 47 — text liber, ultima interacțiune
            semnificativă.
        perceived_interest: Decizia 47 — cât de deschisă crede liderul că
            e persoana; percepție declarată, nu scor calculat.
    """

    id: UUID
    owner_id: UUID
    full_name: str
    phone: Optional[str]
    email: Optional[str]
    status: str
    source: Optional[str]
    metadata: dict
    relationship_category: Optional[str] = None
    relationship_level: Optional[str] = None
    last_contact_approx: Optional[str] = None
    significant_context: Optional[str] = None
    perceived_interest: Optional[str] = None


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
        relationship_category: Optional[str] = None,
        relationship_level: Optional[str] = None,
        last_contact_approx: Optional[str] = None,
        significant_context: Optional[str] = None,
        perceived_interest: Optional[str] = None,
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
            relationship_category: Decizia 47, opțional — una din
                `_VALID_RELATIONSHIP_CATEGORIES`.
            relationship_level: Decizia 47, opțional.
            last_contact_approx: Decizia 47, opțional — aproximare, nu dată.
            significant_context: Decizia 47, opțional — text liber.
            perceived_interest: Decizia 47, opțional.

        Returns:
            `Contact` complet, construit din valorile `RETURNING`.

        Raises:
            InvalidRelationshipValueError: oricare din cele 4 câmpuri de
                tip enum are o valoare în afara setului permis. Validare
                la nivel de aplicație, înainte de orice apel DB.
        """
        _validate_relationship_value(
            relationship_category, _VALID_RELATIONSHIP_CATEGORIES, "relationship_category",
        )
        _validate_relationship_value(
            relationship_level, _VALID_RELATIONSHIP_LEVELS, "relationship_level",
        )
        _validate_relationship_value(
            last_contact_approx, _VALID_LAST_CONTACT_APPROX, "last_contact_approx",
        )
        _validate_relationship_value(
            perceived_interest, _VALID_PERCEIVED_INTEREST, "perceived_interest",
        )

        query = """
            INSERT INTO contacts (
                owner_id, full_name, phone, email, status, source, metadata,
                relationship_category, relationship_level, last_contact_approx,
                significant_context, perceived_interest
            )
            VALUES (%s, %s, %s, %s, 'NEW', %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, owner_id, full_name, phone, email, status, source, metadata,
                      relationship_category, relationship_level, last_contact_approx,
                      significant_context, perceived_interest
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    owner_id, full_name, phone, email, source, Json(metadata or {}),
                    relationship_category, relationship_level, last_contact_approx,
                    significant_context, perceived_interest,
                ))
                row = cur.fetchone()

        contact = Contact(
            id=row[0], owner_id=row[1], full_name=row[2], phone=row[3],
            email=row[4], status=row[5], source=row[6], metadata=row[7],
            relationship_category=row[8], relationship_level=row[9],
            last_contact_approx=row[10], significant_context=row[11],
            perceived_interest=row[12],
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
