# Decizia 43 — Objection Events

Status: APPROVED (owner, 19 august 2026)

## 1. Context

Auditul final E2E (Decizia 41) a confirmat: `ObjectionEngine` nu emite
niciun eveniment — nici la `create_objection()`, nici la
`submit_response()` (cel mai important punct de decizie din tot
fluxul, verificarea de siguranță). Decizia 42 a închis deja gap-ul
analog pentru Contact.

Tipar `_emit_event()` deja validat, verbatim identic în 5 engine-uri
acum (`Conversation`, `FollowUp`, `Partner`, `Mission`, `Contact`):

```python
def _emit_event(self, event_name: str, target_object_id: UUID, payload: dict) -> None:
    """Scrie evenimentul în tabelul generic `events`."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (event_name, target_object, target_object_id, payload) "
                "VALUES (%s, %s, %s, %s)",
                (event_name, "<target_object>", target_object_id, Json(payload)),
            )
```

## 2. Scope

**Domeniu:**
- `src/engines/objection/objection_engine.py` — adaugă `_emit_event()`
  + 2 apeluri (`create_objection`, `submit_response`)
- `tests/test_objection_engine.py` — teste unitare noi
- `tests/test_real_postgres.py` — extinde `TestObjectionEngineOnRealPostgres`
  (clasă deja existentă, nu se creează una nouă)

**Explicit exclus:**
- `src/api/routers/objections.py`, `schemas.py` — niciun răspuns HTTP
  nu se schimbă, evenimentul e intern
- `ConversationAgent` — neatins, nu orchestrează nimic legat de
  evenimente, doar deleagă la `ObjectionEngine`
- Workbench — neatins
- Nicio migrare DB — schema `events` există deja

## 3. Design înghețat — 2 evenimente

### 3.1. `create_objection()` → `ObjectionCreated`

Emis după `INSERT`, `target_object_id = objection.id`.

```python
self._emit_event("ObjectionCreated", objection.id, {"owner_id": str(owner_id)})
```

Payload identic ca formă cu `ContactCreated`/`MissionGenerated` —
entitate fără părinte relevant de referențiat separat (`conversation_id`
e deja parte din rândul `objections` însuși, opțional).

### 3.2. `submit_response()` → `ObjectionResponseSubmitted`, pe TOATE ramurile

**Un singur eveniment**, emis indiferent de rezultatul validării —
inclusiv pe ramura `BLOCK`. Motivație (verbatim din decizia aprobată):
`BLOCK` e o decizie reală de business, nu absența unei acțiuni —
excluderea lui ar reproduce exact gap-ul semnalat de auditul 41, doar
mutat de la „zero evenimente" la „evenimente doar pentru cazul fericit".

```python
self._emit_event("ObjectionResponseSubmitted", objection_id, {
    "owner_id": str(owner_id),
    "validation_level": validation.level,
    "persisted": persisted,
})
```

**Ordine exactă în cod:**
```
validate_response(...)
   ↓
BLOCK?
   ├── DA → persisted=False, ZERO UPDATE, apoi _emit_event (persisted=False)
   └── NU → UPDATE real, persisted=True, apoi _emit_event (persisted=True)
```

`persisted` elimină orice ambiguitate la citirea ulterioară a
evenimentului — nu trebuie dedus din `validation_level` ce s-a
întâmplat efectiv în DB.

**Punct de atenție tehnic, verificat din audit**: pe ramura `BLOCK`,
metoda face `return` înainte de blocul `with get_connection()`
existent (linia 277 din cod curent) — `_emit_event()` trebuie apelat
**înainte** de acel `return`, nu după, altfel nu se execută niciodată
pe ramura `BLOCK`.

## 4. Ownership — neschimbat

Ambele metode păstrează exact verificările existente:
- `submit_response()` — filtrare `owner_id` în `UPDATE ... WHERE`,
  `ObjectionNotFoundError` dacă 0 rânduri afectate (verificare
  neschimbată, evenimentul nu se emite dacă apare această eroare —
  metoda ridică excepția înainte de a ajunge la `_emit_event`)
- `create_objection()` — nicio verificare de ownership proprie
  (owner_id vine deja din JWT, prin `ConversationAgent`)

## 5. Criterii de acceptare (RED)

**Nivel unitar** (`tests/test_objection_engine.py`), pattern identic
cu `test_creare_noua_emite_event_conversation_created`:

1. `test_create_objection_emite_event_objection_created` — `patch.object(ObjectionEngine, "_emit_event")`, verifică `args[0] == "ObjectionCreated"`, `args[1] == objection.id`
2. `test_submit_response_pass_emite_event_cu_persisted_true` — verifică `args[0] == "ObjectionResponseSubmitted"`, payload conține `"persisted": True`, `"validation_level": "PASS"`
3. `test_submit_response_block_emite_event_cu_persisted_false` — verifică `args[0] == "ObjectionResponseSubmitted"`, payload conține `"persisted": False`, `"validation_level": "BLOCK"` — **evenimentul TOT se emite**, deși nimic nu s-a scris în `objections`

**Nivel PostgreSQL real** (`tests/test_real_postgres.py`, extinde
`TestObjectionEngineOnRealPostgres`):

4. `test_evenimentul_objection_created_e_scris_in_events` — `SELECT event_name, target_object FROM events WHERE target_object_id = %s` → `("ObjectionCreated", "objection")`
5. `test_evenimentul_submit_response_pass_e_scris_in_events` — verifică rândul din `events` pentru `ObjectionResponseSubmitted`, payload cu `persisted=true`
6. `test_evenimentul_submit_response_block_e_scris_in_events` — verifică rândul din `events` pentru `ObjectionResponseSubmitted`, payload cu `persisted=false`, **și** confirmă separat că `objections.response_text` a rămas `NULL` (regresie explicită pe regula deja validată — evenimentul nu schimbă comportamentul de persistare)

## 6. Ordinea de lucru

```
contract (acest document)
   ↓
RED — 6 teste, toate eșuând din lipsă _emit_event
   ↓
GREEN — _emit_event() + 2 apeluri, plasare corectă pe ramura BLOCK
   ↓
regresie completă (457 + 6, toate PASS)
   ↓
43 CLOSED
```

Nu se scrie cod de implementare înainte de RED.
