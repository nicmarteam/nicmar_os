"""
ContactAgent — Agent 1 din 08-MVP-AGENT-001.md.

Sursă: 20-contact-agent-contract.md, secțiunile 1-9 (verificat linie cu
linie față de schema reală și codul existent Mission/FollowUp/Partner).

Regulă arhitecturală centrală (identică cu Mission/FollowUp/Partner
Agent): ContactAgent este STRICT read-only. Nu scrie niciodată în
`contacts`, `clients`, `partners`, `follow_ups` sau `scores`. Nu
declanșează nicio tranziție de stare — acestea rămân, conform
`02-business-objects-5-pillars.md`, exclusiv în sarcina evenimentelor
reale de interacțiune.

Fără ContactEngine dedicat în v1 — motivat în contract secțiunea 8:
agentul nu scrie nimic, deci nu are nevoie de un State Owner propriu.

Nu implementate (out of scope v1, contract secțiunea 4 și 10):
- RelationshipEngine, CustomerRelationshipEngine, PartnerRelationshipEngine
  (toate absente din cod / dependințe arhitecturale declarate, nu
  implementate — v. contract secțiunea 1)
- CRH (zero producători în `scores`, nu se citește niciodată)
- Conversation Agent / context conversațional
- Scor de prioritate compozit (echivalentul PriorityEngine pentru Contact)

Limitare semnalată explicit (nu ascunsă): scorurile PDI/PIP sunt citite
per owner_id (cel mai recent scor global al liderului), nu per Partener
individual — identic cu precedentul din `PartnerAgent.get_recent_scores()`.
Dacă un owner are mai mulți Contacți convertiți în Partner, toți vor
afișa același PDI/PIP (cel mai recent global). Distincția per-partener
ar necesita o interogare suplimentară per contact, în afara scopului v1.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from src.data.db import get_connection

# Tuplul brut întors de interogarea principală, în ordinea coloanelor:
# (contact_id, full_name, status, last_followup_at, last_followup_status,
#  converted_to, updated_at)
_ContactRow = Tuple[
    UUID, str, str, Optional[datetime], Optional[str], Optional[str], datetime
]


@dataclass(frozen=True)
class ContactSummary:
    """Rezumatul unui Contact, așa cum e prezentat liderului de ContactAgent.

    Attributes:
        contact_id: Identificatorul Contactului.
        full_name: Numele complet al Contactului.
        status: Starea curentă (NEW, ACTIVE, CONVERTED, ARCHIVED).
        last_followup_at: Data programată a celui mai recent FollowUp,
            sau None dacă nu există niciun FollowUp pentru acest Contact.
        last_followup_status: Starea celui mai recent FollowUp
            (PENDING, COMPLETED, POSTPONED, RESCHEDULED), sau None.
        converted_to: "client" dacă există un rând corespondent în
            `clients`, "partner" dacă există în `partners`, altfel None.
        pdi: Cel mai recent scor Partner Development Index al owner-ului,
            populat doar când converted_to == "partner" și există deja
            o scriere reală în `scores`. Niciodată calculat aici.
        pip: Analog cu pdi, pentru Partner Integration Progress.
    """

    contact_id: UUID
    full_name: str
    status: str
    last_followup_at: Optional[datetime]
    last_followup_status: Optional[str]
    converted_to: Optional[str]
    pdi: Optional[float]
    pip: Optional[float]


def _priority_group(
    last_followup_at: Optional[datetime], last_followup_status: Optional[str]
) -> int:
    """Calculează grupul de prioritate al unui Contact.

    Regulă CONFIRMATĂ (20-contact-agent-contract.md, secțiunea 5,
    17 august 2026):
        0 = FollowUp PENDING scadent (scheduled_at <= ACUM)
        1 = fără niciun FollowUp
        2 = restul (FollowUp COMPLETED/POSTPONED/RESCHEDULED, sau
            PENDING dar programat în viitor)

    Args:
        last_followup_at: Data programată a celui mai recent FollowUp.
        last_followup_status: Starea celui mai recent FollowUp.

    Returns:
        Grupul de prioritate (0, 1 sau 2), folosit ca primă cheie de
        sortare în `ContactAgent.list_prioritized_contacts`.
    """
    if last_followup_at is None:
        return 1
    if last_followup_status == "PENDING" and last_followup_at <= datetime.now(timezone.utc):
        return 0
    return 2


class ContactAgent:
    """Agent 1 — prezintă o listă prioritizată de Contacte liderului.

    Strict read-only: citește `contacts`, `follow_ups`, `clients`,
    `partners`, `scores`+`kpis`. Nu scrie niciodată, nu calculează KPI,
    nu declanșează tranziții de stare.
    """

    def list_prioritized_contacts(self, owner_id: UUID) -> List[ContactSummary]:
        """Returnează Contactele owner_id-ului, prioritizate conform regulii confirmate.

        Args:
            owner_id: Identificatorul liderului autentificat (din
                `CurrentUser.id`, niciodată din request body/query —
                v. contract secțiunea 7).

        Returns:
            Lista de ContactSummary, excluzând Contactele ARCHIVED,
            sortată: FollowUp scadent, apoi fără FollowUp, apoi restul
            după `updated_at` descrescător.
        """
        rows = self._fetch_contacts(owner_id)
        active_rows = [row for row in rows if row[2] != "ARCHIVED"]

        has_partner_contact = any(row[5] == "partner" for row in active_rows)
        scores = self._fetch_partner_scores(owner_id) if has_partner_contact else {}

        sorted_rows = sorted(active_rows, key=self._sort_key)

        return [
            ContactSummary(
                contact_id=contact_id,
                full_name=full_name,
                status=status,
                last_followup_at=last_followup_at,
                last_followup_status=last_followup_status,
                converted_to=converted_to,
                pdi=scores.get("PDI") if converted_to == "partner" else None,
                pip=scores.get("PIP") if converted_to == "partner" else None,
            )
            for (
                contact_id,
                full_name,
                status,
                last_followup_at,
                last_followup_status,
                converted_to,
                _updated_at,
            ) in sorted_rows
        ]

    @staticmethod
    def _sort_key(row: _ContactRow) -> Tuple[int, float]:
        """Cheie de sortare pentru un rând brut de Contact.

        Args:
            row: Tuplul brut întors de `_fetch_contacts`.

        Returns:
            Tuplu `(grup, tie_break)`. `tie_break` decide ordinea doar
            în interiorul Grupului 2 (restul), sortat după `updated_at`
            descrescător — pentru Grupurile 0 și 1, secțiunea 5 din
            contract nu specifică o ordine secundară, deci `tie_break`
            rămâne `0.0` (ordinea de intrare se păstrează, sortare stabilă).
        """
        _, _, _, last_followup_at, last_followup_status, _, updated_at = row
        group = _priority_group(last_followup_at, last_followup_status)
        tie_break = -updated_at.timestamp() if group == 2 else 0.0
        return group, tie_break

    def _fetch_contacts(self, owner_id: UUID) -> List[_ContactRow]:
        """Interoghează Contactele owner_id-ului, cu ultimul FollowUp și conversia.

        Args:
            owner_id: Identificatorul liderului.

        Returns:
            Listă de tupluri brute `(contact_id, full_name, status,
            last_followup_at, last_followup_status, converted_to,
            updated_at)`. Filtrarea `ARCHIVED` e aplicată și în SQL
            (index `idx_contacts_owner_status`), dar rezultatul final
            e re-verificat explicit în Python — un singur punct de
            adevăr pentru comportamentul testat.
        """
        query = """
            SELECT
                c.id,
                c.full_name,
                c.status,
                fu.scheduled_at,
                fu.status,
                CASE
                    WHEN cl.id IS NOT NULL THEN 'client'
                    WHEN p.id IS NOT NULL THEN 'partner'
                    ELSE NULL
                END,
                c.updated_at
            FROM contacts c
            LEFT JOIN LATERAL (
                SELECT scheduled_at, status
                FROM follow_ups
                WHERE follow_ups.contact_id = c.id
                ORDER BY scheduled_at DESC
                LIMIT 1
            ) fu ON TRUE
            LEFT JOIN clients cl ON cl.contact_id = c.id
            LEFT JOIN partners p ON p.contact_id = c.id
            WHERE c.owner_id = %s
              AND c.status != 'ARCHIVED'
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id,))
                return cur.fetchall()

    def _fetch_partner_scores(self, owner_id: UUID) -> Dict[str, float]:
        """Citește cele mai recente scoruri PDI/PIP ale partenerilor owner-ului.

        READ-ONLY, același tipar ca `PartnerAgent.get_recent_scores()`.
        CRH nu apare niciodată aici — zero producători în `scores`
        (verificat în audit, contract secțiunea 2.4).

        Args:
            owner_id: Identificatorul liderului.

        Returns:
            Dict cu cel mult cheile "PDI"/"PIP" → cel mai recent
            `score_value`. Dict gol dacă nu există nicio scriere reală.
        """
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
        result: Dict[str, float] = {}
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id,))
                for metric_code, score_value in cur.fetchall():
                    result.setdefault(metric_code, score_value)
        return result
