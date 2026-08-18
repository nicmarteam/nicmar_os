# DECIZIA 30 — `POST /api/v1/auth/register` — AUTH REGISTRATION v1 — CONTRACT

**Status:** confirmat de owner, cele 3 decizii oficiale (duplicate email, normalizare email,
politică parolă) + o consecință derivată explicit din criteriul de acceptare stabilit anterior.
Verificat direct din cod (`auth.py`, `service.py`, `security.py`, `dependencies.py`,
`exception_handlers.py`, `001`/`003` migrări, `test_auth.py`) — nu din memorie.

**Scope strict**: `/auth/login` **nu se modifică** în acest pas. Normalizarea globală a
emailului rămâne decizie separată, viitoare.

---

## 1. Cele 4 decizii oficiale

| # | Decizie | Contract |
|---|---|---|
| 1 | Duplicate email | `INSERT ... RETURNING` direct; `psycopg.errors.UniqueViolation` → `409 ALREADY_EXISTS` (handler nou, reutilizează `_error_response` existent) |
| 2 | Email | Primit exact, fără `.lower()`/`.strip()` — consecvent cu `/login` |
| 3 | Parolă | Minim **8 caractere**, maxim **72 bytes UTF-8** (limita tehnică bcrypt) — validat înainte de `hash_password()` |
| 4 | `/register` NU returnează JWT | **Derivat explicit din criteriul de acceptare stabilit anterior** ("register → user creat → ... → login cu utilizatorul nou → JWT") — `register` confirmă doar userul creat; JWT vine exclusiv din `/login`, pas separat |

## 1A. Rollback la `UniqueViolation` — verificat, nu doar presupus

**Confirmat direct din `src/data/db.py`, `get_connection()`**: context manager-ul existent face
deja `except Exception: conn.rollback(); raise` urmat de `finally: conn.close()` — comportament
implicit `psycopg3`, neschimbat, nicio logică nouă de adăugat. În plus, fiecare request
deschide o conexiune **nouă** (fără connection pooling/reuse între request-uri) — deci nu există
risc real de "conexiune poluată" propagată de la un request eșuat la următorul.

**Cerință explicită pentru implementare**: `INSERT`-ul din `register_user()` trebuie să
rămână **în interiorul** blocului `with get_connection() as conn: with conn.cursor() as cur:`,
iar `UniqueViolation` trebuie să **propage natural** din acel bloc (neprinsă local în
`registration.py`) — exact ca `ForeignKeyViolation` la `create_objection()`. Nu se adaugă
niciun `try/except`/rollback manual în `registration.py` — mecanismul existent e suficient,
verificat mai sus.

## 1B. `role` — formulare corectată (securitate, nu doar omisiune)

