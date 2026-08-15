"""
RuleEngine — motorul de evaluare a regulilor pentru NicMar OS.

Sursă: MISSION-VERTICAL-SLICE-CONTRACT v1, secțiunea 1.3.
Regulă implementată: RULE-MISSION-DAILY-001 — "dacă owner_id are
mai puțin de 1 misiune activă azi, misiunea poate fi generată."

Design: logica pură de decizie (`evaluate_mission_readiness`) e separată
de accesul la date (`count_active_missions_today`, `persist_evaluation`).
Primul e testabil fără bază de date. Al doilea folosește exclusiv
`src.data.db.get_connection()` — nicio conexiune proprie, nicio
logică de DB duplicată aici.

Nu implementate (out of scope v1, conform contractului):
- PriorityEngine (capability separată, nu parte din RuleEngine)
- Completion Rate, Consistency Score (metrici neconfirmate în KPI Registry)
"""

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from src.data.db import get_connection

DecisionOutcome = Literal["MISSION_READY", "MISSION_BLOCKED"]

# Stările de Mission considerate "active" — conform 09-MVP-DATA-001.md,
# missions.status CHECK (GENERATED, ASSIGNED, IN_PROGRESS, COMPLETED).
# COMPLETED nu e activă; restul da.
_ACTIVE_MISSION_STATUSES = ("GENERATED", "ASSIGNED", "IN_PROGRESS")


@dataclass(frozen=True)
class RuleEvaluationResult:
    """
    Rezultatul unei evaluări de regulă.

    Câmpurile reflectă exact structura tabelului `rule_evaluations`
    (09-MVP-DATA-001.md, secțiunea 5.2), fără câmpuri suplimentare
    inventate.
    """
    rule_code: str
    rule_version: str
    decision_outcome: DecisionOutcome
    active_mission_count: int


class RuleEngine:
    """
    Motor de evaluare a regulilor — cod oficial ENG-RULE-001.

    Pentru v1, implementează o singură regulă (RULE-MISSION-DAILY-001).
    Nu conține reguli inventate din exemplele ilustrative ale
    RULE-MODEL-001 — doar regula explicit confirmată în contractul
    vertical slice-ului.
    """

    RULE_CODE = "RULE-MISSION-DAILY-001"
    RULE_VERSION = "1.0.0"

    def evaluate_mission_readiness(self, active_mission_count: int) -> RuleEvaluationResult:
        """
        Decizie pură, fără acces la date.

        Regulă: dacă owner_id are 0 misiuni active azi, e pregătit
        pentru o misiune nouă (MISSION_READY). Altfel, blocat
        (MISSION_BLOCKED) — nu generăm misiuni multiple simultan.
        """
        outcome: DecisionOutcome = (
            "MISSION_READY" if active_mission_count < 1 else "MISSION_BLOCKED"
        )
        return RuleEvaluationResult(
            rule_code=self.RULE_CODE,
            rule_version=self.RULE_VERSION,
            decision_outcome=outcome,
            active_mission_count=active_mission_count,
        )

    def count_active_missions_today(self, owner_id: UUID) -> int:
        """
        Numără misiunile active ale unui owner, generate azi.

        Singura metodă din acest fișier care atinge baza de date —
        folosește `get_connection()` din `src.data.db`, nu deschide
        o conexiune proprie.
        """
        placeholders = ", ".join(["%s"] * len(_ACTIVE_MISSION_STATUSES))
        query = f"""
            SELECT COUNT(*)
            FROM missions
            WHERE owner_id = %s
              AND status IN ({placeholders})
              AND created_at::date = CURRENT_DATE
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id, *_ACTIVE_MISSION_STATUSES))
                (count,) = cur.fetchone()
        return count

    def evaluate(self, owner_id: UUID) -> RuleEvaluationResult:
        """Comoditate: numără misiunile active, apoi evaluează regula."""
        count = self.count_active_missions_today(owner_id)
        return self.evaluate_mission_readiness(count)

    def persist_evaluation(
        self,
        result: RuleEvaluationResult,
        rule_id: UUID,
        target_object_type: str,
        target_object_id: UUID,
        engine_source: str = "RuleEngine",
    ) -> None:
        """
        Scrie rezultatul evaluării în `rule_evaluations`.

        `rule_id` trebuie să existe deja în tabelul `rules` (regula
        RULE-MISSION-DAILY-001 se seed-uiește separat, nu aici —
        acest fișier nu creează reguli, doar le evaluează).
        """
        query = """
            INSERT INTO rule_evaluations
                (rule_id, rule_code, rule_version, target_object_type,
                 target_object_id, result, engine_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        rule_id,
                        result.rule_code,
                        result.rule_version,
                        target_object_type,
                        target_object_id,
                        result.decision_outcome,
                        engine_source,
                    ),
                )
