# API CONTRACT — v1

**Status:** verificat direct față de semnăturile reale din cod (`src/agents/*.py`, `src/engines/*.py`)
**Data:** 12 august 2026 (continuare, aceeași sesiune)
**Numerotare corectată:** `13` era deja folosit (`13-partner-vertical-slice-contract.md`) — acest document devine `14-api-contract.md`.

---

## 0. Avertisment de securitate temporar — citit înainte de orice altceva

Ordinea de lucru stabilită e explicit: **API → teste → CI → Auth**. Asta înseamnă că, până la pasul Auth, **`owner_id` vine direct din request-ul clientului** (body sau header), nu dintr-o sesiune autentificată verificată de server.

**Consecință reală:** oricine poate trimite orice `owner_id` și poate acționa ca acel lider. Corectura din `MissionAccessDeniedError`/`FollowUpAccessDeniedError`/`PartnerAccessDeniedError` protejează împotriva accesării datelor **altui `owner_id`**, dar nu împotriva **impersonării** unui `owner_id` — cineva poate încă pretinde că e Lider B, doar completând `owner_id`-ul lui în request.

**Acest API nu trebuie expus public** înainte de pasul Auth. Rămâne marcat explicit ca etapă intermediară, nu ca stare finală sigură.

---

## 1. Principii generale

- **Format:** JSON, request și response
- **Autentificare:** absentă în v1 (v. avertismentul de mai sus) — `owner_id` explicit în fiecare request
- **Eroare standard:** fiecare eroare de business (excepțiile deja definite în `Engine`) se mapează la un cod HTTP + JSON cu `error_code` și `message`
- **Niciun endpoint nu ocolește Agent-ul** — API-ul apelează exclusiv metodele `Agent` deja testate, nu `Engine` direct (păstrează regula "Agent nu devine al doilea Engine", aplicată azi la toate cele 3 slice-uri)

---

## 2. Maparea erorilor — comună tuturor endpoint-urilor

| Excepție Python (deja existentă în cod) | Cod HTTP | `error_code` |
|---|---|---|
| `MissionNotReadyError` / `FollowUpDuplicateError` / `PartnerDiagnosticAlreadyGeneratedError` | 409 Conflict | `ALREADY_EXISTS` |
| `MissionAccessDeniedError` / `FollowUpAccessDeniedError` / `PartnerAccessDeniedError` | 403 Forbidden | `ACCESS_DENIED` |
| `InvalidTransitionError` / `InvalidDiagnosticTypeError` | 400 Bad Request | `INVALID_TRANSITION` |
| `HumanConfirmationRequiredError` | 400 Bad Request | `CONFIRMATION_REQUIRED` |
| Eroare neprevăzută | 500 Internal Server Error | `INTERNAL_ERROR` |

---

## 3. Endpoint-uri — Mission (primul de implementat)

### `POST /api/v1/missions`
Echivalent cod: `MissionEngine.generate_mission(owner_id, title)` — apelat direct (nu există metodă `Agent` de generare, doar de prezentare/confirmare — verificat, `MissionAgent` nu are `generate`)

**Request:**
```json
{"owner_id": "uuid", "title": "string"}
```
**Response 201:**
```json
{"id": "uuid", "owner_id": "uuid", "title": "string", "status": "GENERATED"}
```
**Erori:** `409 ALREADY_EXISTS` (dacă owner are deja misiune activă azi)

---

### `GET /api/v1/missions/{mission_id}/present?owner_id={uuid}`
Echivalent cod: `MissionAgent.present_daily_mission(mission)` — necesită mai întâi citirea misiunii (verificat: metoda primește obiectul `Mission`, nu doar ID — API-ul trebuie să-l citească din DB întâi)

**Response 200:**
```json
{"text": "Pasul tău de azi: <title>"}
```

---

### `POST /api/v1/missions/{mission_id}/start`
Echivalent cod: `MissionAgent.confirm_and_start(mission_id, owner_id, confirmed)`

**Request:**
```json
{"owner_id": "uuid", "confirmed": true}
```
**Response 200:** obiectul `Mission`, `status: "IN_PROGRESS"`
**Erori:** `403 ACCESS_DENIED`, `400 CONFIRMATION_REQUIRED`, `400 INVALID_TRANSITION`

---

### `POST /api/v1/missions/{mission_id}/complete`
Echivalent cod: `MissionAgent.confirm_completion(mission_id, owner_id)`

**Request:**
```json
{"owner_id": "uuid"}
```
**Response 200:** obiectul `Mission`, `status: "COMPLETED"` — persistă și `DIS` (placeholder, cum e deja în cod)

---

### `GET /api/v1/missions/dis-score?owner_id={uuid}`
Echivalent cod: `MissionAgent.get_recent_dis_score(owner_id)` — READ-ONLY

**Response 200:**
```json
{"dis_score": 1.0}
```

---

## 4. Endpoint-uri — FollowUp (structură identică, pentru referință)

| Endpoint | Echivalent cod |
|---|---|
| `GET /api/v1/followups?owner_id={uuid}` | listă, ordonată — Agent nu calculează RPS (v. limitare deja documentată) |
| `POST /api/v1/followups/{id}/complete` | `FollowUpAgent.confirm_completion` |
| `POST /api/v1/followups/{id}/postpone` | `FollowUpAgent.request_postpone` |
| `POST /api/v1/followups/{id}/reschedule` | `FollowUpAgent.request_reschedule` |
| `GET /api/v1/followups/dis-score?owner_id={uuid}` | `FollowUpAgent.get_recent_dis_score` |

## 5. Endpoint-uri — Partner (structură identică, pentru referință)

| Endpoint | Echivalent cod |
|---|---|
| `POST /api/v1/partners/{id}/diagnostic` | `PartnerAgent.request_diagnostic` — necesită `diagnostic_type` în body |
| `POST /api/v1/partners/{id}/send` | `PartnerAgent.confirm_and_send` |
| `GET /api/v1/partners/scores?owner_id={uuid}` | `PartnerAgent.get_recent_scores` |

---

## 6. Ce NU construim acum (scop clar delimitat)

- Endpoint pentru `assign_mission` — nu are corespondent în `MissionAgent` (doar `Engine`); rămâne apelat intern, nu expus API, până se decide dacă merită endpoint propriu
- Autentificare reală — pas separat (5)
- Rate limiting, CORS, validare de schemă avansată — infrastructură post-MVP

---

## 7. Ordinea de implementare, confirmată

1. Framework HTTP (de ales — nu presupun încă unul, întreb înainte de cod)
2. Endpoint-urile Mission (secțiunea 3), primele
3. Teste: unitare (routing + serializare) + integrare (cu `FakeDB`, ca la Engine) + PostgreSQL real + izolare 2 lideri
4. CI extins cu noile teste
5. FollowUp + Partner, după ce Mission e complet verificat

---
*Contract verificat față de semnăturile reale din `src/agents/*.py`. Avertismentul de securitate din secțiunea 0 rămâne activ până la implementarea Auth.*
