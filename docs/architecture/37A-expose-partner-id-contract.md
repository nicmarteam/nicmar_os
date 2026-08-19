# Decizia 37A — Expunere `partner_id` în ContactSummary

Status: APPROVED (owner, 19 august 2026)

## 1. Context

Auditul Deciziei 37 (Partner Workbench) a găsit un gol: `partner_id`
este citit intern de `ContactAgent._fetch_contacts()` (coloana `p.id`,
folosită azi doar pentru mapare PDI/PIP), dar nu e expus niciodată
public în `ContactSummary` / `ContactSummaryResponse`. Fără el,
Workbench-ul nu poate apela `POST /partners/{id}/diagnostic` sau
`POST /partners/{id}/send` pentru un contact convertit reîncărcat
dintr-o sesiune nouă.

## 2. Verificări de audit (blocante, ambele închise)

- `partners.contact_id` este `UUID UNIQUE NOT NULL` (migration
  `001_initial_schema.sql`) — relația Contact → Partner e strict 1:1
  la nivel DB. Zero risc de ambiguitate la `p.id`.
- `PartnerEngine._verify_ownership()` verifică real, în DB,
  `partner_id` + `owner_id` înainte de orice operație pe Partner,
  confirmat prin teste HTTP reale (`test_diagnostic_wrong_jwt_owner_returns_403`,
  `test_send_wrong_jwt_owner_returns_403`) și teste de engine
  (`PartnerAccessDeniedError`).

## 3. Scope

Domeniu:
- `src/agents/contact/contact_agent.py` — `ContactSummary`
- `src/api/schemas.py` — `ContactSummaryResponse`
- `src/api/routers/contacts.py` — trecerea câmpului către response
  (necesară mecanic: router-ul construiește `ContactSummaryResponse`
  câmp cu câmp, nu prin `asdict()`)
- `tests/test_contact_agent.py`, `tests/test_contacts_api.py`

Explicit exclus (neatins):
- `PartnerEngine`, `PartnerAgent`, `src/api/routers/partners.py`
- `PartnerScoresResponse` / `GET /partners/scores`
- Workbench (frontend)

## 4. Modificare

`partner_id: Optional[UUID]` — nou câmp, populat cu valoarea deja
citită la poziția 7 din `_ContactRow` (`None` dacă `converted_to !=
"partner"`).

## 5. Criterii de acceptare (RED)

1. Contact convertit (`converted_to == "partner"`) → `partner_id`
   este exact UUID-ul partenerului asociat (nu doar "not None").
2. Contact neconvertit → `partner_id is None`.
3. Ownership: liderul B nu primește niciodată `partner_id` al unui
   contact/partener al liderului A — verificat la nivel de rezultat
   (agent + HTTP real), nu doar prin prezența filtrului `owner_id` în
   SQL.
