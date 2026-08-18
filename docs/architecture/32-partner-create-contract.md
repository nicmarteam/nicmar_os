# DECIZIA 32 — `POST /api/v1/partners` — PARTNER CREATE v1 — CONTRACT

**Status:** confirmat de owner, cele 3 decizii oficiale (status `ACTIVATED`, arhitectură
`Router → PartnerAgent → PartnerEngine`, eveniment `PartnerCreated` fără KPI). Verificat direct
din cod (`001_initial_schema.sql`, `partner_engine.py`, `partner_agent.py`, `partners.py`,
`exception_handlers.py`, toate fixture-urile de test) — nu din memorie.

---

## 1. Cele 3 decizii oficiale

| # | Decizie | Contract |
|---|---|---|
| 1 | Status inițial | `'ACTIVATED'` hardcodat server-side — precedent unanim, toate cele 6 fixture-uri de test existente |
| 2 | Arhitectură | `Router → PartnerAgent.create_partner() → PartnerEngine.create_partner()` — consecvent cu restul endpoint-urilor Partner (spre deosebire de Contact, unde `ContactAgent` e strict read-only) |
| 3 | Eveniment | `PartnerCreated`, emis după succes; **fără PDI/PIP**, fără alt efect secundar — acelea rămân exclusiv la `confirm_and_complete()` |

## 2. Reguli de securitate — fluxul exact de ownership

```
JWT (user A)
    ↓
contact_id (din request)
    ↓
verificare: contacts.owner_id == user A  ← NOU, verificare explicită
    ↓
INSERT partners(owner_id=A, contact_id=...)
```

**Verificare nouă, necesară**: nu există azi nicio metodă de citire ownership pentru `contacts`
(spre deosebire de `partners`, care are deja `_verify_ownership`). Se adaugă un `SELECT 1 FROM
contacts WHERE id = %s AND owner_id = %s` în `PartnerEngine.create_partner()`, înainte de
`INSERT`. **Reutilizează `PartnerAccessDeniedError`** (deja existentă, deja înregistrată la
`403 ACCESS_DENIED`) — nu se introduce o excepție nouă doar pentru acest caz; mesajul rămâne
specific ("Contact X nu există sau nu aparține acestui owner"), clasa excepției rămâne aceeași.

## 3. `partner_level`/`status` — niciunul nu intră în request

- `partner_level`: absent din `CreatePartnerRequest` — DB aplică `DEFAULT 'BRONZE'`, la fel ca
  `role='LEADER'` la register.
- `status`: absent din `CreatePartnerRequest` — hardcodat `'ACTIVATED'` în `INSERT`, exact
  pattern-ul `ConversationEngine`/`ContactEngine`.

## 4. Duplicate `contact_id` — mecanism deja existent, zero cod nou de handler

Schema: `partners.contact_id UUID UNIQUE NOT NULL`. La al doilea `INSERT` cu același
`contact_id`, PostgreSQL ridică `UniqueViolation`. **Verificat: deja înregistrată global**
(`exception_handlers.py`, `ALREADY_EXISTS_ERRORS`, adăugată la Decizia 30) → `409
ALREADY_EXISTS`, automat. Niciun cod nou necesar în `exception_handlers.py`.

## 5. Semnătura request/response

```python
class CreatePartnerRequest(BaseModel):
    contact_id: UUID


class PartnerResponse(BaseModel):
    id: UUID
    owner_id: UUID
    contact_id: UUID
    status: str
    partner_level: str
```

## 6. `PartnerEngine.create_partner()` — semnătură și flux

```python
def create_partner(self, owner_id: UUID, contact_id: UUID) -> Partner:
```

```
1. SELECT 1 FROM contacts WHERE id = %s AND owner_id = %s
   → None → PartnerAccessDeniedError
2. INSERT INTO partners (owner_id, contact_id, status)
   VALUES (%s, %s, 'ACTIVATED')
   RETURNING id, owner_id, contact_id, status, partner_level
   → UniqueViolation (contact_id deja partener) → propagă neprinsă → 409 (handler existent)
3. _emit_event("PartnerCreated", partner.id, {"contact_id": str(contact_id)})
4. return Partner(...)
```

`PartnerAgent.create_partner()` — delegare simplă, identică stilistic cu
`request_diagnostic()`/`confirm_and_send()`:

```python
def create_partner(self, owner_id: UUID, contact_id: UUID) -> Partner:
    return self.partner_engine.create_partner(owner_id, contact_id)
```

## 7. Fișiere afectate

| Fișier | Schimbare |
|---|---|
| `src/engines/partner/partner_engine.py` | Adaugă `Partner` dataclass, `create_partner()` |
| `src/agents/partner/partner_agent.py` | Adaugă `create_partner()` (delegare) |
| `src/api/schemas.py` | Adaugă `CreatePartnerRequest`, `PartnerResponse` |
| `src/api/routers/partners.py` | Adaugă `POST /api/v1/partners`, `status_code=201` |

**Neschimbate, explicit**: `exception_handlers.py` (ambele excepții deja înregistrate),
`generate_diagnostic()`/`confirm_and_complete()`/`_record_pdi_pip_scores()`.

## 8. Testarea — criteriul de acceptare, cu cele 2 teste de securitate cerute explicit

```
TEST 1 — ownership la creare (403, nu doar la operații ulterioare):
Leader A creează Contact A
Leader B → POST /partners {contact_id=Contact A} → 403 ACCESS_DENIED
    ↓
verificare explicită: NU există rând nou în partners

TEST 2 — duplicate + rollback (identic disciplina de la Register):
Leader A → Partner(contact X) → 201
Leader A → Partner(contact X) din nou → 409 ALREADY_EXISTS
Leader A → Partner(contact Y, diferit) → 201, imediat după eșecul de mai sus
    ↓
confirmă simultan: ownership + UNIQUE + rollback funcțional

FLUX COMPLET:
register → login → POST /contacts → POST /partners → 201
    ↓
partner.status == 'ACTIVATED', partner.partner_level == 'BRONZE' (verificat din DB)
    ↓
eveniment PartnerCreated prezent în `events` (target_object='partner')
    ↓
PDI/PIP NU apar în `scores` după creare (verificat explicit — creare ≠ finalizare)
    ↓
regresie completă (365 existente + noile)
```
