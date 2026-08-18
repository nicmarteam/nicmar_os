# DECIZIA 33 — `Conversation → Objection` LINKAGE — CONTRACT

**Status:** confirmat de owner, direcția A+B din audit. Verificat direct din cod
(`objection_engine.py`, `conversation_agent.py`, `conversation_engine.py`, `dependencies.py`,
`apps/workbench/index.html`) — nu din memorie.

**Descoperire centrală, motivul acestei decizii**: `create_objection()` transmite
`conversation_id` la `INSERT` fără nicio verificare de proprietate — doar `ForeignKeyViolation`
(existență). Un `conversation_id` real, al altui lider, ar reuși azi cu `201`. Acest contract
închide gaura, fără să atingă `ObjectionEngine`.

---

## 1. Reparația de securitate — `ConversationAgent` capătă a doua dependință

```python
class ConversationAgent:
    def __init__(
        self,
        objection_engine: ObjectionEngine,
        conversation_engine: ConversationEngine,   # NOU
    ):
        self.objection_engine = objection_engine
        self.conversation_engine = conversation_engine
```

**`ConversationEngine.get_conversation(conversation_id, owner_id) -> Conversation`** — metodă
nouă, mirror exact al `ObjectionEngine.get_objection()` (Decizia 8A): `SELECT` simplu, fără
filtrare pe status (spre deosebire de `get_or_create_conversation`, care filtrează doar
conversații deschise — aici verificăm orice conversație, indiferent de stare). Reutilizează
`ConversationAccessDeniedError`, deja existentă — nicio excepție nouă.

**`prepare_response_options()` — comportament nou**:

```
conversation_id = None
    → fluxul existent, neschimbat, zero verificare suplimentară

conversation_id = valid + owned
    → self.conversation_engine.get_conversation(conversation_id, owner_id)  [NOU]
    → apoi create_objection() ca înainte

conversation_id = existent, al altui lider
    → ConversationAccessDeniedError, propagată neprinsă
    → create_objection() NU se apelă deloc — ZERO INSERT
```

**`ObjectionEngine` rămâne complet neatins** — nu importă, nu cunoaște `ConversationEngine`.

## 2. Endpoint nou — `POST /api/v1/conversations`

Expune `ConversationEngine.get_or_create_conversation()`. **Decizie**: `channel` NU e acceptat
din request — rămâne hardcodat `'WHATSAPP'` server-side (identic motiv ca `status`/`role`
la deciziile anterioare: nicio altă valoare de canal nu e folosită real nicăieri în sistem,
componenta 5 fiind neconstruită încă — a expune parametrul acum ar fi prematur).

```python
class CreateConversationRequest(BaseModel):
    contact_id: UUID


class ConversationResponse(BaseModel):
    id: UUID
    owner_id: UUID
    contact_id: UUID
    channel: str
    status: str
```

```
POST /api/v1/conversations
    ↓
owner_id = current_user.id (JWT)
    ↓
ConversationEngine.get_or_create_conversation(owner_id, contact_id)
    ↓
201 (idempotent — poate returna o conversație EXISTENTĂ cu status 201,
     nu 200, pentru simplitate — nu distingem "creat nou" de "returnat
     existent" la nivel de status code în v1; ambele sunt răspunsuri
     de succes ale aceleiași operații idempotente)
    ↓
ConversationAccessDeniedError (contact_id invalid/al altui owner) → 403,
    reutilizează handler-ul deja înregistrat
```

## 3. Endpoint nou — `GET /api/v1/contacts`

Expune `ContactAgent.list_prioritized_contacts()` — deja implementat, deja testat, doar
neconectat. Necesită `get_contact_agent()` nou în `dependencies.py` (confirmat lipsă).

```python
class ContactSummaryResponse(BaseModel):
    contact_id: UUID
    full_name: str
    status: str
    last_followup_at: Optional[datetime]
    last_followup_status: Optional[str]
    converted_to: Optional[str]
    pdi: Optional[float]
    pip: Optional[float]
    reason: str
```

```
GET /api/v1/contacts
    ↓
owner_id = current_user.id (JWT)
    ↓
ContactAgent.list_prioritized_contacts(owner_id)
    ↓
200, listă (posibil goală) — READ-ONLY, zero scriere, comportament deja verificat de testele
    existente ale ContactAgent
```

## 4. `/objections/prepare` — contract neschimbat

Confirmat explicit: `conversation_id` rămâne `Optional[UUID] = None` în
`PrepareResponseOptionsRequest` — nicio schimbare de schemă. Doar comportamentul intern
(secțiunea 1) se schimbă.

## 5. Fișiere afectate

| Fișier | Schimbare |
|---|---|
| `src/engines/conversation/conversation_engine.py` | Adaugă `get_conversation()` |
| `src/agents/conversation/conversation_agent.py` | Constructor + `prepare_response_options()` modificate |
| `src/api/dependencies.py` | `get_contact_agent()` nou; `get_conversation_engine()` nou; `get_conversation_agent()` capătă a doua `Depends()` |
| `src/api/schemas.py` | `CreateConversationRequest`, `ConversationResponse`, `ContactSummaryResponse` |
| `src/api/routers/conversations.py` | **NOU** — `POST /api/v1/conversations` |
| `src/api/routers/contacts.py` | Adaugă `GET ""` |
| `src/api/main.py` | `app.include_router(conversations.router)` |
| `apps/workbench/index.html` | **NU se modifică în acest pas** — conectarea UI e pas separat, ulterior; acest contract livrează doar backend-ul funcțional |

**Notă importantă de scope**: contractul NU include actualizarea `index.html` — criteriul de
acceptare cere fluxul backend complet (Contact → Conversation → Objection legat), verificabil
prin API/PostgreSQL real, nu neapărat prin Workbench-ul vizual încă. Conectarea UI rămâne
explicit un pas separat, dacă va fi decis.

## 6. Testarea — criteriul de acceptare complet

```
FLUX POZITIV (Leader A):
register → login → POST /contacts → POST /conversations → POST /objections/prepare
    (cu conversation_id real al lui A)
    ↓
verificare explicită, nu doar 201:
    objection.conversation_id == conversation_id (din DB, nu doar din response)

FLUX NEGATIV (Leader B, obligatoriu):
Leader A creează Contact A + Conversation A
Leader B → POST /objections/prepare {conversation_id=Conversation A} → 403
    ↓
ConversationAccessDeniedError
    ↓
verificare explicită: COUNT(*) FROM objections WHERE conversation_id=Conversation_A
    neschimbat față de înainte de încercarea lui B (ZERO INSERT)

conversation_id=None — regresie: fluxul vechi neschimbat, toate testele existente
    ObjectionEngine/ConversationAgent rămân verzi neschimbate

GET /contacts — owner_id izolat corect (deja testat la nivel de ContactAgent,
    verificăm doar conectarea HTTP)

POST /conversations — idempotent prin HTTP (al doilea apel, același contact,
    returnează aceeași conversație — verificat deja la nivel de ConversationEngine,
    verificăm conectarea HTTP)

regresie completă (381 existente + noile)
```
