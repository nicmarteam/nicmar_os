"""
PartnerEngine — motorul de relație cu partenerii pentru NicMar OS.

Sursă: PARTNER-VERTICAL-SLICE-CONTRACT v1, secțiunile 1.3-1.6.

Lanț implementat:
    RuleEngine → PARTNER_READY/ALREADY_DIAGNOSED → PartnerEngine →
    diagnostic (4 variante fixe) → mesaj (STUB) → confirmare →
    PDI/PIP → scores

Cod motor: ENG-PRE-001 — plauzibil, nu confirmat (aceeași categorie de
dovadă ca ENG-MISSION-001, corectat azi în mission_engine.py — apare
doar ca exemplu în 03-rule-model-001.md).

Decizii de design, verificate din sursă (nu presupuse prin analogie):
- Fără tabel nou pentru "diagnostic deja generat azi" — se reutilizează
  `events` (generic), verificat de RuleEngine.has_diagnostic_today().
- `PDI`/`PIP` se persistă la FINALIZAREA completă a interacțiunii
  (după confirmarea mesajului, Ecranul 8 din 05), NU la generarea
  diagnosticului — diferit de FollowUp (persistat la creare).
- Generarea mesajului e STUB — text fix, fără apel AI real. Contractul
  scoate explicit generarea de conținut din scope-ul v1.
- Tipul de diagnostic (care din cele 4) NU e calculat aici — formula
  de selecție nu există în nicio sursă. Se primește ca parametru
  explicit, ales de apelant (Agent), nu inventat de motor.

Reguli de design (identice cu Mission/FollowUp):
- Confirmarea umană e parametru explicit (`confirmed: bool`).
- Nicio conexiune proprie la DB — totul trece prin
  src.data.db.get_connection().

Nu implementate (out of scope v1):
- PriorityEngine (selecția partenerului cu cea mai mare nevoie —
  rămâne capability la nivel de Agent, ca la Partner Agent din
  06-harta-motoare-tehnice.md, Decizia P11)
- AMS, LRI (Nic a confirmat explicit doar PDI+PIP pentru acest slice)
- Generare reală de mesaj (necesită integrare LLM)
"""

from dataclasses import dataclass
from uuid import UUID

from src.data.db import get_connection
from src.engines.rule.rule_engine import RuleEngine

# Plauzibil, nu confirmat — v. docstring modul.
ENGINE_CODE = "ENG-PRE-001"

# Cele 4 variante fixe, exact din 05 (Competența 27, Ecranul 3) —
# nu se adaugă altele, nu se inventează o a 5-a categorie.
VALID_DIAGNOSTIC_TYPES = ("ENCOURAGEMENT", "CLARITY", "APPRECIATION", "NEXT_STEP")

_STUB_MESSAGES = {
    "ENCOURAGEMENT": "[STUB] Mesaj de încurajare — necesită integrare LLM reală.",
    "CLARITY": "[STUB] Mesaj de claritate — necesită integrare LLM reală.",
    "APPRECIATION": "[STUB] Mesaj de apreciere — necesită integrare LLM reală.",
    "NEXT_STEP": "[STUB] Mesaj despre pasul următor — necesită integrare LLM reală.",
}


class PartnerDiagnosticAlreadyGeneratedError(Exception):
    """Ridicată când RuleEngine returnează PARTNER_ALREADY_DIAGNOSED."""


class InvalidDiagnosticTypeError(Exception):
    """Ridicată dacă diagnostic_type nu e una din cele 4 variante fixe."""


class HumanConfirmationRequiredError(Exception):
    """Ridicată dacă se încearcă finalizarea fără confirmare umană explicită."""


@dataclass(frozen=True)
class PartnerDiagnostic:
    """Diagnosticul generat pentru un partener, cu mesajul (stub) asociat."""
    partner_id: UUID
    owner_id: UUID
    diagnostic_type: str
    message: str


