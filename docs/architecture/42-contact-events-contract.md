# Decizia 42 — Contact Events

Status: APPROVED (owner, 19 august 2026)

## 1. Context

Auditul final E2E (Decizia 41) a confirmat: `ContactEngine.create_contact()`
nu emite niciun eveniment — singurul engine de creare din tot lanțul
fără această trasabilitate. Toate celelalte 4 engine-uri
(`ConversationEngine`, `FollowUpEngine`, `PartnerEngine`,
`MissionEngine`) au `_emit_event()`, cu tipar **identic, verbatim**,
verificat explicit prin comparație directă de cod:

```python
def _emit_event(self, event_name: str, target_object_id: UUID, payload: dict) -> None:
    """Scrie evenimentul în tabelul generic `events`."""
    from psycopg.types.json import Json
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (event_name, target_object, target_object_id, payload) "
                "VALUES (%s, %s, %s, %s)",
                (event_name, "<target_object>", target_object_id, Json(payload)),
            )
```

Singura variabilă între implementări e valoarea `target_object`
(`"conversation"`, `"followup"`, `"partner"`, `"mission"`).

**Descoperire suplimentară de audit** (nu era în raportul 41, la acest
nivel de detaliu): `ContactEngine` nu are nici clasă
`TestContactEngineOnRealPostgres` — doar `TestContactAgentOnRealPostgres`
există, care testează `ContactAgent` (read-only), altă componentă.
Zero test PostgreSQL real pentru `ContactEngine.create_contact()` —
gol de acoperit tot acum, ca implementarea nouă să respecte disciplina
de testare pe 2 niveluri deja folosită peste tot (unitar mock +
PostgreSQL real).

## 2. Scope

**Domeniu:**
- `src/engines/contact/contact_engine.py` — adaugă `_emit_event()` +
  un apel din `create_contact()`
- `tests/test_contact_engine.py` — test unitar nou (fișier existent,
  extins)
- `tests/test_real_postgres.py` — clasă nouă `TestContactEngineOnRealPostgres`

**Explicit exclus:**
- `ContactAgent` (read-only) — neatins
- `src/api/routers/contacts.py`, `schemas.py` — niciun răspuns HTTP nu
  se schimbă (evenimentul e intern, nu apare în response)
- Nicio migrare DB — schema `events` există deja, neschimbată
- Workbench — neatins

## 3. Implementare exactă

```python
# ContactEngine._emit_event() — identic ca tipar cu celelalte 4
def _emit_event(self, event_name: str, target_object_id: UUID, payload: dict) -> None:
    """Scrie evenimentul în tabelul generic `events`."""
    from psycopg.types.json import Json
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (event_name, target_object, target_object_id, payload) "
                "VALUES (%s, %s, %s, %s)",
                (event_name, "contact", target_object_id, Json(payload)),
            )
```

```python
# în create_contact(), după construirea obiectului Contact, înainte de return:
self._emit_event("ContactCreated", contact.id, {"owner_id": str(owner_id)})
return contact
```

**Payload**: `{"owner_id": str(owner_id)}` — convenția exactă folosită
la `MissionGenerated` (entitate top-level, fără părinte), nu convenția
`{"contact_id": ...}` folosită la `ConversationCreated`/`PartnerCreated`
(care au un părinte `contact`). Contact nu are părinte în acest sens —
`owner_id` e singurul identificator relevant de atașat.

## 4. Criterii de acceptare (RED)

**Nivel unitar** (`tests/test_contact_engine.py`), pattern identic cu
`test_creare_noua_emite_event_conversation_created`:

1. `test_create_contact_emite_event_contact_created` — `patch.object(ContactEngine, "_emit_event")`, verifică `mock_emit.assert_called_once()`, `args[0] == "ContactCreated"`, `args[1] == contact_id`

**Nivel PostgreSQL real** (`tests/test_real_postgres.py`), clasă nouă,
pattern identic cu `test_evenimentul_conversation_created_e_scris_in_events`:

2. `TestContactEngineOnRealPostgres.test_creeaza_contact_pe_postgres_real` — verifică `Contact` complet, valorile scrise corect în `contacts`
3. `TestContactEngineOnRealPostgres.test_evenimentul_contact_created_e_scris_in_events` — `SELECT event_name, target_object FROM events WHERE target_object_id = %s` → `("ContactCreated", "contact")`

## 5. Ordinea de lucru

```
contract (acest document)
   ↓
RED — 3 teste, toate eșuând (2 din lipsă _emit_event, 1 clasă nouă lipsă complet)
   ↓
GREEN — _emit_event() + apelul din create_contact()
   ↓
regresie completă (454 + 3, toate PASS)
   ↓
42 CLOSED
```

Nu se scrie cod de implementare înainte de RED.
