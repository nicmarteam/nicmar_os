# PARTNER API CONTRACT — v1

**Status:** verificat direct față de semnăturile reale (`src/engines/partner/partner_engine.py`, `src/agents/partner/partner_agent.py`)
**Data:** 12 august 2026 (continuare, aceeași sesiune)
**Atenție specială:** regula critică descoperită azi — `_verify_ownership(partner_id, owner_id)` — trebuie demonstrată prin HTTP + PostgreSQL real, nu doar unitar

---

## 0. Avertisment de securitate — identic cu Mission/FollowUp API

`owner_id` vine explicit din request. Rămâne valabil până la Auth.

---

## 1. Diferență structurală importantă față de Mission/FollowUp

**`PartnerAgent.confirm_and_send()` returnează `None`**, nu un obiect Partner/diagnostic actualizat — spre deosebire de `MissionAgent.confirm_completion()` sau `FollowUpAgent.confirm_completion()`, care returnează obiectul cu starea nouă.

**Motiv verificat:** Partner nu are o mașină de stări tranzițională la acest pas (diagnosticul + trimiterea nu schimbă `partners.status`) — doar persistă `PDI`+`PIP` în `scores`. Nu există "stare nouă" de returnat.

**Decizie pentru API:** endpoint-ul `/send` returnează un răspuns de confirmare simplu (`{"status": "sent"}`), nu un obiect Partner. Alternativ, am putea apela `PartnerAgent.get_recent_scores(owner_id)` după confirmare și returna scorurile proaspăt persistate — **aleg această a doua variantă**, mai utilă pentru un Dashboard (confirmă vizual că PDI/PIP chiar s-au scris).

---

## 2. Endpoint-uri

### `POST /api/v1/partners/{partner_id}/diagnostic`
Echivalent: `PartnerAgent.request_diagnostic(partner_id, owner_id, diagnostic_type)`

**Request:**
```json
{"owner_id": "uuid", "diagnostic_type": "ENCOURAGEMENT"}
```
`diagnostic_type` trebuie să fie unul din: `ENCOURAGEMENT`, `CLARITY`, `APPRECIATION`, `NEXT_STEP` (verificat din sursă, `VALID_DIAGNOSTIC_TYPES`)

**Response 201:**
```json
{"partner_id": "uuid", "owner_id": "uuid", "diagnostic_type": "ENCOURAGEMENT", "message": "[STUB] ..."}
```
**Erori:**
- `403 ACCESS_DENIED` (`PartnerAccessDeniedError` — **verificare de ownership rulează PRIMA**, înaintea oricărei alte verificări, conform corecturii de azi)
- `409 ALREADY_EXISTS` (`PartnerDiagnosticAlreadyGeneratedError`)
- `400 INVALID_TRANSITION` (`InvalidDiagnosticTypeError`, dacă `diagnostic_type` invalid)

---

### `POST /api/v1/partners/{partner_id}/send`
Echivalent: `PartnerAgent.confirm_and_send(partner_id, owner_id, confirmed)` — apoi `get_recent_scores(owner_id)` (v. secțiunea 1)

**Request:**
```json
{"owner_id": "uuid", "confirmed": true}
```
**Response 200:**
```json
{"pdi": 1.0, "pip": 1.0}
```
**Erori:** `403 ACCESS_DENIED` (verificare ownership, PRIMA), `400 CONFIRMATION_REQUIRED`

---

### `GET /api/v1/partners/scores?owner_id={uuid}`
Echivalent: `PartnerAgent.get_recent_scores(owner_id)` — READ-ONLY, deja verificat azi cu `JOIN partners` corect (bug găsit și reparat)

**Response 200:**
```json
{"pdi": 1.0, "pip": 1.0}
```

---

## 3. Testare specială cerută — ownership demonstrat prin HTTP + PostgreSQL real

Nu ne mulțumim cu teste unitare cu mock. Testul decisiv:
```
Lider A creează Partner propriu (owner_id = A)
Lider B încearcă POST /diagnostic pe partner_id-ul lui A, cu owner_id = B
    → 403 ACCESS_DENIED, verificat cu request HTTP real, pe PostgreSQL real
```
Exact bug-ul #4 găsit azi (impersonare parțială prin `partner_id` nepotrivit) — de data asta verificat și la nivel HTTP, nu doar Engine direct.

---

## 4. `partner_id: UUID` din prima versiune

Aceeași disciplină ca la FollowUp (nicio corectură ulterioară necesară, ca la Mission).

---

## 5. Ce NU construim acum

- Selecția automată a `diagnostic_type` (nu există formulă în sursă — clientul alege explicit, la fel ca în cod)
- Ecranul 4 (5 direcții emoționale) — rămâne FOLLOW-UP, ca și în `PartnerAgent`

---
*Contract verificat. Diferența de tip de răspuns la `/send` explicată și decisă, nu inventată arbitrar.*
