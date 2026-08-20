"""
OutreachEngine — Decizia 46, `46-prospectare-relationala-contract.md`.

Ce face: persistă `Outreach` (fapt imutabil, mesaj trimis de lider către
un contact, scop `REFERRAL`/`REACTIVATION`) și `Outcome` (reacția
imediată observată, cardinalitate 0..1 per Outreach, garantată de
`UNIQUE` la nivel de DB). `Outcome`-ul declanșează cel mult o predare
(*handoff*) către `Conversation`, exclusiv pentru cele 3 rezultate care
continuă cu aceeași persoană (`QUESTION_ASKED`/`HESITATION`/
`WILL_RESPOND_LATER`).

Ce NU face: nu creează `FollowUp`/`Objection` — acestea rămân acțiuni
separate ale liderului, prin fluxurile deja existente, folosind
`conversation_id` întors de `record_outcome()`. Nu creează `Contact`
nou pentru `REFERRAL_RECEIVED` — pas explicit separat, prin
`POST /api/v1/contacts` deja existent. Nu atinge Mission, Priority,
niciun KPI.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.data.db import get_connection
from src.engines.conversation.conversation_engine import ConversationEngine, Conversation

_VALID_PURPOSES = {"REFERRAL", "REACTIVATION"}
_VALID_TONES = {"CALDA", "RELAXATA", "DIRECTA"}
_VALID_OUTCOMES = {
    "QUESTION_ASKED", "HESITATION", "WILL_RESPOND_LATER",
    "REFERRAL_RECEIVED", "POSITIVE_RESPONSE",
}
# Contract 46, §3.3 — doar aceste 3 outcome-uri continua cu ACEEASI
# persoana (target-ul original), deci doar ele declanseaza handoff
# automat catre Conversation. REFERRAL_RECEIVED (persoana noua, inca
# fara Contact) si POSITIVE_RESPONSE (flux 07, neconstruit) raman
# manuale.
_OUTCOMES_WITH_AUTO_HANDOFF = {"QUESTION_ASKED", "HESITATION", "WILL_RESPOND_LATER"}


class OutreachAccessDeniedError(Exception):
    """Contactul sau outreach-ul nu există, sau nu aparține owner-ului dat."""


class InvalidPurposeError(Exception):
    """`purpose` în afara valorilor permise (Contract 46, §3.1)."""


class InvalidToneError(Exception):
    """`tone_used` în afara valorilor permise (Contract 46, §3.1)."""


class InvalidOutcomeError(Exception):
    """`outcome` în afara valorilor permise (Contract 46, §3.2)."""


class OutcomeAlreadyRecordedError(Exception):
    """Acest Outreach are deja un Outcome — cardinalitate 0..1 (Contract 46, §3.2)."""


@dataclass
class OutreachAttempt:
    id: UUID
    owner_id: UUID
    contact_id: UUID
    purpose: str
    message_text: str
    tone_used: str


@dataclass
class OutreachOutcomeResult:
    id: UUID
    outreach_id: UUID
    outcome: str
    conversation_id: Optional[UUID]


class OutreachEngine:
    """Proprietarul complet al ciclului de viață `outreach_attempts`/
    `outreach_outcomes` — niciun alt engine nu scrie direct în aceste
    tabele."""

    def __init__(self, conversation_engine: ConversationEngine):
        self._conversation_engine = conversation_engine

    def create_outreach(
        self,
        owner_id: UUID,
        contact_id: UUID,
        purpose: str,
        message_text: str,
        tone_used: str,
    ) -> OutreachAttempt:
        """Creează intervenția — imutabilă de la acest moment (Regula 1).

        Raises:
            OutreachAccessDeniedError: `contact_id` nu aparține `owner_id`.
            InvalidPurposeError: `purpose` nu e `REFERRAL`/`REACTIVATION`.
            InvalidToneError: `tone_used` nu e una din cele 3 valori permise.
        """
        if purpose not in _VALID_PURPOSES:
            raise InvalidPurposeError(f"purpose invalid: {purpose!r}")
        if tone_used not in _VALID_TONES:
            raise InvalidToneError(f"tone_used invalid: {tone_used!r}")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM contacts WHERE id = %s AND owner_id = %s",
                    (contact_id, owner_id),
                )
                if cur.fetchone() is None:
                    raise OutreachAccessDeniedError(
                        f"Contact {contact_id} nu există sau nu aparține acestui owner."
                    )

                cur.execute(
                    """
                    INSERT INTO outreach_attempts
                        (owner_id, contact_id, purpose, message_text, tone_used)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, owner_id, contact_id, purpose, message_text, tone_used
                    """,
                    (owner_id, contact_id, purpose, message_text, tone_used),
                )
                row = cur.fetchone()

        outreach = OutreachAttempt(
            id=row[0], owner_id=row[1], contact_id=row[2],
            purpose=row[3], message_text=row[4], tone_used=row[5],
        )
        self._emit_event("OutreachSent", outreach.id, {
            "owner_id": str(owner_id), "purpose": purpose,
        })
        return outreach

    def record_outcome(
        self,
        owner_id: UUID,
        outreach_id: UUID,
        outcome: str,
    ) -> OutreachOutcomeResult:
        """Înregistrează reacția imediată observată — o singură dată per
        Outreach (Regula 5, `UNIQUE` la nivel de DB).

        Pentru `QUESTION_ASKED`/`HESITATION`/`WILL_RESPOND_LATER`, predă
        automat către `Conversation` (aceeași persoană). Pentru
        `REFERRAL_RECEIVED`/`POSITIVE_RESPONSE`, nu creează nimic automat
        — liderul continuă manual (Contract 46, §3.3).

        Raises:
            OutreachAccessDeniedError: `outreach_id` nu aparține `owner_id`.
            InvalidOutcomeError: `outcome` în afara celor 5 valori permise.
            OutcomeAlreadyRecordedError: acest Outreach are deja un Outcome.
        """
        if outcome not in _VALID_OUTCOMES:
            raise InvalidOutcomeError(f"outcome invalid: {outcome!r}")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT contact_id FROM outreach_attempts WHERE id = %s AND owner_id = %s",
                    (outreach_id, owner_id),
                )
                outreach_row = cur.fetchone()
                if outreach_row is None:
                    raise OutreachAccessDeniedError(
                        f"Outreach {outreach_id} nu există sau nu aparține acestui owner."
                    )
                contact_id = outreach_row[0]

                cur.execute(
                    "SELECT 1 FROM outreach_outcomes WHERE outreach_id = %s",
                    (outreach_id,),
                )
                if cur.fetchone() is not None:
                    raise OutcomeAlreadyRecordedError(
                        f"Outreach {outreach_id} are deja un Outcome înregistrat."
                    )

                cur.execute(
                    """
                    INSERT INTO outreach_outcomes (owner_id, outreach_id, outcome)
                    VALUES (%s, %s, %s)
                    RETURNING id, outreach_id, outcome
                    """,
                    (owner_id, outreach_id, outcome),
                )
                outcome_row = cur.fetchone()

        self._emit_event("OutreachOutcomeRecorded", outreach_id, {
            "owner_id": str(owner_id), "outcome": outcome,
        })

        conversation_id: Optional[UUID] = None
        if outcome in _OUTCOMES_WITH_AUTO_HANDOFF:
            conversation: Conversation = self._conversation_engine.get_or_create_conversation(
                owner_id=owner_id, contact_id=contact_id, source_outreach_id=outreach_id,
            )
            conversation_id = conversation.id

        return OutreachOutcomeResult(
            id=outcome_row[0], outreach_id=outcome_row[1], outcome=outcome_row[2],
            conversation_id=conversation_id,
        )

    def _emit_event(self, event_name: str, target_object_id: UUID, payload: dict) -> None:
        """Scrie evenimentul în tabelul generic `events` (pattern identic cu celelalte 7 engine-uri)."""
        from psycopg.types.json import Json

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO events (event_name, target_object, target_object_id, payload) "
                    "VALUES (%s, %s, %s, %s)",
                    (event_name, "outreach", target_object_id, Json(payload)),
                )