class PartnerEngine:
    """
    Motorul de relație cu partenerii — State Owner pentru Partner
    (02-business-objects-5-pillars.md, linia 909).

    Depinde explicit de RuleEngine (injectat) — nu decide singur dacă
    un diagnostic poate fi generat, doar execută decizia RuleEngine-ului.
    """

    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine

    # ------------------------------------------------------------------
    # Diagnostic — trece prin RuleEngine, tip ales de apelant
    # ------------------------------------------------------------------

    def generate_diagnostic(
        self, partner_id: UUID, owner_id: UUID, diagnostic_type: str
    ) -> PartnerDiagnostic:
        """
        Generează un diagnostic + mesaj (STUB), DOAR dacă RuleEngine
        confirmă PARTNER_READY (partenerul n-a primit deja unul azi).

        `diagnostic_type` trebuie să fie unul din VALID_DIAGNOSTIC_TYPES
        — motorul nu alege singur tipul (nicio formulă de selecție nu
        există în sursă).
        """
        if diagnostic_type not in VALID_DIAGNOSTIC_TYPES:
            raise InvalidDiagnosticTypeError(
                f"diagnostic_type invalid: {diagnostic_type}. "
                f"Valide: {VALID_DIAGNOSTIC_TYPES}"
            )

        rule_result = self.rule_engine.evaluate_partner_diagnostic(partner_id)
        if rule_result.decision_outcome != "PARTNER_READY":
            raise PartnerDiagnosticAlreadyGeneratedError(
                f"partner_id={partner_id} a primit deja un diagnostic azi — "
                f"PartnerEngine nu generează unul nou."
            )

        message = _STUB_MESSAGES[diagnostic_type]
        self._emit_event(
            "PartnerDiagnosticGenerated", partner_id,
            {"owner_id": str(owner_id), "diagnostic_type": diagnostic_type},
        )
        return PartnerDiagnostic(
            partner_id=partner_id, owner_id=owner_id,
            diagnostic_type=diagnostic_type, message=message,
        )

    # ------------------------------------------------------------------
    # Finalizare — confirmare umană obligatorie, apoi KPI
    # ------------------------------------------------------------------

    def confirm_and_complete(
        self, partner_id: UUID, owner_id: UUID, confirmed: bool
    ) -> None:
        """
        Finalizează interacțiunea — liderul a confirmat mesajul și l-a
        "trimis" (Ecranul 6-7 din 05). Persistă PDI + PIP DOAR aici,
        nu la generarea diagnosticului (verificat din sursă, Ecranul 8:
        "Se recalculează automat PDI" — după trimitere, nu înainte).

        `confirmed` fără valoare implicită — motorul refuză activ
        fără ea, identic cu Mission/FollowUp.
        """
        if not confirmed:
            raise HumanConfirmationRequiredError(
                "Finalizarea interacțiunii necesită confirmare umană "
                "explicită (confirmed=True)."
            )

        self._record_pdi_pip_scores(partner_id, owner_id)
        self._emit_event(
            "PartnerInteractionCompleted", partner_id, {"owner_id": str(owner_id)}
        )

    # ------------------------------------------------------------------
    # KPI — PDI + PIP, prin infrastructura kpis + scores
    # ------------------------------------------------------------------

    def _record_pdi_pip_scores(self, partner_id: UUID, owner_id: UUID) -> None:
        """
        Persistă scoruri PDI și PIP pentru interacțiunea finalizată.

        ATENȚIE: score_value = 1.0 e PLACEHOLDER pentru ambele — formula
        reală rămâne nedefinită în KPI-MODEL-001. Doar PDI+PIP (Nic a
        confirmat explicit) — nu AMS, nu LRI.
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                for metric_code in ("PDI", "PIP"):
                    cur.execute(
                        "SELECT id FROM kpis WHERE metric_code = %s", (metric_code,)
                    )
                    row = cur.fetchone()
                    if row is None:
                        raise RuntimeError(
                            f"KPI '{metric_code}' nu există în tabelul kpis — "
                            f"trebuie seed-uit cu cei 13 KPI din 04-KPI-REG-001.md."
                        )
                    kpi_id = row[0]

                    cur.execute(
                        "INSERT INTO scores "
                        "(kpi_id, entity_type, entity_id, score_value, engine_source) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (kpi_id, "partner", partner_id, 1.0, ENGINE_CODE),
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
                    (event_name, "partner", target_object_id, Json(payload)),
                )
