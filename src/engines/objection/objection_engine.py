"""
ObjectionEngine — motor MVP confirmat (Decizia 2, `06-harta-motoare-tehnice.md`).

Sursă: `21-objection-engine-contract.md` (consolidează Deciziile 1-5,
`21-objection-engine-decizii-preliminare.md`, 17 august 2026).

Regulă arhitecturală centrală: `ObjectionEngine` e singurul loc care
scrie în `objections.response_text`/`response_variant_used` — la fel
cum `PartnerEngine` e singurul care scrie în `partners`/`scores`.

Nu implementat (out of scope v1, contract secțiunea 6 și 8):
- Generare de text liber (fără LLM, Decizia 1)
- Verificare generală de adevăr (doar listă cunoscută, Decizia 4)
- Istoric de conversație (doar `objection_text` curent, Decizia 4)
- Adăugare automată a disclaimer-ului de venituri (doar verificare,
  Decizia 5 — regulă Human-in-the-loop explicită)
"""

from dataclasses import dataclass
from typing import Dict, Optional
from uuid import UUID

from src.data.db import get_connection
from src.engines.objection.classifier import classify_objection
from src.engines.objection.library import get_variants as _get_variants
from src.engines.objection.safety_validation import ValidationResult, validate_response


class ObjectionNotFoundError(Exception):
    """Ridicată când `objection_id` nu există sau nu aparține `owner_id`.

    Eroare explicită (contract secțiunea 6) — niciodată eșec silențios
    când 0 rânduri sunt afectate de UPDATE.
    """


@dataclass(frozen=True)
class SubmitResponseResult:
    """Rezultatul unei încercări de a trimite/persista un răspuns.

    Attributes:
        persisted: True dacă răspunsul a fost scris în DB. False dacă
            `validation.level == "BLOCK"` — nimic nu se scrie.
        validation: Rezultatul complet al Safety Validation, indiferent
            dacă a permis sau nu persistarea.
    """

    persisted: bool
    validation: ValidationResult


class ObjectionEngine:
    """Motorul `ObjectionEngine` v1 — clasificare, bibliotecă, validare, persistare.

    Strict scope v1 (Decizia 1): `Objection → Biblioteca Experienței →
    răspuns`, fără `RelationshipEngine`/`Motorul Identității`/
    `CustomerRelationshipEngine`/`PartnerRelationshipEngine`.
    """

    def classify(self, objection_text: str) -> Optional[str]:
        """Clasifică determinist o obiecție (Decizia 2).

        Args:
            objection_text: Textul liber al obiecției.

        Returns:
            Una din cele 6 categorii eligibile automat, sau `None` dacă
            nu există potrivire — niciodată o ghicire.
        """
        return classify_objection(objection_text)

    def get_variants(self, category: str) -> Dict[str, str]:
        """Returnează cele 3 variante de răspuns pentru o categorie (Decizia 3).

        Args:
            category: Codul categoriei (una din cele 13 oficiale).

        Returns:
            Dict cu cheile "CALDA", "DIRECTA", "INTREBARE".

        Raises:
            ValueError: categorie necunoscută (v. `library.get_variants`).
        """
        return _get_variants(category)

    def submit_response(
        self,
        objection_id: UUID,
        owner_id: UUID,
        objection_category: str,
        objection_text: str,
        response_text: str,
        response_variant_used: str,
    ) -> SubmitResponseResult:
        """Validează și, dacă e permis, persistă răspunsul final al liderului.

        Rulează Safety Validation (Decizia 4 + Decizia 5) pe
        `response_text`. Dacă rezultatul e `BLOCK`, nu scrie nimic în
        DB. Altfel (`PASS`, `PARTIAL_VALIDATION`, `HUMAN_REVIEW`),
        persistă — aceste niveluri semnalează, nu blochează.

        `response_variant_used` se persistă exact cum a fost transmis
        — motorul NU îl recalculează la editare (regulă Decizia 3:
        păstrează varianta de ORIGINE, chiar dacă `response_text` a
        fost modificat de lider).

        Args:
            objection_id: Identificatorul rândului `objections` de actualizat.
            owner_id: Identificatorul liderului autentificat — filtrare
                obligatorie în `WHERE`, niciodată doar din `objection_id`.
            objection_category: Categoria obiecției (folosită de Safety
                Validation, ex. verificarea specifică `INCREDERE_STRUCTURA`).
            objection_text: Textul original al obiecției (folosit pentru
                regula "ocolirea refuzului explicit").
            response_text: Textul final al răspunsului, posibil editat.
            response_variant_used: Varianta de origine ("CALDA"/"DIRECTA"/
                "INTREBARE") — neschimbată de editare.

        Returns:
            `SubmitResponseResult` cu `persisted` și `validation`.

        Raises:
            ObjectionNotFoundError: `objection_id` nu există sau nu
                aparține `owner_id` — 0 rânduri afectate de UPDATE.
        """
        validation = validate_response(response_text, objection_category, objection_text)

        if validation.level == "BLOCK":
            return SubmitResponseResult(persisted=False, validation=validation)

        query = """
            UPDATE objections
            SET response_text = %s,
                response_variant_used = %s,
                updated_at = clock_timestamp()
            WHERE id = %s AND owner_id = %s
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (response_text, response_variant_used, objection_id, owner_id))
                if cur.rowcount == 0:
                    raise ObjectionNotFoundError(
                        f"Obiecția {objection_id} nu există sau nu aparține owner-ului {owner_id}."
                    )

        return SubmitResponseResult(persisted=True, validation=validation)
