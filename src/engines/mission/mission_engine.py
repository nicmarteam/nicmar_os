"""
MissionEngine — motorul de misiuni pentru NicMar OS.

Sursă: MISSION-VERTICAL-SLICE-CONTRACT v1, secțiunile 1.4, 1.8, 1.9, 1.10.
Cod motor: ENG-MISSION-001 — plauzibil, nu pe deplin confirmat (corectură
de consecvență, 12 august 2026 — apare doar ca valoare de exemplu în
03-rule-model-001.md, secțiunea Rule Ownership, sub "Exemplu:", aceeași
categorie de încredere ca ENG-FOLLOWUP-XXX din followup_engine.py, care
a rămas explicit "neconfirmat". Tratarea inconsecventă anterioară — acest
cod numit "confirmat" — a fost o supra-afirmare, corectată acum.)

Lanț implementat:
    RuleEngine → MISSION_READY/BLOCKED → MissionEngine → missions →
    MissionGenerated/Started/Completed → DIS → scores

Reguli de design:
- O singură cale de scriere a stării (`_set_status`) — nicio altă
  metodă nu atinge direct `missions.status`.
- Confirmarea umană pentru `MissionStarted` e un parametru explicit
  (`confirmed: bool`), nu doar o convenție de apelare — motorul refuză
  activ tranziția fără ea.
- `DIS` e persistat ca valoare-placeholder (1.0 per misiune completată).
  Formula reală rămâne nedefinită în KPI-MODEL-001 — nu inventăm una aici.

Nu implementate (out of scope v1, conform contractului):
- PriorityEngine
- Completion Rate, Consistency Score
- Conexiune proprie la DB — totul trece prin src.data.db.get_connection()
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.data.db import get_connection
from src.engines.rule.rule_engine import RuleEngine

ENGINE_CODE = "ENG-MISSION-001"

# Sursă unică de adevăr pentru stările valide — 09-MVP-DATA-001.md,
# missions.status CHECK.
VALID_STATUSES = ("GENERATED", "ASSIGNED", "IN_PROGRESS", "COMPLETED")

# Tranzițiile permise — un singur drum înainte, fără sărituri.
_ALLOWED_TRANSITIONS = {
    "GENERATED": {"ASSIGNED"},
    "ASSIGNED": {"IN_PROGRESS"},
    "IN_PROGRESS": {"COMPLETED"},
    "COMPLETED": set(),
}

# Numele evenimentelor, exact ca în Event Catalog (02-business-objects-5-pillars.md).
_EVENT_FOR_STATUS = {
    "GENERATED": "MissionGenerated",
    "ASSIGNED": "MissionAssigned",
    "IN_PROGRESS": "MissionStarted",
    "COMPLETED": "MissionCompleted",
}


class MissionNotReadyError(Exception):
    """Ridicată când RuleEngine returnează MISSION_BLOCKED."""


class InvalidTransitionError(Exception):
    """Ridicată la o tranziție de stare neconformă cu _ALLOWED_TRANSITIONS."""


class HumanConfirmationRequiredError(Exception):
    """Ridicată dacă se încearcă pornirea unei misiuni fără confirmare umană explicită."""


@dataclass(frozen=True)
class Mission:
    """Reprezentarea unei misiuni, așa cum e citită din `missions`."""
    id: UUID
    owner_id: UUID
    title: str
    status: str


class MissionEngine:
    """
    Motorul de misiuni — Primary Engine / State Owner pentru Mission.

    Depinde explicit de RuleEngine (injectat, nu instanțiat intern) —
    MissionEngine nu decide singur dacă o misiune poate fi generată,
    doar execută decizia RuleEngine-ului.
    """

    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine

    # ------------------------------------------------------------------
    # Generare — trece prin RuleEngine înainte de orice scriere
    # ------------------------------------------------------------------

    def generate_mission(self, owner_id: UUID, title: str, description: Optional[str] = None) -> Mission:
        """
        Generează o misiune nouă, DOAR dacă RuleEngine confirmă MISSION_READY.

        Ridică MissionNotReadyError dacă owner_id are deja o misiune activă azi
        — nu generăm misiuni multiple simultan (RULE-MISSION-DAILY-001).
        """
        rule_result = self.rule_engine.evaluate(owner_id)
        if rule_result.decision_outcome != "MISSION_READY":
            raise MissionNotReadyError(
                f"owner_id={owner_id} are deja {rule_result.active_mission_count} "
                f"misiune(i) activă/e azi — MissionEngine nu generează una nouă."
            )

        query = """
            INSERT INTO missions (owner_id, title, description, status)
            VALUES (%s, %s, %s, 'GENERATED')
            RETURNING id, owner_id, title, status
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id, title, description))
                row = cur.fetchone()

        mission = Mission(id=row[0], owner_id=row[1], title=row[2], status=row[3])
        self._emit_event("MissionGenerated", mission.id, {"owner_id": str(owner_id)})
        return mission

    # ------------------------------------------------------------------
    # Tranziții — o singură cale de scriere a stării
    # ------------------------------------------------------------------

    def _set_status(self, mission_id: UUID, new_status: str) -> Mission:
        """
        SINGURA metodă din tot fișierul care scrie `missions.status`.

        Validează tranziția, scrie noua stare, înregistrează în
        `state_history`, emite evenimentul corespunzător. Orice altă
        metodă publică (assign_mission, start_mission, complete_mission)
        trece prin aceasta — nu duplică logică de scriere.
        """
        if new_status not in VALID_STATUSES:
            raise InvalidTransitionError(f"Stare necunoscută: {new_status}")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT status FROM missions WHERE id = %s", (mission_id,))
                row = cur.fetchone()
                if row is None:
                    raise InvalidTransitionError(f"Mission {mission_id} nu există.")
                current_status = row[0]

                if new_status not in _ALLOWED_TRANSITIONS.get(current_status, set()):
                    raise InvalidTransitionError(
                        f"Tranziție interzisă: {current_status} -> {new_status}"
                    )

                cur.execute(
                    "UPDATE missions SET status = %s, updated_at = clock_timestamp() "
                    "WHERE id = %s RETURNING id, owner_id, title, status",
                    (new_status, mission_id),
                )
                row = cur.fetchone()

                cur.execute(
                    "INSERT INTO state_history "
                    "(entity_type, entity_id, previous_state, new_state, triggered_by_event) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    ("mission", mission_id, current_status, new_status,
                     _EVENT_FOR_STATUS[new_status]),
                )

        mission = Mission(id=row[0], owner_id=row[1], title=row[2], status=row[3])
        self._emit_event(_EVENT_FOR_STATUS[new_status], mission_id, {"new_status": new_status})
        return mission

    def assign_mission(self, mission_id: UUID) -> Mission:
        """GENERATED -> ASSIGNED. Fără confirmare umană necesară aici (afișare în Dashboard)."""
        return self._set_status(mission_id, "ASSIGNED")

    def start_mission(self, mission_id: UUID, confirmed: bool) -> Mission:
        """
        ASSIGNED -> IN_PROGRESS.

        `confirmed` NU are valoare implicită — apelantul trebuie să decidă
        explicit True/False. Reflectă direct butonul "Sunt gata, încep"
        din Mission Agent (08-MVP-AGENT-001.md) — fără el, tranziția nu are loc.
        """
        if not confirmed:
            raise HumanConfirmationRequiredError(
                "MissionStarted necesită confirmare umană explicită (confirmed=True)."
            )
        return self._set_status(mission_id, "IN_PROGRESS")

    def complete_mission(self, mission_id: UUID) -> Mission:
        """
        IN_PROGRESS -> COMPLETED. Persistă și DIS (placeholder) în `scores`.
        """
        mission = self._set_status(mission_id, "COMPLETED")
        self._record_dis_score(mission.id, mission.owner_id)
        return mission

    # ------------------------------------------------------------------
    # KPI — DIS, prin infrastructura kpis + scores
    # ------------------------------------------------------------------

    def _record_dis_score(self, mission_id: UUID, owner_id: UUID) -> None:
        """
        Persistă un scor DIS pentru misiunea completată.

        ATENȚIE: score_value = 1.0 e un PLACEHOLDER — formula reală a
        DIS nu e încă definită în KPI-MODEL-001 (03-rule-model-001.md
        marchează explicit "Va fi definită"). Acest MVP confirmă doar
        mecanismul de persistență (kpis -> scores), nu calculul final.
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM kpis WHERE metric_code = %s", ("DIS",))
                row = cur.fetchone()
                if row is None:
                    raise RuntimeError(
                        "KPI 'DIS' nu există în tabelul kpis — trebuie seed-uit "
                        "cu cei 13 KPI din 04-KPI-REG-001.md înainte de prima misiune completată."
                    )
                kpi_id = row[0]

                cur.execute(
                    "INSERT INTO scores "
                    "(kpi_id, entity_type, entity_id, score_value, engine_source) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (kpi_id, "mission", mission_id, 1.0, ENGINE_CODE),
                )

    # ------------------------------------------------------------------
    # Evenimente
    # ------------------------------------------------------------------

    def _emit_event(self, event_name: str, target_object_id: UUID, payload: dict) -> None:
        """Scrie evenimentul în tabelul generic `events`."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO events (event_name, target_object, target_object_id, payload) "
                    "VALUES (%s, %s, %s, %s)",
                    (event_name, "mission", target_object_id, psycopg_json(payload)),
                )


def psycopg_json(payload: dict):
    """Helper minimal — psycopg3 serializează dict-uri direct pentru JSONB."""
    from psycopg.types.json import Json
    return Json(payload)
