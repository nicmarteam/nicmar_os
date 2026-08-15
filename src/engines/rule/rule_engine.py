"""
RuleEngine — motorul de evaluare a regulilor pentru NicMar OS.

Sursă: MISSION-VERTICAL-SLICE-CONTRACT v1, secțiunea 1.3, extins prin
CONTACT-FOLLOWUP-VERTICAL-SLICE-CONTRACT v1, secțiunea 1.3.

Reguli implementate:
- RULE-MISSION-DAILY-001 — "dacă owner_id are mai puțin de 1 misiune
  activă azi, misiunea poate fi generată."
- RULE-FOLLOWUP-DUPLICATE-001 — "dacă o Conversation e în
  FOLLOWUP_NEEDED și nu are deja un follow_up PENDING asociat,
  poate fi generat unul nou."

Design: logica pură de decizie (`evaluate_mission_readiness`,
`evaluate_followup_readiness`) e separată de accesul la date
(`count_active_missions_today`, `has_pending_followup`,
`persist_evaluation`). Prima categorie e testabilă fără bază de date.
A doua folosește exclusiv `src.data.db.get_connection()` — nicio
conexiune proprie, nicio logică de DB duplicată aici.

Notă de extensie: regula FollowUp are propriul dataclass de rezultat
(`FollowUpRuleEvaluationResult`), separat de `RuleEvaluationResult`
(Mission) — cele două reguli au context diferit (număr de misiuni vs.
existența unui duplicat), nu se forțează într-o structură comună
artificială. Regula Mission existentă rămâne complet neatinsă.

Nu implementate (out of scope v1, conform contractului):
- PriorityEngine (capability separată, nu parte din RuleEngine)
- Completion Rate, Consistency Score (metrici neconfirmate în KPI Registry)
"""

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from src.data.db import get_connection

DecisionOutcome = Literal["MISSION_READY", "MISSION_BLOCKED"]
FollowUpDecisionOutcome = Literal["FOLLOWUP_READY", "FOLLOWUP_DUPLICATE"]

# Stările de Mission considerate "active" — conform 09-MVP-DATA-001.md,
# missions.status CHECK (GENERATED, ASSIGNED, IN_PROGRESS, COMPLETED).
# COMPLETED nu e activă; restul da.
_ACTIVE_MISSION_STATUSES = ("GENERATED", "ASSIGNED", "IN_PROGRESS")


@dataclass(frozen=True)
class RuleEvaluationResult:
    """
    Rezultatul evaluării regulii Mission.

    Câmpurile reflectă exact structura tabelului `rule_evaluations`
    (09-MVP-DATA-001.md, secțiunea 5.2), fără câmpuri suplimentare
    inventate.
    """
    rule_code: str
    rule_version: str
    decision_outcome: DecisionOutcome
    active_mission_count: int


@dataclass(frozen=True)
class FollowUpRuleEvaluationResult:
    """
    Rezultatul evaluării regulii FollowUp (RULE-FOLLOWUP-DUPLICATE-001).

    Separat de `RuleEvaluationResult` — context diferit (existența unui
    duplicat, nu un număr de misiuni active).
    """
    rule_code: str
    rule_version: str
    decision_outcome: FollowUpDecisionOutcome
    had_pending_duplicate: bool


class RuleEngine:
    """
    Motor de evaluare a regulilor — cod oficial ENG-RULE-001.

    v1 implementează 2 reguli: RULE-MISSION-DAILY-001 și
    RULE-FOLLOWUP-DUPLICATE-001. Nu conține reguli inventate din
    exemplele ilustrative ale RULE-MODEL-001 — doar regulile explicit
    confirmate în contractele vertical slice-urilor.
    """

    RULE_CODE = "RULE-MISSION-DAILY-001"
    RULE_VERSION = "1.0.0"

    FOLLOWUP_RULE_CODE = "RULE-FOLLOWUP-DUPLICATE-001"
    FOLLOWUP_RULE_VERSION = "1.0.0"

    # ------------------------------------------------------------------
    # Regula Mission — NEATINSĂ față de Mission Vertical Slice
    # ------------------------------------------------------------------

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

        Folosește `get_connection()` din `src.data.db`, nu deschide
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
        """Comoditate: numără misiunile active, apoi evaluează regula Mission."""
        count = self.count_active_missions_today(owner_id)
        return self.evaluate_mission_readiness(count)

    # ------------------------------------------------------------------
    # Regula FollowUp — NOU, extensie pentru Contact→FollowUp Slice
    # ------------------------------------------------------------------

    def evaluate_followup_readiness(self, had_pending_duplicate: bool) -> FollowUpRuleEvaluationResult:
        """
        Decizie pură, fără acces la date.

        Regulă: dacă NU există deja un follow_up cu status PENDING
        pentru aceeași conversație, poate fi generat unul nou
        (FOLLOWUP_READY). Altfel, blocat (FOLLOWUP_DUPLICATE) — nu
        generăm follow-up-uri duplicate pentru aceeași conversație.
        """
        outcome: FollowUpDecisionOutcome = (
            "FOLLOWUP_DUPLICATE" if had_pending_duplicate else "FOLLOWUP_READY"
        )
        return FollowUpRuleEvaluationResult(
            rule_code=self.FOLLOWUP_RULE_CODE,
            rule_version=self.FOLLOWUP_RULE_VERSION,
            decision_outcome=outcome,
            had_pending_duplicate=had_pending_duplicate,
        )

    def has_pending_followup(self, conversation_id: UUID) -> bool:
        """
        Verifică dacă există deja un follow_up PENDING pentru
        aceeași conversație.

        Folosește `get_connection()` din `src.data.db`, nu deschide
        o conexiune proprie.
        """
        query = """
            SELECT COUNT(*)
            FROM follow_ups
            WHERE conversation_id = %s
              AND status = 'PENDING'
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (conversation_id,))
                (count,) = cur.fetchone()
        return count > 0

    def evaluate_followup(self, conversation_id: UUID) -> FollowUpRuleEvaluationResult:
        """Comoditate: verifică duplicate, apoi evaluează regula FollowUp."""
        had_duplicate = self.has_pending_followup(conversation_id)
        return self.evaluate_followup_readiness(had_duplicate)

    # ------------------------------------------------------------------
    # Persistență — comună ambelor reguli (interfață identică)
    # ------------------------------------------------------------------

    def persist_evaluation(
        self,
        result,
        rule_id: UUID,
        target_object_type: str,
        target_object_id: UUID,
        engine_source: str = "RuleEngine",
    ) -> None:
        """
        Scrie rezultatul unei evaluări (Mission SAU FollowUp) în
        `rule_evaluations`. Acceptă orice rezultat cu `rule_code`,
        `rule_version`, `decision_outcome` — funcționează identic
        pentru ambele reguli, fără duplicare de cod.

        `rule_id` trebuie să existe deja în tabelul `rules` (regulile
        se seed-uiesc separat, nu aici — acest fișier nu creează
        reguli, doar le evaluează).
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
