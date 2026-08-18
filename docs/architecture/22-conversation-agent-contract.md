# `ConversationAgent v1` — CONTRACT DE IMPLEMENTARE

**Status:** verificat direct din cod (`src/engines/objection/objection_engine.py`,
`library.py`, `safety_validation.py`) — nu din memorie, nu din contractul `21`, care descrie
intenția motorului, nu semnătura exactă. Construiește pe `22-conversation-agent-interfata-
objection-engine.md` (precondiția verificată 17 august 2026) și pe `20-2A-create-objection-
contract.md` (Decizia 2A, implementată + validată pe PostgreSQL real).
**Precedent:** aceeași disciplină ca `20-2A` — fără cod înainte de contract, TDD strict.

---

## 0. Auditul semnăturilor reale (înainte de orice decizie de contract)

| Metodă `ObjectionEngine` | Semnătură verificată | DB? | Erori |
|---|---|---|---|
| `classify(objection_text: str)` | `-> Optional[str]` | **NU** — pur, fără `get_connection` | Niciuna — fără potrivire → `None` |
| `create_objection(owner_id, objection_text, objection_category, conversation_id=None)` | `-> Objection` | DA — `INSERT ... RETURNING` | `ValueError` (categorie invalidă, înainte de DB); `psycopg.errors.ForeignKeyViolation` (owner/conversation invalid, neprinsă) |
| `get_variants(category: str)` | `-> Dict[str, str]` | NU — pur, deleagă la `library.py` | `ValueError` (categorie necunoscută) |
| `submit_response(objection_id, owner_id, objection_category, objection_text, response_text, response_variant_used)` | `-> SubmitResponseResult` | DA — `UPDATE` | `ObjectionNotFoundError` (0 rânduri afectate) |

Confirmat suplimentar: `ALL_CATEGORIES` (folosit de `create_objection`) și cheile `_LIBRARY`
(folosite de `get_variants`) sunt **identice** (13/13, verificat direct) — deci dacă
`create_objection` acceptă o categorie, `get_variants` nu va eșua pentru aceeași categorie.

## 1. Controlul cerut: `submit_response()` mai are nevoie de `owner_id`/`objection_category`/`objection_text`?

**Da, toate trei rămân necesare — nu sunt date redundante.** Verificat direct din corpul metodei:

- **`owner_id`** — folosit în `WHERE id = %s AND owner_id = %s` la UPDATE. Nu e înlocuit de
  `objection_id`: e filtrul de izolare care împiedică un lider să scrie pe obiecția altui lider,
  chiar dacă ar ghici/cunoaște `objection_id`-ul. Eliminarea lui ar sparge izolarea testată în
  `test_submit_response_izoleaza_owner_id_pe_postgres`.
- **`objection_category`** — transmis direct la `validate_response(response_text,
  objection_category, objection_text)`. Safety Validation îl folosește activ (ex. regula
  specifică pentru `INCREDERE_STRUCTURA`) — nu e citit din DB, nu e doar un identificator.
- **`objection_text`** — folosit de aceeași `validate_response()` pentru regula "ocolirea
  refuzului explicit" (compară textul original cu răspunsul propus).

**Concluzie:** `ConversationAgent` **păstrează** toate trei în `confirm_response()`. Nu le preia
din DB (metoda curentă nu face `SELECT` intern de fetch), ci din `Objection` deja obținut la
pasul `prepare_response_options()` — evită round-trip suplimentar, consecvent cu designul
existent al `submit_response()`.

## 2. Limita strictă v1 (neschimbată față de `22-conversation-agent-interfata-objection-engine.md`)

`ConversationAgent` orchestrează — **nu scrie niciodată direct** în schema `objections`.
Nu citește/scrie `conversations` (v1 nu are `Conversation` writer — confirmat ABSENT prin audit).
`conversation_id` rămâne opțional, transmis pasiv, fără validare suplimentară în afara FK-ului
din PostgreSQL (deja acoperit de `create_objection`).

`resolution_status` **nu** e modificat de acest contract — nicio metodă din `ObjectionEngine`
nu-l actualizează după creare (verificat: `resolution_status` nu apare în niciun `UPDATE`
existent). Rămâne `'OPEN'` pe tot parcursul v1 — tranziția lui e explicit în afara scopului.

---

## 3. Cele trei metode

### 3.1 `analyze_objection(objection_text: str) -> AnalyzeObjectionResult`

```python
@dataclass(frozen=True)
class AnalyzeObjectionResult:
    detected_category: Optional[str]
    needs_manual_selection: bool
```

| | |
|---|---|
| DB | **NU** — deleagă direct la `ObjectionEngine.classify()`, pur |
| `needs_manual_selection` | `True` exact când `detected_category is None` — derivat, nu introdus separat |
| Erori | Niciuna — text gol/fără potrivire → `detected_category=None`, `needs_manual_selection=True` |

### 3.2 `prepare_response_options(owner_id, objection_text, objection_category, conversation_id=None) -> PrepareResponseOptionsResult`

```python
@dataclass(frozen=True)
class PrepareResponseOptionsResult:
    objection: Objection
    variants: Dict[str, str]
```

