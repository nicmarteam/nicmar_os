# Contract de interfață — `ConversationAgent` ↔ `ObjectionEngine`

**Status:** precondiție pentru Decizia 2 (`ConversationAgent`), cerută explicit de owner, 17 august 2026.
**Verificat direct din cod** (`src/engines/objection/objection_engine.py`, `library.py`, `safety_validation.py`) — nu din memorie, nu din contractul `21`, care descrie intenția, nu semnătura exactă.

---

## 1. `ObjectionEngine.classify(objection_text: str) -> Optional[str]`

| | |
|---|---|
| **Input** | `objection_text: str` — textul liber al obiecției |
| **Output** | `str` (una din cele 6: `PRET`, `TIMP`, `INCREDERE_STRUCTURA`, `FAMILIE_SUPORT`, `AMANARE`, `FRICA_TEHNOLOGIE`) sau `None` |
| **Erori** | Niciuna — text gol/fără potrivire → `None`, nu excepție |
| **`None` înseamnă** | Fără potrivire deterministă. `ConversationAgent` TREBUIE să ofere liderului lista completă a celor 13 categorii pentru selecție manuală (contract `21`, secțiunea 2.2) — nu poate presupune o categorie |

---

## 2. `ObjectionEngine.get_variants(category: str) -> Dict[str, str]`

| | |
|---|---|
| **Input** | `category: str` — una din cele 13 categorii oficiale |
| **Output** | `Dict[str, str]` cu exact cheile `"CALDA"`, `"DIRECTA"`, `"INTREBARE"` |
| **Erori** | `ValueError("Categorie necunoscută: {category!r}")` — pentru orice categorie în afara celor 13, inclusiv `NEINCREDERE_PRODUS` |
| **Responsabilitate `ConversationAgent`** | Trebuie să prindă `ValueError` dacă permite input liber de categorie (ex. din UI) — nu trebuie să lase excepția să propage necontrolat către lider |
| **`VULNERABILITATE_IZOLARE`** | `get_variants` NU face singur gate-ul suplimentar (contract `21`, secțiunea 2.3) — **`ConversationAgent` e responsabil să ceară confirmarea explicită înainte de a apela `get_variants` cu această categorie**, sau să o semnaleze vizibil liderului după |

---

## 3. `ObjectionEngine.submit_response(...) -> SubmitResponseResult`

### Semnătură exactă
```python
def submit_response(
    self,
    objection_id: UUID,
    owner_id: UUID,
    objection_category: str,
    objection_text: str,
    response_text: str,
    response_variant_used: str,
) -> SubmitResponseResult
```

### Inputuri — cine le furnizează

| Parametru | Sursă (responsabilitatea `ConversationAgent`) |
|---|---|
| `objection_id` | Trebuie să existe deja un rând `objections` — `ConversationAgent` NU îl creează (out of scope, v. mai jos secțiunea 5) |
| `owner_id` | Din `CurrentUser.id` (JWT), niciodată din input liber — identic tiparul `ContactAgent`/`PartnerAgent` |
| `objection_category` | Rezultatul lui `classify()` SAU alegerea manuală a liderului |
| `objection_text` | Textul original, neschimbat — folosit de Safety Validation pentru regula "ocolire refuz explicit" |
| `response_text` | Varianta aleasă din `get_variants()`, posibil editată de lider |
| `response_variant_used` | Cheia variantei ALESE INIȚIAL (`"CALDA"`/`"DIRECTA"`/`"INTREBARE"`) — **rămâne neschimbată chiar dacă liderul editează `response_text`** (regulă Decizia 3, contract `21` secțiunea 4) |

### Output
```python
@dataclass(frozen=True)
class SubmitResponseResult:
    persisted: bool
    validation: ValidationResult  # level: PASS/BLOCK/PARTIAL_VALIDATION/HUMAN_REVIEW, reason: Optional[str]
```

### Comportament exact per nivel de validare

| `validation.level` | `persisted` | Ce trebuie să facă `ConversationAgent` |
|---|---|---|
| `PASS` | `True` | Confirmă succesul liderului, fără mesaj suplimentar |
| `BLOCK` | `False` | **Nimic nu s-a scris.** `ConversationAgent` trebuie să arate liderului `validation.reason` și să-i ceară să editeze din nou `response_text` — apoi să apeleze `submit_response` din nou |
| `PARTIAL_VALIDATION` | `True` | S-a scris, DAR `ConversationAgent` trebuie să semnaleze liderului `validation.reason` ca avertisment, nu ca blocaj — decizia finală de a trimite efectiv mesajul (în afara acestui contract, canal extern) rămâne a liderului |
| `HUMAN_REVIEW` | `True` | Identic cu `PARTIAL_VALIDATION` — semnalare, nu blocaj |

### Erori

| Excepție | Când | Ce face `ConversationAgent` |
|---|---|---|
| `ObjectionNotFoundError` | `objection_id` nu există SAU nu aparține `owner_id` | Trebuie prinsă explicit — nu lăsată să propage ca eroare 500 necontrolată către lider. Mesaj clar: obiecția nu a fost găsită sau nu-i aparține |

---

## 4. Fluxul complet, cu tipurile exacte la fiecare pas

```python
# 1. ConversationAgent primește textul obiecției (din UI/canal)
objection_text: str = "..."

# 2. Clasificare
category: Optional[str] = objection_engine.classify(objection_text)
# Dacă None -> ConversationAgent cere liderului să aleagă manual din cele 13

# 3. Variante
try:
    variants: Dict[str, str] = objection_engine.get_variants(category)
except ValueError:
    # categorie invalidă transmisă - ConversationAgent trebuie sa previna asta
    # la sursă (listă fixă de 13 în UI), nu doar să prindă eroarea
    ...

# 4. Prezentare + alegere lider (fara logica ObjectionEngine implicata)
chosen_variant_key: str = "..."  # "CALDA" | "DIRECTA" | "INTREBARE", ales de lider
edited_text: str = variants[chosen_variant_key]  # posibil editat de lider

# 5. Submit
result: SubmitResponseResult = objection_engine.submit_response(
    objection_id=...,       # trebuie sa existe deja
    owner_id=current_user.id,
    objection_category=category,
    objection_text=objection_text,
    response_text=edited_text,
    response_variant_used=chosen_variant_key,
)

# 6. ConversationAgent interpretează result.validation.level, per tabelul de mai sus
```

---

## 5. Ce rămâne explicit NEDEFINIT aici (pentru Decizia 2)

- **Cine creează rândul `objections`** (cu `objection_id`) înainte ca `ConversationAgent` să poată apela `submit_response`? `ObjectionEngine` nu are metodă de creare — doar `submit_response` (UPDATE). Trebuie decis dacă `ConversationAgent` creează rândul (INSERT), sau dacă rămâne o dependință externă (posibil din fluxul `Conversation`, neconstruit).
- **Formatul exact al returnării `ConversationAgent`** către UI/canal — ce structură de date, ce câmpuri.
- **Cum interacționează `conversation_id` (opțional, per Decizia 1) cu `objection_id`** — dacă există o `Conversation`, obiecția e legată de ea prin FK deja existent (`objections.conversation_id`), dar `ConversationAgent` v1 nu citește/scrie `conversations` (Decizia 1) — deci această legătură rămâne pasivă, nu activă.
