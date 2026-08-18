# `objections.py` — API ROUTER — CONTRACT v1

**Status:** verificat direct din codul existent (`missions.py`, `followups.py`, `partners.py`,
`exception_handlers.py`, `test_mission_api.py`) — nu din memorie. Precondiții: Decizia 7
(`24-dependency-wiring-contract.md`, `get_objection_engine`/`get_conversation_agent`
implementate + validate) și Decizia 8A (`25-get-objection-contract.md`, `get_objection()` +
`confirm_response()` cu semnătură scalară, validate pe PostgreSQL real).

## 0. Auditul convențiilor existente (rezumat)

- Prefix router: `/api/v1/{resursă}`, `tags=[...]` — identic la toate 3 routere existente.
- `POST` care creează o resursă nouă → `status_code=201`; restul acțiunilor → `200` implicit.
- Erorile de domeniu (excepții Python) sunt mapate central în `exception_handlers.py`, pe
  **categorii semantice**, nu pe numele exact al excepției — `ACCESS_DENIED_ERRORS`,
  `ALREADY_EXISTS_ERRORS`, `INVALID_TRANSITION_ERRORS`, `CONFIRMATION_REQUIRED_ERRORS`.
  Fiecare excepție trebuie înregistrată **individual** (`app.add_exception_handler`) — un bug
  real descoperit anterior: sintaxa de tuplu la `@app.exception_handler((A, B))` nu funcționează
  la dispatch, deși nu ridică eroare la înregistrare.
- **Nici `ValueError`, nici `psycopg.errors.ForeignKeyViolation` nu sunt tratate nicăieri în
  stratul API actual** — confirmat, zero mențiune. Trebuie introduse acum, ca noutate.
- Testele API (`test_mission_api.py`) folosesc `TestClient` real, `DATABASE_URL` obligatoriu,
  autentificare reală prin `/api/v1/auth/login` (nu mock pe `get_current_user`).

## 1. Endpoint-urile

| Metodă | Path | `ConversationAgent` | DB | Status succes |
|---|---|---|---|---|
| `POST` | `/api/v1/objections/analyze` | `analyze_objection()` | NU | `200` |
| `GET` | `/api/v1/objections/categories` | `list_categories()` | NU | `200` |
| `POST` | `/api/v1/objections/prepare` | `prepare_response_options()` | DA | `201` (creează rândul `objections`) |
| `POST` | `/api/v1/objections/confirm` | `confirm_response()` | DA | `200` (actualizează rândul existent) |

## 2. Schemele request/response (Pydantic, `src/api/schemas.py`)

```python
class AnalyzeObjectionRequest(BaseModel):
    objection_text: str


class AnalyzeObjectionResponse(BaseModel):
    detected_category: Optional[str]
    needs_manual_selection: bool


class CategoriesResponse(BaseModel):
    categories: List[str]


class PrepareResponseOptionsRequest(BaseModel):
    objection_text: str
    objection_category: str
    conversation_id: Optional[UUID] = None


class PrepareResponseOptionsResponse(BaseModel):
    objection_id: UUID
    variants: Dict[str, str]


class ConfirmResponseRequest(BaseModel):
    objection_id: UUID
    response_text: str
    response_variant_used: str


class ConfirmResponseResponseSchema(BaseModel):
    persisted: bool
    validation_level: str
    reason: Optional[str]
```

**Decizie de expunere minimă:** `PrepareResponseOptionsResponse` NU expune `owner_id`,
`objection_text`, `resolution_status` — clientul le are deja (le-a trimis el însuși sau nu-i
sunt necesare). Doar `objection_id` (necesar la `/confirm`) și `variants`.

**Câmpuri absente intenționat, per regula de securitate:** niciun schema de request nu conține
`owner_id`, `objection_category` (la `/confirm`) sau `objection_text` (la `/confirm`) — exact
lista interzisă din auditul tău.

## 3. Statusurile HTTP pentru erori — 2 decizii noi, propuse mai jos

### 3.1 `ObjectionNotFoundError` → reutilizează categoria `ACCESS_DENIED` (403)

