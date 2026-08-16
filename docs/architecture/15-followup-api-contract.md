# FOLLOWUP API CONTRACT — v1

**Status:** verificat direct față de semnăturile reale (`src/engines/followup/followup_engine.py`, `src/agents/followup/followup_agent.py`)
**Data:** 12 august 2026 (continuare, aceeași sesiune)
**Precedent:** aceeași structură ca `14-api-contract.md` (Mission), aceeași disciplină de validare

---

## 0. Avertisment de securitate — identic cu Mission API

`owner_id` vine explicit din request, nu din identitate autentificată. Rămâne valabil până la Auth (secțiunea 0, `14-api-contract.md`).

---

## 1. Gol descoperit înainte de implementare — necesită decizie

**Nu există nicio metodă în `FollowUpEngine` care să listeze follow-up-urile unui owner.** `FollowUpAgent.present_followup_list(followups: List[FollowUp])` primește deja o listă gata construită — nimic din cod nu citește lista din PostgreSQL.

**Consecință:** endpoint-ul `GET /api/v1/followups?owner_id={uuid}` (planificat în `14-api-contract.md`, secțiunea 4) nu poate fi implementat fără o metodă nouă, minimă, de tipul:
```python
def list_pending_followups(self, owner_id: UUID) -> List[FollowUp]
```
**Nu o adaug acum** — aștept confirmare, la fel cum am cerut aprobare pentru `get_mission` înainte de a-l scrie.

---

## 2. Endpoint-uri — verificate față de semnăturile reale

### `POST /api/v1/followups`
Echivalent cod: `FollowUpEngine.create_from_trigger(owner_id, contact_id, conversation_id)` — apelat direct (fără metodă `Agent` de creare, la fel ca Mission)

**Request:**
```json
{"owner_id": "uuid", "contact_id": "uuid", "conversation_id": "uuid"}
```
**Response 201:** `{"id", "owner_id", "contact_id", "conversation_id", "status": "PENDING"}`
**Erori:** `409 ALREADY_EXISTS` (`FollowUpDuplicateError` — conversație cu PENDING deja existent)

---

### `GET /api/v1/followups?owner_id={uuid}` — **BLOCAT de golul din secțiunea 1**
Necesită metoda nouă `list_pending_followups`, apoi `FollowUpAgent.present_followup_list`.

---

### `POST /api/v1/followups/{followup_id}/complete`
Echivalent: `FollowUpAgent.confirm_completion(followup_id, owner_id, confirmed)`
**Erori:** `403 ACCESS_DENIED`, `400 CONFIRMATION_REQUIRED`, `400 INVALID_TRANSITION`

### `POST /api/v1/followups/{followup_id}/postpone`
Echivalent: `FollowUpAgent.request_postpone(followup_id, owner_id)` — **fără `confirmed`** (verificat: semnătura reală nu-l are, la fel ca `assign_mission`)

### `POST /api/v1/followups/{followup_id}/reschedule`
Echivalent: `FollowUpAgent.request_reschedule(followup_id, owner_id)` — fără `confirmed`

### `GET /api/v1/followups/dis-score?owner_id={uuid}`
Echivalent: `FollowUpAgent.get_recent_dis_score(owner_id)` — READ-ONLY

---

## 3. Toate path params `UUID` de la început

Lecția de la Mission API (`present`/`start`/`complete` inițial `str`, aliniate ulterior) se aplică direct — `followup_id: UUID` peste tot, din prima versiune, nu corectat ulterior.

---

## 4. Ordinea de implementare

1. Decizie: adăugăm `list_pending_followups` acum sau amânăm `GET /followups` pentru mai târziu?
2. Restul de 4 endpoint-uri (create, complete, postpone, reschedule, dis-score) — nu depind de gol, se pot construi imediat
3. Teste: unitare + PostgreSQL real + izolare 2 lideri + anti-duplicare + ID invalid → 422 (toate din prima, nu în 2 runde ca la Mission)
4. Regresie completă (79 teste existente rămân verzi)

---
*Contract verificat. Un gol real găsit (lista de follow-up-uri) — semnalat, nu completat fără aprobare.*