**Corectare față de formularea inițială** ("`role` NU e acceptat din payload — dacă trimis,
ignorat"): `role` **nu face parte din `RegisterRequest`** deloc. Comportamentul pentru câmpuri
extra trimise de client respectă politica Pydantic implicită a proiectului (fără `extra="forbid"`
introdus acum — repo-ul nu folosește această convenție global, și n-o introducem transversal
doar pentru acest pas). Garanția de securitate reală, verificabilă, e alta:

```
role nu vine din client (nu există în schema request)
        ↓
INSERT-ul nu include coloana role
        ↓
PostgreSQL aplică DEFAULT 'LEADER'
```

Testul relevant verifică rezultatul din DB (`role == 'LEADER'`), nu presupune ce se întâmplă cu
un câmp extra ipotetic trimis de client.

## 1C. `full_name`/`email` — obligatorii ca prezență, fără politică de conținut

`full_name: str` și `email: str` rămân **obligatorii ca prezență** (Pydantic `422` dacă lipsesc),
**fără** nicio regulă suplimentară de conținut în această etapă — `full_name=""` sau
`full_name="   "` **nu sunt respinse explicit** acum; nu se inventează o politică de business
care nu există azi nicăieri altundeva în proiect. Dacă va fi nevoie, e o decizie separată.

## 2. Câmp obligatoriu, verificat din schemă, netratat explicit până acum

`users.full_name TEXT NOT NULL` — fără `DEFAULT`. **`RegisterRequest` trebuie să includă
`full_name` ca obligatoriu** — altfel `INSERT` eșuează cu `NotNullViolation`, netratată. Nu e o
decizie nouă, e o consecință directă a schemei reale, verificată acum.

## 3. Semnătura request/response

```python
class RegisterRequest(BaseModel):
    email: str
    password: str  # validat: 8-72 bytes UTF-8, vezi secțiunea 4
    full_name: str


class RegisterResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
```

**Niciodată** `password`/`password_hash` în `RegisterResponse` — parola în clar nu se persistă,
nu se ecouă înapoi.

## 4. Validarea parolei — unde și cum, ca să nu coliziune cu erorile existente

**Decizie tehnică explicită**: validarea lungimii parolei (8-72 bytes) se face printr-un
**validator Pydantic** pe `RegisterRequest`, NU printr-un `raise ValueError` manual în codul de
business.

**Motiv, verificat din `exception_handlers.py`**: există deja un handler global
`ValueError → 400 INVALID_CATEGORY` (Decizia 26A, specific pentru categoria de obiecție
invalidă). Dacă aș ridica un `ValueError` simplu pentru parolă invalidă în stratul de business,
ar fi etichetat greșit, semantic, drept `INVALID_CATEGORY` — complet nepotrivit. Validatorul
Pydantic evită asta: erorile de validare a body-ului sunt prinse de FastAPI **înainte** să ajungă
la handler-ele noastre custom, returnând `422` automat (comportament deja documentat în
`26-objections-router-contract.md`, secțiunea 3.5, "Body Pydantic invalid... automat FastAPI,
neschimbat") — fără nicio coliziune.

```python
@field_validator("password")
@classmethod
def _validate_password_length(cls, v: str) -> str:
    byte_length = len(v.encode("utf-8"))
    if len(v) < 8:
        raise ValueError("Parola trebuie să aibă minimum 8 caractere.")
    if byte_length > 72:
        raise ValueError("Parola nu poate depăși 72 de bytes (UTF-8).")
    return v
```

## 5. Fluxul intern

```
POST /api/v1/auth/register
        ↓
RegisterRequest validat (Pydantic — email: str, password: 8-72 bytes, full_name obligatoriu)
        ↓
hash_password(password)  — bcrypt, funcția EXISTENTĂ din security.py, neschimbată
        ↓
INSERT INTO users (email, full_name, password_hash)
VALUES (%s, %s, %s)
RETURNING id, email, full_name, role
        ↓
role — NU e în lista de coloane INSERT — DB aplică DEFAULT 'LEADER'
        ↓
UniqueViolation (email deja există) → propagă neprinsă → handler global → 409 ALREADY_EXISTS
        ↓
succes → 201 RegisterResponse(id, email, full_name, role)
```

## 6. Fișiere afectate — verificat exact, minim necesar

| Fișier | Schimbare |
|---|---|
| `src/auth/registration.py` | **NOU** — `register_user(email, password, full_name) -> RegisteredUser`, dataclass `RegisteredUser(id, email, full_name, role)` |
| `src/api/schemas.py` | Adaugă `RegisterRequest` (cu validator), `RegisterResponse` |
| `src/api/routers/auth.py` | Adaugă endpoint `POST /register`, `status_code=201` |
| `src/api/exception_handlers.py` | Import `UniqueViolation`; `app.add_exception_handler(UniqueViolation, handle_already_exists)` — reutilizează handler-ul `409 ALREADY_EXISTS` deja existent, nu creează unul nou |

**Neschimbate, explicit**: `src/auth/service.py` (`authenticate`), `src/auth/security.py`
(`hash_password`/`verify_password` — refolosite ca atare, nu modificate),
`src/auth/dependencies.py`, `/auth/login`.

## 7. Testarea — RED → GREEN → PostgreSQL real, criteriul de acceptare complet

```
register valid → 201, RegisterResponse corect
        ↓
password_hash verificat direct din DB — hash bcrypt valid, NU parola în clar
        ↓
email duplicat → 409 ALREADY_EXISTS
        ↓
full_name lipsă → 422 (Pydantic)
        ↓
parolă < 8 caractere → 422
        ↓
parolă > 72 bytes UTF-8 (atenție: caractere multi-byte, ex. emoji/diacritice, nu doar count() de caractere) → 422
        ↓
role NU e acceptat din payload — verificat prin rezultatul din DB (role == 'LEADER'), nu prin presupunere despre câmpuri extra
        ↓
DoD suplimentar — verifică indirect că UniqueViolation nu lasă conexiunea/tranzacția
într-o stare defectă:
    register (email X) → 201
    register (același email X) → 409
    register (email Y, diferit) → 201, ÎN ACEEAȘI SUITĂ, imediat după eșecul de mai sus
        ↓
FLUX COMPLET: register → login cu userul nou creat → 200, JWT valid → GET către un endpoint
protejat existent (ex. /objections/categories) cu acel JWT → 200, acces confirmat
        ↓
regresie completă (334 existente + noile)
```
