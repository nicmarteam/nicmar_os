"""
FollowUpEngine — motorul de follow-up pentru NicMar OS.

Sursă: CONTACT-FOLLOWUP-VERTICAL-SLICE-CONTRACT v1, secțiunile 1.4, 1.6, 1.8.

Lanț implementat:
    RuleEngine → FOLLOWUP_READY/DUPLICATE → FollowUpEngine → follow_ups →
    FollowUpTriggered → DIS → scores

Diferență importantă față de MissionEngine (verificată din sursă, nu
copiată orbește): `02-business-objects-5-pillars.md` atribuie KPI `DIS`
evenimentului `FollowUpTriggered` însuși (crearea follow-up-ului), nu
finalizării lui — spre deosebire de Mission, unde DIS era legat de
`MissionCompleted`. De aceea, aici `DIS` se persistă la creare
(`create_from_trigger`), nu la `complete_followup`.

Reguli de design (identice cu MissionEngine):
- O singură cale de scriere a stării (`_set_status`).
- Confirmarea umană pentru finalizare e parametru explicit (`confirmed: bool`).
- `DIS` e persistat ca valoare-placeholder (1.0) — formula reală rămâne
  nedefinită în KPI-MODEL-001.

Cod oficial motor: ⚠️ NECONFIRMAT. Nu există `ENG-FOLLOWUP-XXX` în
03-rule-model-001.md (spre deosebire de ENG-MISSION-001) — nu inventăm
unul. Constanta ENGINE_CODE rămâne None, marcată explicit.

Nu implementate (out of scope v1, conform contractului):
- PriorityEngine
- RPS ca KPI persistat (rămâne scor operațional, nu se scrie în `scores`)
- Completion Rate, Consistency Score
- Conexiune proprie la DB — totul trece prin src.data.db.get_connection()
- Interacțiunea cu MissionEngine la FollowUpTriggered (rămâne FOLLOW-UP,
  nedocumentată suficient pentru implementare acum)
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from src.data.db import get_connection
from src.engines.rule.rule_engine import RuleEngine

# Neconfirmat în nicio sursă — nu inventăm un cod ENG-FOLLOWUP-XXX.
ENGINE_CODE: Optional[str] = None

# Sursă unică de adevăr — 09-MVP-DATA-001.md, follow_ups.status CHECK.
VALID_STATUSES = ("PENDING", "COMPLETED", "POSTPONED", "RESCHEDULED")

# Tranziții permise. Doar cele confirmate din sursă (05, Competența
# 06_Follow_Up: "Amână" -> POSTPONED, "Programăm un nou follow-up" ->
# RESCHEDULED, confirmare -> COMPLETED). POSTPONED/RESCHEDULED sunt
# terminale în v1 — nicio sursă nu documentează ce urmează după ele.
_ALLOWED_TRANSITIONS = {
    "PENDING": {"COMPLETED", "POSTPONED", "RESCHEDULED"},
    "COMPLETED": set(),
    "POSTPONED": set(),
    "RESCHEDULED": set(),
}

_EVENT_FOR_STATUS = {
    "PENDING": "FollowUpTriggered",
    "COMPLETED": "FollowUpCompleted",
    "POSTPONED": "FollowUpPostponed",
    "RESCHEDULED": "FollowUpRescheduled",
}


class FollowUpDuplicateError(Exception):
    """Ridicată când RuleEngine returnează FOLLOWUP_DUPLICATE."""


class InvalidTransitionError(Exception):
    """Ridicată la o tranziție de stare neconformă cu _ALLOWED_TRANSITIONS."""


class FollowUpAccessDeniedError(Exception):
    """
    Ridicată dacă followup_id nu există SAU nu aparține owner_id-ului dat.

    Mesaj identic pentru ambele cazuri — previne enumerare de ID-uri.
    Descoperit prin Security Isolation Audit (12 august 2026), aceeași
    categorie de gaură ca la MissionEngine.
    """


class HumanConfirmationRequiredError(Exception):
    """Ridicată dacă se încearcă finalizarea unui follow-up fără confirmare umană explicită."""


@dataclass(frozen=True)
class FollowUp:
    """Reprezentarea unui follow-up, așa cum e citit din `follow_ups`."""
    id: UUID
    owner_id: UUID
    contact_id: UUID
    conversation_id: Optional[UUID]
    status: str


class FollowUpEngine:
    """
    Motorul de follow-up — motor MVP confirmat (06-harta-motoare-tehnice.md).

    Depinde explicit de RuleEngine (injectat) — nu decide singur dacă
    un follow-up poate fi creat, doar execută decizia RuleEngine-ului.
    """

    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine

    # ------------------------------------------------------------------
    # Creare — trece prin RuleEngine, apoi persistă DIS imediat
    # ------------------------------------------------------------------

    def create_from_trigger(
        self,
        owner_id: UUID,
        contact_id: UUID,
        conversation_id: UUID,
        notes: Optional[str] = None,
        scheduled_at: Optional[str] = None,
    ) -> FollowUp:
        """
        Creează un follow-up nou, DOAR dacă RuleEngine confirmă
        FOLLOWUP_READY (nu există deja unul PENDING pe aceeași conversație).

        Persistă DIS imediat — sursa (02) atribuie DIS evenimentului
        FollowUpTriggered însuși, nu finalizării ulterioare.
        """
        rule_result = self.rule_engine.evaluate_followup(conversation_id)
        if rule_result.decision_outcome != "FOLLOWUP_READY":
            raise FollowUpDuplicateError(
                f"conversation_id={conversation_id} are deja un follow-up "
                f"PENDING — FollowUpEngine nu creează unul duplicat."
            )

        query = """
            INSERT INTO follow_ups
                (owner_id, contact_id, conversation_id, status, scheduled_at, notes)
            VALUES (%s, %s, %s, 'PENDING', COALESCE(%s, clock_timestamp()), %s)
            RETURNING id, owner_id, contact_id, conversation_id, status
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id, contact_id, conversation_id, scheduled_at, notes))
                row = cur.fetchone()

        followup = FollowUp(
            id=row[0], owner_id=row[1], contact_id=row[2],
            conversation_id=row[3], status=row[4],
        )
        self._emit_event("FollowUpTriggered", followup.id, {"conversation_id": str(conversation_id)})
        self._record_dis_score(followup.id, owner_id)
        return followup

    # ------------------------------------------------------------------
    # Citire — READ-ONLY, necesară pentru API (GET /followups)
    # ------------------------------------------------------------------

    def list_pending_followups(self, owner_id: UUID) -> List[FollowUp]:
        """
        Listează follow-up-urile PENDING ale unui owner (READ-ONLY).

        Filtrare OBLIGATORIE prin owner_id — aceeași disciplină de
        izolare ca la toate celelalte metode de citire (get_mission,
        get_recent_dis_score etc.). Doar status='PENDING' — celelalte
        stări (COMPLETED, POSTPONED, RESCHEDULED) nu apar în lista
        zilnică de acțiuni.

        Fără modificări în `follow_ups` — un singur SELECT.
        """
        query = """
            SELECT id, owner_id, contact_id, conversation_id, status
            FROM follow_ups
            WHERE owner_id = %s AND status = 'PENDING'
            ORDER BY created_at ASC
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id,))
                rows = cur.fetchall()

        return [
            FollowUp(id=row[0], owner_id=row[1], contact_id=row[2],
                     conversation_id=row[3], status=row[4])
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Tranziții — o singură cale de scriere a stării
    # ------------------------------------------------------------------

    def _set_status(self, followup_id: UUID, owner_id: UUID, new_status: str) -> FollowUp:
        """
        SINGURA metodă din tot fișierul care scrie `follow_ups.status`.

        `owner_id` OBLIGATORIU și verificat — la fel ca la MissionEngine
        (Security Isolation Audit, 12 august 2026). Fără el, oricine
        cunoștea un followup_id putea schimba starea oricărui follow-up.
        """
        if new_status not in VALID_STATUSES:
            raise InvalidTransitionError(f"Stare necunoscută: {new_status}")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT status FROM follow_ups WHERE id = %s AND owner_id = %s",
                    (followup_id, owner_id),
                )
                row = cur.fetchone()
                if row is None:
                    raise FollowUpAccessDeniedError(
                        f"FollowUp {followup_id} nu există sau nu aparține acestui owner."
                    )
                current_status = row[0]

                if new_status not in _ALLOWED_TRANSITIONS.get(current_status, set()):
                    raise InvalidTransitionError(
                        f"Tranziție interzisă: {current_status} -> {new_status}"
                    )

                cur.execute(
                    "UPDATE follow_ups SET status = %s, updated_at = clock_timestamp() "
                    "WHERE id = %s AND owner_id = %s "
                    "RETURNING id, owner_id, contact_id, conversation_id, status",
                    (new_status, followup_id, owner_id),
                )
                row = cur.fetchone()

                cur.execute(
                    "INSERT INTO state_history "
                    "(entity_type, entity_id, previous_state, new_state, triggered_by_event) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    ("followup", followup_id, current_status, new_status,
                     _EVENT_FOR_STATUS[new_status]),
                )

        followup = FollowUp(
            id=row[0], owner_id=row[1], contact_id=row[2],
            conversation_id=row[3], status=row[4],
        )
        self._emit_event(_EVENT_FOR_STATUS[new_status], followup_id, {"new_status": new_status})
        return followup

    def complete_followup(self, followup_id: UUID, owner_id: UUID, confirmed: bool) -> FollowUp:
        """
        PENDING -> COMPLETED.

        `confirmed` fără valoare implicită — reflectă direct cerința
        contractului: "liderul confirmă fiecare follow-up înainte să
        fie marcat ca realizat".
        """
        if not confirmed:
            raise HumanConfirmationRequiredError(
                "FollowUpCompleted necesită confirmare umană explicită (confirmed=True)."
            )
        return self._set_status(followup_id, owner_id, "COMPLETED")

    def postpone_followup(self, followup_id: UUID, owner_id: UUID) -> FollowUp:
        """PENDING -> POSTPONED. Alegerea liderului ('Amână') e ea însăși acțiunea."""
        return self._set_status(followup_id, owner_id, "POSTPONED")

    def reschedule_followup(self, followup_id: UUID, owner_id: UUID) -> FollowUp:
        """PENDING -> RESCHEDULED."""
        return self._set_status(followup_id, owner_id, "RESCHEDULED")

    # ------------------------------------------------------------------
    # KPI — DIS, persistat la creare (nu la finalizare — vezi docstring modul)
    # ------------------------------------------------------------------

    def _record_dis_score(self, followup_id: UUID, owner_id: UUID) -> None:
        """
        Persistă un scor DIS pentru follow-up-ul creat.

        ATENȚIE: score_value = 1.0 e PLACEHOLDER — formula reală rămâne
        nedefinită în KPI-MODEL-001. RPS NU se persistă aici — rămâne
        scor operațional (Decizia G2), nu KPI oficial.
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM kpis WHERE metric_code = %s", ("DIS",))
                row = cur.fetchone()
                if row is None:
                    raise RuntimeError(
                        "KPI 'DIS' nu există în tabelul kpis — trebuie seed-uit "
                        "cu cei 13 KPI din 04-KPI-REG-001.md."
                    )
                kpi_id = row[0]

                cur.execute(
                    "INSERT INTO scores "
                    "(kpi_id, entity_type, entity_id, score_value, engine_source) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (kpi_id, "followup", followup_id, 1.0, "FollowUpEngine"),
                )

    # ------------------------------------------------------------------
    # Evenimente
    # ------------------------------------------------------------------

    def _emit_event(self, event_name: str, target_object_id: UUID, payload: dict) -> None:
        """Scrie evenimentul în tabelul generic `events`."""
        from psycopg.types.json import Json

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO events (event_name, target_object, target_object_id, payload) "
                    "VALUES (%s, %s, %s, %s)",
                    (event_name, "followup", target_object_id, Json(payload)),
                )
