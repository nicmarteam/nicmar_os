# DECIZIA 2A — `ObjectionEngine.create_objection()` — CONTRACT v1

**Status:** confirmat de owner, 18 august 2026, precondiție pentru `ConversationAgent` (Decizia 2).
**Precedent:** aceeași disciplină ca `21-objection-engine-contract.md` — verificare explicită
DECLARAT vs. EXISTĂ, TDD strict, fără cod înainte de contract.
**Motiv:** `ObjectionEngine.submit_response()` (v. `21`) face doar `UPDATE` — presupune un rând
`objections` deja existent. `ConversationAgent` nu poate orchestra fluxul complet fără o metodă
de creare. Fără această decizie, `ConversationAgent` ar fi obligat fie să facă `INSERT` direct
(rupe încapsularea domeniului `objections`, deținut de `ObjectionEngine`), fie să depindă de un
`Conversation writer` inexistent (confirmat ABSENT prin audit).

---

## 0. Decizie arhitecturală

`ObjectionEngine` devine proprietarul complet al ciclului de viață `objections`:
`classify → create → get_variants → validate → submit_response`.

`ConversationAgent` orchestrează — nu scrie niciodată direct în schema `objections`.

---

## 1. Semnătura exactă

```python
def create_objection(
    self,
    owner_id: UUID,
    objection_text: str,
    objection_category: str,
    conversation_id: Optional[UUID] = None,
) -> Objection
```

## 2. Tip de return — `Objection` (dataclass nou, nu `UUID`)

Consecvență cu precedentul din repo: `FollowUpEngine.create_from_trigger()` întoarce obiectul de
domeniu complet (`FollowUp`), nu doar `id`-ul. `create_objection()` urmează același tipar.

```python
@dataclass(frozen=True)
class Objection:
    """Reprezentarea unei obiecții, așa cum e citită din `objections`."""
    id: UUID
    owner_id: UUID
    conversation_id: Optional[UUID]
    objection_category: str
    objection_text: str
    resolution_status: str
```

## 3. Schema DB folosită (verificată din `001_initial_schema.sql`)

```sql
objections(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,  -- nullable
    objection_category TEXT NOT NULL,
    objection_text TEXT NOT NULL,
    resolution_status TEXT NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
)
```

`create_objection` nu setează explicit `resolution_status` — se bazează pe `DEFAULT 'OPEN'` al
coloanei, verificat direct din migrare.

## 4. Ordinea internă

```
1. objection_category not in ALL_CATEGORIES (library.py, deja existent)
       → ValueError, ÎNAINTE de orice conexiune DB (zero round-trip)
2. INSERT INTO objections (owner_id, conversation_id, objection_category, objection_text)
       VALUES (...) RETURNING id, owner_id, conversation_id, objection_category,
                             objection_text, resolution_status
3. PostgreSQL generează UUID + aplică DEFAULT 'OPEN'
4. Returnează Objection complet din RETURNING (nu presupune valorile — le citește din row)
```

## 5. Comportament per situație (matrice confirmată)

| Situație | Comportament |
|---|---|
| `objection_category` validă (una din cele 13, `ALL_CATEGORIES`) | `INSERT`, continuă |
| `objection_category` invalidă | `ValueError`, **fără apel DB** |
| `owner_id` valid | `INSERT` |
| `owner_id` invalid (FK) | Excepție `psycopg` nativă (`ForeignKeyViolation`), **nu se prinde separat** — consecvent cu restul repo-ului (niciun engine existent nu prinde FK violation explicit) |
| `conversation_id=None` | Permis — coloana e nullable |
| `conversation_id` valid | `INSERT` |
| `conversation_id` invalid (FK) | Excepție `psycopg` nativă, **nu se prinde separat** — idem |
| Aceeași obiecție (owner + categorie + text) repetată | **Nu există verificare de duplicat în v1** — fiecare apel valid creează un rând nou. Motiv: un prospect poate ridica aceeași obiecție de mai multe ori în aceeași conversație — sunt evenimente reale distincte, nu duplicate artificiale. Dacă va fi nevoie de deduplicare, va fi o decizie arhitecturală separată, bazată pe o regulă reală (nu presupusă aici). |
| `resolution_status` | `OPEN` implicit — din `DEFAULT` DB, nu setat explicit în cod |

## 6. Ce rămâne explicit în afara scopului v1

- Strat comun de traducere a erorilor DB (`ForeignKeyViolation` → excepție de domeniu) — dacă va fi
  nevoie, se proiectează separat, pentru toate engine-urile, nu ad-hoc aici.
- Orice regulă de deduplicare — nesusținută de nicio sursă reală în acest moment.
- Validarea existenței `conversation_id` înainte de `INSERT` (dublu round-trip) — se lasă pe seama
  constrângerii FK din PostgreSQL, consecvent cu restul codului.

---

## 7. Următorul pas

RED → teste pentru `create_objection()` (v. `tests/test_objection_engine.py`) → GREEN →
PostgreSQL real → regresie completă asupra suitei existente `ObjectionEngine`.