Verificat: docstring-ul `ObjectionNotFoundError` ("nu există SAU nu aparține owner_id-ului dat
... mesaj identic pentru ambele cazuri, previne enumerare") e **aproape identic cuvânt cu
cuvânt** cu `FollowUpAccessDeniedError`. Deși numele clasei conține "NotFound", semantica e
"AccessDenied" — propun adăugarea ei în tuplul existent `ACCESS_DENIED_ERRORS`, nu crearea unei
categorii noi. **Nu introduce un handler nou** — doar extinde lista existentă.

### 3.2 `ValueError` (categorie invalidă la `/prepare`) → categorie NOUĂ, `400 INVALID_CATEGORY`

Nu există azi în `exception_handlers.py`. Apare doar dacă un client trimite o
`objection_category` din afara celor 13 — posibil doar dacă clientul ocolește
`/objections/categories`. E o eroare de input, nu de server → `400`, nu `500`. Propun un handler
nou, separat de cele 4 existente (nu se potrivește semantic cu niciuna).

### 3.3 `psycopg.errors.ForeignKeyViolation` (`conversation_id` inexistent la `/prepare`) → categorie NOUĂ, `400 INVALID_REFERENCE`

`owner_id` nu poate produce FK violation prin router — vine din JWT, deja validat de
`get_current_user()` (user-ul există în DB, verificat acolo). Doar `conversation_id` (opțional,
trimis liber de client) poate fi un UUID inexistent. E tot o eroare de input → `400`. Handler nou.

**Aceste două decizii (3.2, 3.3) sunt propuneri — au nevoie de confirmarea ta înainte de RED,
pentru că introduc categorii de eroare noi, nu doar extind una existentă.**

### 3.4 `BLOCK` — NU e eroare HTTP

Rezultatul `validation_level="BLOCK"` din `/confirm` e un răspuns **normal**, `200 OK`, cu
`persisted=false` în body. Nu ridică nicio excepție — `ConfirmResponseResponseSchema` deja
comunică starea. Routerul NU face nimic special pentru `BLOCK` — doar serializează rezultatul.

### 3.5 Tabel complet

| Excepție | Status | `error_code` | Handler |
|---|---|---|---|
| `ObjectionNotFoundError` | 403 | `ACCESS_DENIED` | reutilizează `handle_access_denied` existent |
| `ValueError` (categorie invalidă) | 400 | `INVALID_CATEGORY` | nou |
| `psycopg.errors.ForeignKeyViolation` | 400 | `INVALID_REFERENCE` | nou |
| Body Pydantic invalid (tip greșit, câmp lipsă) | 422 | — | automat FastAPI, neschimbat |

## 4. Regula de securitate — verificată explicit împotriva schemelor de mai sus

| Câmp | Sursă | Prezent în vreun `Request` schema? |
|---|---|---|
| `owner_id` | `CurrentUser.id` (JWT) | **NU** |
| `objection_category` (la `/confirm`) | `get_objection()` din DB | **NU** |
| `objection_text` (la `/confirm`) | `get_objection()` din DB | **NU** |
| `objection_id` | client | DA (`ConfirmResponseRequest`) |
| `response_text` | lider | DA |
| `response_variant_used` | lider | DA |

## 5. Routerul — schelet, subțire, fără logică

```python
router = APIRouter(prefix="/api/v1/objections", tags=["objections"])


@router.post("/analyze", response_model=AnalyzeObjectionResponse)
def analyze_objection(
    body: AnalyzeObjectionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    agent: ConversationAgent = Depends(get_conversation_agent),
):
    result = agent.analyze_objection(body.objection_text)
    return AnalyzeObjectionResponse(
        detected_category=result.detected_category,
        needs_manual_selection=result.needs_manual_selection,
    )


@router.get("/categories", response_model=CategoriesResponse)
def get_categories(
    current_user: CurrentUser = Depends(get_current_user),
    agent: ConversationAgent = Depends(get_conversation_agent),
):
    return CategoriesResponse(categories=agent.list_categories())


@router.post("/prepare", response_model=PrepareResponseOptionsResponse, status_code=201)
def prepare_response_options(
    body: PrepareResponseOptionsRequest,
    current_user: CurrentUser = Depends(get_current_user),
    agent: ConversationAgent = Depends(get_conversation_agent),
):
    result = agent.prepare_response_options(
        owner_id=current_user.id,
        objection_text=body.objection_text,
        objection_category=body.objection_category,
        conversation_id=body.conversation_id,
    )
    return PrepareResponseOptionsResponse(objection_id=result.objection.id, variants=result.variants)


@router.post("/confirm", response_model=ConfirmResponseResponseSchema)
def confirm_response(
    body: ConfirmResponseRequest,
    current_user: CurrentUser = Depends(get_current_user),
    agent: ConversationAgent = Depends(get_conversation_agent),
):
    result = agent.confirm_response(
        objection_id=body.objection_id,
        owner_id=current_user.id,
        response_text=body.response_text,
        response_variant_used=body.response_variant_used,
    )
    return ConfirmResponseResponseSchema(
        persisted=result.persisted,
        validation_level=result.validation_level,
        reason=result.reason,
    )
```

Observație: `owner_id` NU apare niciodată citit din `body` — doar din `current_user.id`,
identic cu pattern-ul `missions.py`.

## 6. Testarea — `TestClient`, `DATABASE_URL` real, autentificare reală

Fișier nou: `tests/test_objections_api.py`, urmând exact structura `test_mission_api.py`
(fixture `client`, `_create_authenticated_user`, `ensure_kpis_seeded` dacă e nevoie — de
verificat dacă `objections`/`ObjectionEngine` ating vreun KPI; până acum, nu).

Cazuri obligatorii:
1. Flux fericit complet: `/analyze` → `/categories` (dacă `needs_manual_selection`) → `/prepare`
   → `/confirm`, `PASS`, autentificat.
2. `/confirm` cu `BLOCK` → `200`, `persisted=false`, `reason` prezent.
3. **Izolare `owner_id` prin HTTP real**: User A creează prin `/prepare`, User B (JWT diferit)
   încearcă `/confirm` cu `objection_id`-ul lui A → `403 ACCESS_DENIED`.
4. `/prepare` cu `objection_category` invalidă → `400 INVALID_CATEGORY`.
5. `/prepare` cu `conversation_id` inexistent → `400 INVALID_REFERENCE`.
6. Fără header `Authorization` pe orice endpoint → `401` (comportament `get_current_user`,
   neschimbat, doar verificat că se aplică și aici).
7. `/confirm` cu `objection_id` inexistent → `403 ACCESS_DENIED` (identic cu cazul 3, motiv
   diferit, cod identic — previne enumerare).

## 7. Ce rămâne explicit în afara scopului

- UI-ul (Objection Workbench) — pas separat, după router.
- Gate-ul `VULNERABILITATE_IZOLARE` — moștenit nerezolvat din `21`/`22`.
- Rate limiting, paginare, orice funcție dincolo de cele 4 endpoint-uri.
