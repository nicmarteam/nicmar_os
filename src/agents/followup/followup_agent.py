"""
FollowUpAgent — Agent 3 din 08-MVP-AGENT-001.md.

Sursă: CONTACT-FOLLOWUP-VERTICAL-SLICE-CONTRACT v1, secțiunile 1.7, 1.8, 1.9.

Regulă arhitecturală centrală (identică cu MissionAgent): FollowUpAgent
NU devine al doilea FollowUpEngine. Nu scrie niciodată direct în
`follow_ups` sau `scores` — orice schimbare de stare trece exclusiv
prin `FollowUpEngine`.

Limită onestă despre RPS: contractul (08) cere ordonarea listei după
Relationship Priority Score, dar formula lui rămâne nedefinită
(05-competente-37-motor1.md descrie doar componentele, fără formula
exactă) — nu o inventăm aici. v1 nu calculează RPS; ordonarea reală
după RPS rămâne FOLLOW-UP, până la formalizarea KPI-MODEL-001.
RPS, oricum, nu se persistă niciodată (Decizia G2 — scor operațional,
nu KPI oficial).

Nu implementate (out of scope v1):
- PriorityEngine
- Calculul formulei RPS
- Completion Rate, Consistency Score
"""

from typing import List, Optional
from uuid import UUID

from src.data.db import get_connection
from src.engines.followup.followup_engine import FollowUp, FollowUpEngine


class FollowUpAgent:
    """
    Agent 3 — prezintă follow-up-urile zilei, cere confirmare umană
    pentru finalizare, deleagă orice tranziție de stare către
    FollowUpEngine.
    """

    def __init__(self, followup_engine: FollowUpEngine):
        self.followup_engine = followup_engine

    # ------------------------------------------------------------------
    # Prezentare
    # ------------------------------------------------------------------

    def present_followup_list(self, followups: List[FollowUp]) -> str:
        """
        Prezintă lista de follow-up-uri primită, în ordinea în care e
        dată (nu recalculează ordinea aici — vezi nota despre RPS în
        docstring-ul modulului).
        """
        if not followups:
            return "Niciun follow-up programat azi."
        lines = [f"- Contact {f.contact_id}  (status: {f.status})" for f in followups]
        return "Follow-up-urile tale de azi:\n" + "\n".join(lines)

    # ------------------------------------------------------------------
    # Citire — READ-ONLY, același precedent ca Mission Agent
    # ------------------------------------------------------------------

    def get_recent_dis_score(self, owner_id: UUID) -> Optional[float]:
        """
        Citește cel mai recent scor DIS al owner-ului, legat de
        follow-up-uri. READ-ONLY — un singur SELECT, nicio scriere.
        """
        query = """
            SELECT s.score_value
            FROM scores s
            JOIN kpis k ON s.kpi_id = k.id
            JOIN follow_ups f ON s.entity_id = f.id
            WHERE k.metric_code = 'DIS'
              AND s.entity_type = 'followup'
              AND f.owner_id = %s
            ORDER BY s.calculated_at DESC
            LIMIT 1
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id,))
                row = cur.fetchone()
        return row[0] if row else None

    # ------------------------------------------------------------------
    # Confirmare umană / acțiuni — deleagă, nu scrie
    # ------------------------------------------------------------------

    def confirm_completion(self, followup_id: UUID, owner_id: UUID, confirmed: bool) -> FollowUp:
        """
        Punctul de Human-in-the-loop: liderul confirmă că follow-up-ul
        a fost realizat. `owner_id` obligatoriu — verificat real de
        FollowUpEngine (Security Isolation Audit, 12 august 2026).
        """
        return self.followup_engine.complete_followup(followup_id, owner_id, confirmed=confirmed)

    def request_postpone(self, followup_id: UUID, owner_id: UUID) -> FollowUp:
        """Liderul alege 'Amână' — deleagă către FollowUpEngine.postpone_followup()."""
        return self.followup_engine.postpone_followup(followup_id, owner_id)

    def request_reschedule(self, followup_id: UUID, owner_id: UUID) -> FollowUp:
        """Liderul alege 'Programăm un nou follow-up' — deleagă către FollowUpEngine."""
        return self.followup_engine.reschedule_followup(followup_id, owner_id)
