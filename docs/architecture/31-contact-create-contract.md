# DECIZIA 31 — `POST /api/v1/contacts` — CONTACT CREATE v1 — CONTRACT

**Status:** confirmat de owner, cele 3 decizii oficiale (status implicit `NEW`, câmpuri
opționale expuse fără validare nouă, `ContactEngine` nou separat de `ContactAgent`). Verificat
direct din cod (`001_initial_schema.sql`, `20-contact-agent-contract.md`,
`conversation_engine.py`, `objection_engine.py`, toate fixture-urile de test) — nu din memorie.

---

## 1. Cele 3 decizii oficiale

| # | Decizie | Contract |
|---|---|---|
| 1 | `status` la creare | Server-side, hardcodat `'NEW'` în `INSERT` — nu vine din client. Precedent identic: `ConversationEngine.get_or_create_conversation()` hardcodează `'INITIATED'`. |
| 2 | `phone`/`email`/`source`/`metadata` | Opționale în `CreateContactRequest`, `NULL` acceptat, **fără nicio validare nouă** de format (fără `EmailStr`, fără regex telefon, fără normalizare) — schema deja le permite `NULL`, nu inventăm reguli de business inexistente azi |
| 3 | `ContactEngine` nou | Fișier nou, `src/engines/contact/contact_engine.py` — **`ContactAgent` rămâne neatins**, strict read-only, exact cum declară contractul `20` |

## 2. Securitate — 2 reguli, verificate structural, nu doar documentate

- `owner_id` **nu apare în `CreateContactRequest`** — exclusiv din `current_user.id` (JWT)
- `status` **nu apare în `CreateContactRequest`** — exclusiv hardcodat server-side ca `'NEW'`

Un client nu poate crea un contact direct `CONVERTED`/`ACTIVE`/`ARCHIVED`, și nu poate crea un
contact pentru alt `owner_id`.

## 3. Semnătura request/response

```python
class CreateContactRequest(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[dict] = None


class ContactResponse(BaseModel):
    id: UUID
    owner_id: UUID
    full_name: str
    phone: Optional[str]
    email: Optional[str]
    status: str
    source: Optional[str]
    metadata: dict
```

## 4. `ContactEngine.create_contact()` — semnătură și flux

```python
def create_contact(
    self,
    owner_id: UUID,
    full_name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    source: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Contact:
```

```
INSERT INTO contacts (owner_id, full_name, phone, email, status, source, metadata)
VALUES (%s, %s, %s, %s, 'NEW', %s, %s)
RETURNING id, owner_id, full_name, phone, email, status, source, metadata
```

`metadata=None` → tratat ca `{}` la nivelul Python înainte de `INSERT` (coloana are
`DEFAULT '{}'::jsonb`, dar transmitem explicit pentru consecvență cu restul câmpurilor —
evită ambiguitatea `NULL` vs `{}` în `RETURNING`).

**Erori**: schema nu are `UNIQUE`/`FK`/`CHECK` suplimentar pe câmpurile noi (doar `owner_id`
FK, deja garantat valid — vine din JWT, user autentificat există prin construcție). Nu există
niciun caz de eroare de domeniu specific creării unui contact, dincolo de validarea Pydantic
standard (`full_name` lipsă → `422`, automat FastAPI).

## 5. Fișiere afectate

| Fișier | Schimbare |
|---|---|
| `src/engines/contact/contact_engine.py` | **NOU** — `ContactEngine.create_contact()`, dataclass `Contact` |
| `src/engines/contact/__init__.py` | **NOU**, gol |
| `src/api/schemas.py` | Adaugă `CreateContactRequest`, `ContactResponse` |
| `src/api/routers/contacts.py` | **NOU** — `POST /api/v1/contacts`, `status_code=201` |
| `src/api/dependencies.py` | Adaugă `get_contact_engine()` |
| `src/api/main.py` | `app.include_router(contacts.router)` |

**Neschimbate, explicit**: `ContactAgent` (`contact_agent.py`), `20-contact-agent-contract.md`.

## 6. Testarea — criteriul de acceptare complet, cu cazurile de integrare cerute

```
register lider A → login A → POST /contacts → 201
        ↓
contact.owner_id == A.id, contact.status == 'NEW'
        ↓
lider B → nu poate crea contact cu owner_id A (owner_id absent din request — verificat
          structural: schema nu are câmpul, nu doar "ignorat")
        ↓
INTEGRARE cu flux existent — contact creat de A prin acest endpoint, folosit real de
ConversationEngine.get_or_create_conversation() (Decizia 29, deja validat pe PostgreSQL real):
    A → get_or_create_conversation(contact_id) → 200/succes
    B → get_or_create_conversation(contact_id_al_lui_A) → ConversationAccessDeniedError
        (mecanism deja existent, verificat aici doar cu date create prin fluxul real,
        nu prin fixture SQL — confirmă integrarea end-to-end, nu un mecanism nou)
        ↓
regresie completă (352 existente + noile)
```
