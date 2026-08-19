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
from typing import Dict, List, Optional
from uuid import UUID

from src.data.db import get_connection
from src.engines.objection.classifier import classify_objection
from src.engines.objection.library import ALL_CATEGORIES, get_variants as _get_variants
from src.engines.objection.safety_validation import ValidationResult, validate_response


class ObjectionNotFoundError(Exception):
    """Ridicată când `objection_id` nu există sau nu aparține `owner_id`.

    Eroare explicită (contract secțiunea 6) — niciodată eșec silențios
    când 0 rânduri sunt afectate de UPDATE.
    """


@dataclass(frozen=True)
class Objection:
    """Reprezentarea unei obiecții, așa cum e citită din `objections`.

    Sursă: `20-2A-create-objection-contract.md`, secțiunea 2. Toate
    câmpurile provin direct din `RETURNING` la INSERT — nu sunt
    presupuse local.

    Attributes:
        id: Identificatorul generat de PostgreSQL (`gen_random_uuid()`).
        owner_id: Liderul care deține obiecția.
        conversation_id: Conversația asociată, sau `None` (coloană nullable).
        objection_category: Una din cele 13 categorii oficiale (`ALL_CATEGORIES`).
        objection_text: Textul liber, neschimbat, al obiecției.
        resolution_status: Starea obiecției — `'OPEN'` la creare (`DEFAULT` DB).
    """

    id: UUID
    owner_id: UUID
    conversation_id: Optional[UUID]
    objection_category: str
    objection_text: str
    resolution_status: str


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

    def list_categories(self) -> List[str]:
        """Listează toate cele 13 categorii oficiale (Decizia 6, `23-list-categories-contract.md`).

        Pentru selecția manuală a liderului, când `classify()` returnează
        `None` (fără potrivire deterministă). Pur — nu atinge DB.

        Returns:
            Listă cu cele 13 categorii din `ALL_CATEGORIES`, sortate
            alfabetic (decizie explicită pentru afișare deterministă —
            `frozenset`-ul sursă nu garantează ordine).
        """
        return sorted(ALL_CATEGORIES)

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

    def create_objection(
        self,
        owner_id: UUID,
        objection_text: str,
        objection_category: str,
        conversation_id: Optional[UUID] = None,
    ) -> Objection:
        """Creează o obiecție nouă (Decizia 2A, `20-2A-create-objection-contract.md`).

        `ObjectionEngine` este proprietarul complet al ciclului de viață
        `objections` — `ConversationAgent` nu scrie niciodată direct în
        această schemă, doar orchestrează apelul acestei metode.

        Nu verifică duplicate: aceeași obiecție (owner + categorie + text)
        poate apărea de mai multe ori în aceeași conversație — sunt
        evenimente reale distincte, nu duplicate artificiale (contract
        secțiunea 5).

        Args:
            owner_id: Identificatorul liderului autentificat — din
                `CurrentUser.id` (JWT), niciodată din input liber.
            objection_text: Textul liber al obiecției, neschimbat.
            objection_category: Categoria obiecției — una din cele 13
                oficiale (`ALL_CATEGORIES`, `library.py`).
            conversation_id: Conversația asociată, opțional — coloana
                `objections.conversation_id` e nullable.

        Returns:
            `Objection` complet, construit exact din valorile `RETURNING`
            ale INSERT-ului — inclusiv `id` generat de PostgreSQL și
            `resolution_status` aplicat din `DEFAULT 'OPEN'` al coloanei.

        Raises:
            ValueError: `objection_category` nu e una din cele 13
                oficiale — verificat ÎNAINTE de orice conexiune DB.
            psycopg.errors.ForeignKeyViolation: `owner_id` sau
                `conversation_id` nu există — propagă neprinsă,
                consecvent cu restul engine-urilor din repo (niciunul
                nu traduce FK violation într-o eroare de domeniu).
        """
        if objection_category not in ALL_CATEGORIES:
            raise ValueError(f"Categorie necunoscută: {objection_category!r}")

        query = """
            INSERT INTO objections (owner_id, conversation_id, objection_category, objection_text)
            VALUES (%s, %s, %s, %s)
            RETURNING id, owner_id, conversation_id, objection_category,
                      objection_text, resolution_status
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (owner_id, conversation_id, objection_category, objection_text))
                row = cur.fetchone()

        objection = Objection(
            id=row[0],
            owner_id=row[1],
            conversation_id=row[2],
            objection_category=row[3],
            objection_text=row[4],
            resolution_status=row[5],
        )
        self._emit_event("ObjectionCreated", objection.id, {"owner_id": str(owner_id)})
        return objection

    def get_objection(self, objection_id: UUID, owner_id: UUID) -> Objection:
        """Citește o obiecție existentă (Decizia 8A, `25-get-objection-contract.md`).

        Precondiție pentru API-ul HTTP: HTTP e stateless între `/prepare` și
        `/confirm` — `ConversationAgent.confirm_response()` re-citește
        `Objection` prin această metodă, folosind `owner_id` din JWT, NICIODATĂ
        din client. Previne exact vulnerabilitatea identificată în audit: un
        client ar putea trimite o `objection_category` falsă, ca să ocolească
        o regulă mai strictă de Safety Validation.

        Args:
            objection_id: Identificatorul rândului `objections` de citit.
            owner_id: Identificatorul liderului autentificat — filtrare
                obligatorie în `WHERE`, la fel ca `submit_response`. Existența
                `objection_id` singură NU acordă acces.

        Returns:
            `Objection` complet, construit din valorile citite.

        Raises:
            ObjectionNotFoundError: rândul nu există SAU aparține altui
                `owner_id` — reutilizează excepția existentă (folosită și de
                `submit_response`), nu introduce una nouă pentru același tip
                de eșec. Mesaj identic pentru ambele cazuri — previne
                enumerare de ID-uri.
        """
        query = """
            SELECT id, owner_id, conversation_id, objection_category,
                   objection_text, resolution_status
            FROM objections
            WHERE id = %s AND owner_id = %s
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (objection_id, owner_id))
                row = cur.fetchone()

        if row is None:
            raise ObjectionNotFoundError(
                f"Obiecția {objection_id} nu există sau nu aparține owner-ului {owner_id}."
            )

        return Objection(
            id=row[0], owner_id=row[1], conversation_id=row[2],
            objection_category=row[3], objection_text=row[4], resolution_status=row[5],
        )

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
            self._emit_event("ObjectionResponseSubmitted", objection_id, {
                "owner_id": str(owner_id),
                "validation_level": validation.level,
                "persisted": False,
            })
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

        self._emit_event("ObjectionResponseSubmitted", objection_id, {
            "owner_id": str(owner_id),
            "validation_level": validation.level,
            "persisted": True,
        })
        return SubmitResponseResult(persisted=True, validation=validation)

    def _emit_event(self, event_name: str, target_object_id: UUID, payload: dict) -> None:
        """Scrie evenimentul în tabelul generic `events` (pattern identic cu celelalte 5 engine-uri)."""
        from psycopg.types.json import Json

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO events (event_name, target_object, target_object_id, payload) "
                    "VALUES (%s, %s, %s, %s)",
                    (event_name, "objection", target_object_id, Json(payload)),
                )