| | |
|---|---|
| DB | **DA** |
| Ordine internă | `create_objection(...)` → `get_variants(objection.objection_category)` |
| `objection_category` sursă | Rezultatul lui `analyze_objection()` (`detected_category`) SAU alegerea manuală a liderului dacă `needs_manual_selection=True` — `ConversationAgent` NU decide singur |
| Erori | `ValueError` — categorie invalidă, ridicată de `create_objection` **înainte** de orice INSERT (zero rânduri scrise dacă eșuează); `psycopg.errors.ForeignKeyViolation` — `owner_id`/`conversation_id` invalid, propagă neprinsă (consecvent cu `20-2A`) |
| De ce `get_variants` DUPĂ `create_objection`, nu înainte | Ordinea contează pentru `objection_id`: obiecția trebuie să existe în DB înainte ca liderul să poată alege o variantă și apoi confirma (`confirm_response` are nevoie de `objection_id` real). `ALL_CATEGORIES == _LIBRARY.keys()` (verificat, secțiunea 0) garantează că `get_variants` nu eșuează separat pentru o categorie deja acceptată de `create_objection`. |

### 3.3 `confirm_response(objection: Objection, response_text: str, response_variant_used: str) -> ConfirmResponseResult`

**Semnătură revizuită față de varianta inițială (4 câmpuri separate)** — motiv: `ObjectionEngine`
nu are nicio metodă de citire (`get_objection(id)`); `owner_id`/`objection_category`/
`objection_text` nu pot veni decât din `Objection`-ul deja obținut la pasul `3.2`, nu din input
nou al liderului. UI-ul transmite efectiv doar decizia liderului (`response_text`,
`response_variant_used`) — `objection_id` e deja parte din `objection.id`, păstrat de apelant
între cei doi pași (`prepare_response_options()` → `confirm_response()`), nu retrimis separat.

```python
@dataclass(frozen=True)
class ConfirmResponseResult:
    persisted: bool
    validation_level: str  # "PASS" | "BLOCK" | "PARTIAL_VALIDATION" | "HUMAN_REVIEW"
    reason: Optional[str]
```

| | |
|---|---|
| DB | **DA** — deleagă direct la `ObjectionEngine.submit_response()` |
| `objection_id`, `owner_id`, `objection_category`, `objection_text` sursă | Toate extrase din `objection` (parametrul), niciunul reintrodus de UI/lider |
| `response_text`/`response_variant_used` sursă | Alese/editate de lider din `variants` (pasul 3.2) — `response_variant_used` e cheia ALEASĂ INIȚIAL, neschimbată dacă liderul editează `response_text` (regulă Decizia 3, `21`, secțiunea 4) |
| Erori | `ObjectionNotFoundError` — propagă neprinsă din `ObjectionEngine.submit_response()`; contractul `ConversationAgent` nu o traduce |
| `validation_level`/`reason` | Extrase din `SubmitResponseResult.validation` (`ValidationResult.level`, `.reason`) — `ConversationAgent` nu reinterpretează nivelurile, doar le expune |

---

## 4. Fluxul complet, cu tipurile exacte

```python
# 1.
result1 = agent.analyze_objection(objection_text)
# AnalyzeObjectionResult(detected_category=..., needs_manual_selection=...)

# 2. daca needs_manual_selection -> liderul alege din cele 13 (ALL_CATEGORIES)
category = result1.detected_category or lider_alege_din_cele_13()

# 3.
result2 = agent.prepare_response_options(
    owner_id=current_user.id, objection_text=objection_text,
    objection_category=category, conversation_id=conversation_id,
)
# PrepareResponseOptionsResult(objection=Objection(...), variants={"CALDA": ..., ...})

# 4. liderul alege + editeaza optional
chosen_key = "..."  # "CALDA" | "DIRECTA" | "INTREBARE"
final_text = result2.variants[chosen_key]  # posibil editat de lider

# 5.
result3 = agent.confirm_response(
    objection=result2.objection,
    response_text=final_text,
    response_variant_used=chosen_key,
)
# ConfirmResponseResult(persisted=..., validation_level=..., reason=...)
```

---

## 5. Ce rămâne explicit NEDEFINIT (viitoare decizii, nu presupuse aici)

- **Cine expune lista celor 13 categorii** pentru selecția manuală a liderului când
  `needs_manual_selection=True` — `ALL_CATEGORIES` există în `library.py`, dar nu e reexportat
  încă printr-o metodă publică a `ObjectionEngine`. Decizie separată dacă va fi nevoie.
- **`VULNERABILITATE_IZOLARE` — gate suplimentar** (contract `21`, secțiunea 2.3): `get_variants`
  nu face acest gate singur. `ConversationAgent v1` moștenește aceeași responsabilitate
  nerezolvată — rămâne în afara scopului până la o decizie explicită de confirmare UI.
  `prepare_response_options()` NU implementează acest gate în v1.
- **API/router HTTP** pentru `ConversationAgent` — out of scope, la fel ca la toate agenții
  existenți înainte de expunerea lor prin API (`PriorityEngine` are aceeași situație).
