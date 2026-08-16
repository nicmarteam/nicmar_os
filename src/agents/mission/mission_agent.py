"""
MissionAgent — Agent 4 din 08-MVP-AGENT-001.md.

Sursă: MISSION-VERTICAL-SLICE-CONTRACT v1, ultima verigă a lanțului:
    RuleEngine → MissionEngine → missions → DIS/scores → MissionAgent →
    "Sunt gata, încep"

Regulă arhitecturală centrală: MissionAgent NU devine al doilea
MissionEngine. Nu scrie niciodată direct în `missions` — orice
schimbare de stare trece exclusiv prin `MissionEngine`, care rămâne
State Owner. MissionAgent doar:
    citește -> explică/recomandă -> cere confirmarea omului -> deleagă.

Excepție justificată: citirea (read-only) a scorului DIS direct din
`scores`, pentru context — același precedent ca `RelationshipEngine
READ-ONLY` la Contact Agent (audit P6). Contractul interzice scrierea
directă în DB, nu citirea.

Nu implementate (out of scope v1):
- PriorityEngine
- Completion Rate, Consistency Score
- Formule KPI inventate — DIS e doar citit, niciodată calculat aici
"""

from typing import Optional
from uuid import UUID

from src.data.db import get_connection
from src.engines.mission.mission_engine import Mission, MissionEngine


class MissionAgent:
    """
    Agent 4 — prezintă Misiunea Zilei, cere confirmare umană, deleagă
    orice tranziție de stare către MissionEngine.
    """

    def __init__(self, mission_engine: MissionEngine):
        self.mission_engine = mission_engine

    # ------------------------------------------------------------------
    # Prezentare — "Legea Primului Pas": un singur pas concret, nu o listă
    # ------------------------------------------------------------------

    def present_daily_mission(self, mission: Mission) -> str:
        """
        Formulează recomandarea pentru lider, aliniată cu Competența 12
        (08-MVP-AGENT-001.md, Agent 4) — un singur pas, nu o listă lungă.
        """
        return f"Pasul tău de azi: {mission.title}"

    # ------------------------------------------------------------------
    # Citire — READ-ONLY, aceeași regulă ca RelationshipEngine la P6
    # ------------------------------------------------------------------

    def get_recent_dis_score(self, owner_id: UUID) -> Optional[float]:
        """
        Citește cel mai recent scor DIS al owner-ului, doar pentru
        context afișat liderului. READ-ONLY explicit — un singur
        SELECT, nicio scriere, nicio conexiune proprie duplicată
        (folosește get_connection() din src.data.db, ca peste tot).
        """
        query = """
            SELECT s.score_value
            FROM scores s
            JOIN kpis k ON s.kpi_id = k.id
            JOIN missions m ON s.entity_id = m.id
            WHERE k.metric_code = 'DIS'
              AND s.entity_type = 'mission'
              AND m.owner_id = %s
            ORDER BY s.calculated_at DESC
            LIMIT 1
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id,))
                row = cur.fetchone()
        return row[0] if row else None

    # ------------------------------------------------------------------
    # Confirmare umană — deleagă, nu scrie
    # ------------------------------------------------------------------

    def confirm_and_start(self, mission_id: UUID, owner_id: UUID, confirmed: bool) -> Mission:
        """
        Punctul de Human-in-the-loop: "Sunt gata, încep".

        `owner_id` obligatoriu — transmis mai departe către
        MissionEngine.start_mission(), care verifică real izolarea
        (Security Isolation Audit, 12 august 2026).
        """
        return self.mission_engine.start_mission(mission_id, owner_id, confirmed=confirmed)

    def confirm_completion(self, mission_id: UUID, owner_id: UUID) -> Mission:
        """
        Marchează misiunea ca finalizată — deleagă complet către
        MissionEngine.complete_mission(), care persistă și DIS.
        MissionAgent nu calculează, nu scrie, doar deleagă.
        """
        return self.mission_engine.complete_mission(mission_id, owner_id)
