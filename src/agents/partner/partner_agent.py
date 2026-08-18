"""
PartnerAgent — Agent 5 din 08-MVP-AGENT-001.md.

Sursă: PARTNER-VERTICAL-SLICE-CONTRACT v1, secțiunea 1.6.

Regulă arhitecturală centrală (identică cu Mission/FollowUp Agent):
PartnerAgent NU devine al doilea PartnerEngine. Nu scrie niciodată
direct în `partners` sau `scores` — orice tranziție/persistență trece
exclusiv prin PartnerEngine.

Simplificare semnalată onest (nu ascunsă): sursa (05, Competența 27)
descrie 2 alegeri separate — Ecranul 3 (diagnostic, 4 variante,
generat de sistem) și Ecranul 4 (direcție emoțională dorită, 5
variante: Susținut/Încrezător/Motivat/Însoțit/Valoros, aleasă de
lider). v1 implementează doar Ecranul 3 (diagnostic_type) — selecția
separată a direcției emoționale (Ecranul 4) rămâne FOLLOW-UP, nu
inventăm o combinare nedocumentată a celor două.

Nu implementate (out of scope v1):
- Selecția celor 5 direcții emoționale (Ecranul 4)
- PriorityEngine — selecția partenerului cu cea mai mare nevoie
- Generare reală de mesaj (rămâne STUB, din PartnerEngine)
"""

from typing import Optional
from uuid import UUID

from src.data.db import get_connection
from src.engines.partner.partner_engine import Partner, PartnerDiagnostic, PartnerEngine


class PartnerAgent:
    """
    Agent 5 — solicită diagnosticul, prezintă mesajul (stub), cere
    confirmare umană, deleagă orice tranziție/persistență către
    PartnerEngine.
    """

    def __init__(self, partner_engine: PartnerEngine):
        self.partner_engine = partner_engine

    # ------------------------------------------------------------------
    # Creare — Decizia 32, deleagă integral, fără logică proprie
    # ------------------------------------------------------------------

    def create_partner(self, owner_id: UUID, contact_id: UUID) -> Partner:
        """Deleagă crearea către PartnerEngine — agentul nu decide nimic aici."""
        return self.partner_engine.create_partner(owner_id, contact_id)

    # ------------------------------------------------------------------
    # Solicitare diagnostic — deleagă, nu generează singur
    # ------------------------------------------------------------------

    def request_diagnostic(
        self, partner_id: UUID, owner_id: UUID, diagnostic_type: str
    ) -> PartnerDiagnostic:
        """
        Deleagă generarea diagnosticului către PartnerEngine. Agentul
        nu decide singur dacă partenerul poate primi un diagnostic
        (asta e regula RuleEngine, executată de PartnerEngine).
        """
        return self.partner_engine.generate_diagnostic(partner_id, owner_id, diagnostic_type)

    # ------------------------------------------------------------------
    # Prezentare
    # ------------------------------------------------------------------

    def present_diagnostic(self, diagnostic: PartnerDiagnostic) -> str:
        """
        Prezintă diagnosticul + mesajul (stub) liderului, aliniat cu
        Ecranele 3 și 5 din Competența 27 (05).
        """
        return (
            f"Diagnostic: {diagnostic.diagnostic_type}\n"
            f"Mesaj propus: {diagnostic.message}"
        )

    # ------------------------------------------------------------------
    # Citire — READ-ONLY, același precedent ca Mission/FollowUp Agent
    # ------------------------------------------------------------------

    def get_recent_scores(self, owner_id: UUID) -> dict:
        """
        Citește cele mai recente scoruri PDI și PIP ale owner-ului,
        legate de interacțiuni cu parteneri. READ-ONLY — doar SELECT,
        nicio scriere.

        Filtrare prin JOIN pe `partners.owner_id` — fără acest JOIN,
        interogarea ar citi scorurile tuturor partenerilor din sistem,
        nu doar ai owner_id-ului cerut (bug real, găsit la testul de
        integrare, corectat aici).
        """
        result = {}
        query = """
            SELECT k.metric_code, s.score_value
            FROM scores s
            JOIN kpis k ON s.kpi_id = k.id
            JOIN partners p ON s.entity_id = p.id
            WHERE k.metric_code IN ('PDI', 'PIP')
              AND s.entity_type = 'partner'
              AND p.owner_id = %s
            ORDER BY s.calculated_at DESC
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id,))
                for metric_code, score_value in cur.fetchall():
                    result.setdefault(metric_code, score_value)
        return result

    # ------------------------------------------------------------------
    # Confirmare umană — deleagă, nu scrie
    # ------------------------------------------------------------------

    def confirm_and_send(self, partner_id: UUID, owner_id: UUID, confirmed: bool) -> None:
        """
        Punctul de Human-in-the-loop: liderul confirmă mesajul (Ecranul
        6) și îl "trimite" (Ecranul 7). Deleagă integral către
        PartnerEngine.confirm_and_complete(), care persistă PDI/PIP.
        """
        self.partner_engine.confirm_and_complete(partner_id, owner_id, confirmed=confirmed)
