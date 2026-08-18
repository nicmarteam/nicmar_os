"""
ConversationAgent v1 — orchestrator pentru fluxul complet al unei obiecții.

Sursă: `22-conversation-agent-contract.md`, verificat direct din semnăturile
reale ale `ObjectionEngine` (`classify`, `create_objection`, `get_variants`,
`submit_response`) — nu din memorie.

Regulă arhitecturală centrală (identică cu FollowUpAgent/MissionAgent):
`ConversationAgent` NU devine al doilea `ObjectionEngine`. Nu duplică
clasificarea, Biblioteca Experienței sau Safety Validation, nu scrie SQL
pentru `objections` — orice operație de domeniu trece exclusiv prin
`ObjectionEngine`. `ConversationAgent` doar leagă cele trei puncte de
intervenție umană (analiză → variante → confirmare), fără să le comprime
într-un singur apel care ar trimite un răspuns automat, fără control.

Nu implementate (out of scope v1, contract secțiunea 5):
- Selecția manuală dintre cele 13 categorii (`needs_manual_selection=True`)
  — expunerea listei `ALL_CATEGORIES` printr-o metodă publică rămâne o
  decizie separată, neluată încă.
- Gate-ul suplimentar pentru `VULNERABILITATE_IZOLARE` (contract `21`,
  secțiunea 2.3) — `get_variants()` nu-l face singur, iar
  `prepare_response_options()` nu-l implementează în v1.
- Orice tranziție a `resolution_status` — nicio metodă din `ObjectionEngine`
  nu-l actualizează după creare; `ConversationAgent` nu inventează o regulă
  nouă doar pentru că există coloana.
- API/router HTTP.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import UUID

from src.engines.objection.objection_engine import Objection, ObjectionEngine


@dataclass(frozen=True)
class AnalyzeObjectionResult:
    """Rezultatul analizei unei obiecții — fără nicio scriere în DB.

    Attributes:
        detected_category: Categoria deterministă găsită de
            `ObjectionEngine.classify()`, sau `None` dacă nu există
            potrivire.
        needs_manual_selection: `True` exact când `detected_category`
            e `None` — liderul trebuie să aleagă manual din cele 13
            categorii oficiale.
    """

    detected_category: Optional[str]
    needs_manual_selection: bool


@dataclass(frozen=True)
class PrepareResponseOptionsResult:
    """Rezultatul pregătirii variantelor de răspuns pentru o obiecție nou creată.

    Attributes:
        objection: `Objection` complet, persistat de `create_objection()`
            — conține `id`-ul necesar pasului `confirm_response()`.
        variants: Dict cu cheile `"CALDA"`, `"DIRECTA"`, `"INTREBARE"`,
            din Biblioteca Experienței, pentru categoria obiecției.
    """

    objection: Objection
    variants: Dict[str, str]


@dataclass(frozen=True)
class ConfirmResponseResult:
    """Rezultatul confirmării finale a liderului, după validarea de siguranță.

    Attributes:
        persisted: `True` dacă răspunsul a fost scris în DB. `False`
            dacă `validation_level == "BLOCK"`.
        validation_level: Unul din `"PASS"`, `"BLOCK"`,
            `"PARTIAL_VALIDATION"`, `"HUMAN_REVIEW"`.
        reason: Explicație scurtă, dacă `validation_level != "PASS"`.
    """

    persisted: bool
    validation_level: str
    reason: Optional[str]


class ConversationAgent:
    """
    Orchestrator pentru fluxul `Objection → Biblioteca Experienței →
    răspuns`, cu trei puncte distincte de intervenție umană: analiză,
    alegere/editare variantă, confirmare finală. Nu deține nicio logică
    de domeniu proprie — deleagă integral la `ObjectionEngine`.
    """

    def __init__(self, objection_engine: ObjectionEngine):
        self.objection_engine = objection_engine

    # ------------------------------------------------------------------
    # Pasul 0 — Selecție manuală, fără DB (Decizia 6)
    # ------------------------------------------------------------------

    def list_categories(self) -> List[str]:
        """Listează cele 13 categorii oficiale, pentru selecția manuală a liderului.

        Folosit când `analyze_objection()` returnează `needs_manual_selection=True`.
        Deleagă integral la `ObjectionEngine.list_categories()` — nu importă
        `ALL_CATEGORIES` direct din `library.py` (contract `23`, secțiunea 0:
        `API → Agent → Engine → Library`, niciodată `API → Library`).

        Returns:
            Listă cu cele 13 categorii, sortate alfabetic.
        """
        return self.objection_engine.list_categories()

    # ------------------------------------------------------------------
    # Pasul 1 — Analiză, fără DB
    # ------------------------------------------------------------------

    def analyze_objection(self, objection_text: str) -> AnalyzeObjectionResult:
        """Clasifică determinist textul obiecției, fără nicio scriere.

        Deleagă integral la `ObjectionEngine.classify()` — nu reimplementează
        clasificarea aici.

        Args:
            objection_text: Textul liber al obiecției.

        Returns:
            `AnalyzeObjectionResult` cu categoria găsită (sau `None`) și
            `needs_manual_selection` derivat direct din aceasta.
        """
        detected_category = self.objection_engine.classify(objection_text)
        return AnalyzeObjectionResult(
            detected_category=detected_category,
            needs_manual_selection=detected_category is None,
        )

    # ------------------------------------------------------------------
    # Pasul 2 — Creare + variante, cu DB
    # ------------------------------------------------------------------

    def prepare_response_options(
        self,
        owner_id: UUID,
        objection_text: str,
        objection_category: str,
        conversation_id: Optional[UUID] = None,
    ) -> PrepareResponseOptionsResult:
        """Creează obiecția și pregătește cele 3 variante de răspuns.

        Ordine obligatorie: `create_objection()` întâi (persistă rândul,
        obține `objection.id` real), apoi `get_variants()` cu categoria
        din `Objection`-ul returnat — nu cu `objection_category` primit
        ca parametru, ca să rămână consecvent cu ce s-a scris efectiv în DB.

        Args:
            owner_id: Liderul autentificat — din `CurrentUser.id` (JWT).
            objection_text: Textul liber al obiecției.
            objection_category: Categoria — din `AnalyzeObjectionResult`
                (pasul 1) sau alegerea manuală a liderului.
            conversation_id: Conversația asociată, opțional.

        Returns:
            `PrepareResponseOptionsResult` cu `Objection`-ul complet și
            cele 3 variante.

        Raises:
            ValueError: categorie invalidă — propagată neprinsă din
                `create_objection()`.
            psycopg.errors.ForeignKeyViolation: `owner_id`/`conversation_id`
                invalid — propagată neprinsă, consecvent cu `20-2A`.
        """
        objection = self.objection_engine.create_objection(
            owner_id=owner_id,
            objection_text=objection_text,
            objection_category=objection_category,
            conversation_id=conversation_id,
        )
        variants = self.objection_engine.get_variants(objection.objection_category)
        return PrepareResponseOptionsResult(objection=objection, variants=variants)

    # ------------------------------------------------------------------
    # Pasul 3 — Confirmare finală, cu DB
    # ------------------------------------------------------------------

    def confirm_response(
        self,
        objection: Objection,
        response_text: str,
        response_variant_used: str,
    ) -> ConfirmResponseResult:
        """Confirmă și persistă răspunsul final ales/editat de lider.

        `objection_id`, `owner_id`, `objection_category`, `objection_text`
        vin EXCLUSIV din `objection` (obiectul persistent obținut la pasul
        `prepare_response_options()`) — nu sunt reintroduse ca input separat
        de UI/lider, evitând inconsecvența între ce s-a clasificat/persistat
        și ce se validează acum.

        Args:
            objection: `Objection`-ul complet, așa cum a fost returnat de
                `prepare_response_options()`.
            response_text: Textul final al răspunsului, ales sau editat
                de lider din `variants`.
            response_variant_used: Cheia variantei ALESE INIȚIAL
                (`"CALDA"`/`"DIRECTA"`/`"INTREBARE"`) — neschimbată chiar
                dacă `response_text` a fost editat.

        Returns:
            `ConfirmResponseResult` cu `persisted`, `validation_level` și
            `reason`, extrase direct din `SubmitResponseResult`.

        Raises:
            ObjectionNotFoundError: propagată neprinsă din
                `ObjectionEngine.submit_response()` — `ConversationAgent`
                nu o traduce.
        """
        result = self.objection_engine.submit_response(
            objection_id=objection.id,
            owner_id=objection.owner_id,
            objection_category=objection.objection_category,
            objection_text=objection.objection_text,
            response_text=response_text,
            response_variant_used=response_variant_used,
        )
        return ConfirmResponseResult(
            persisted=result.persisted,
            validation_level=result.validation.level,
            reason=result.validation.reason,
        )
