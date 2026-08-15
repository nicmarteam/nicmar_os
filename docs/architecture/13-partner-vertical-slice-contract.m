# PARTNER VERTICAL SLICE — IMPLEMENTATION CONTRACT v1

**Status:** verificat contra `02 → 03 → 05 → 06 → 08 → 09 → 04`
**Data:** 12 august 2026

---

## 0. Corectură de consecvență (înainte de contract)

`ENG-PRE-001` și `ENG-MISSION-001` apar **ambele** doar ca valori de exemplu în `03` (secțiunea "Rule Ownership", sub "Exemplu:"), aceeași categorie de încredere ca `ENG-FOLLOWUP-XXX` (marcat "neconfirmat" în Contact→FollowUp Slice). `mission_engine.py` a numit `ENG-MISSION-001` "confirmat" — retrospectiv, imprecis. Pentru Partner, tratăm `ENG-PRE-001` corect: **plauzibil, nu confirmat**. (Corectarea docstring-ului din `mission_engine.py` rămâne FOLLOW-UP, nu se face acum fără aprobare separată.)

---

## 1. Lanțul, verigă cu verigă

### 1.1 Event/trigger
- **Sursă:** `05`, Competența 27, Ecranul 1 — *"Astăzi ai 2 parteneri care au nevoie de tine"* — verificare zilnică, nu eveniment de sistem
- La fel ca Contact/Mission Agent — rulează la cerere (Dashboard), nu declanșat de eveniment extern

### 1.2 Rule — `RuleEngine`, regulă nouă
- **`RULE-PARTNER-DIAGNOSTIC-001`** — decizie minimă, prin analogie cu tiparul deja stabilit (Mission, FollowUp): *"dacă partenerul nu a primit deja un diagnostic azi → `PARTNER_READY`, altfel `PARTNER_ALREADY_DIAGNOSED`"*
- **Asumpție explicită, nu din sursă directă**: sursa nu spune clar "nu repeta diagnosticul de 2 ori pe zi" — e o extensie a principiului deja aplicat (Mission: nu 2 misiuni simultan; FollowUp: nu duplicate). Semnalată, nu ascunsă.

### 1.3 Engine — `PartnerRelationshipEngine`
- **Sursă:** `02`, linia 909 — State Owner confirmat
- **Cod:** `ENG-PRE-001` — plauzibil (v. secțiunea 0), nu pe deplin confirmat

### 1.4 Data — fără tabel nou
- **`partners`** — existent, neschimbat
- **Urmărirea "diagnostic deja făcut azi"**: reutilizăm `events` (generic) — eveniment `PartnerDiagnosticGenerated`, verificat prin `target_object_id = partner_id AND created_at::date = CURRENT_DATE`. Nu creăm tabel nou.

### 1.5 KPI — `PDI`, `PIP`
- **Sursă:** `05`, Ecranul 8 — *"Se recalculează automat Partner Development Index (PDI)"*, **după** trimiterea mesajului (Ecranul 7), nu la generarea diagnosticului
- **Diferență față de FollowUp** (persistat la creare): aici KPI se persistă **la finalizarea completă a interacțiunii**, nu la început — verificat din sursă, nu presupus prin analogie

### 1.6 Agent — Partner Agent
- **Sursă:** `08`, Agent 5
- **Output real, v1:** diagnostic calitativ (4 variante fixe, din `05` — nu inventăm altele) + **mesaj generat = STUB**, nu conținut AI real. Generarea de mesaj necesită integrare LLM, în afara scope-ului acestui vertical slice (contractul Mission/FollowUp n-a avut nevoie de generare de conținut liber; Partner da — semnalat explicit, nu implementat acum)
- **Dual HITL:** alegere direcție emoțională + confirmare mesaj (simulată în v1 ca parametru `confirmed: bool`, la fel ca restul)

---

## 2. Ce NU implementăm acum (semnalat, nu ascuns)

- Generarea reală a mesajului (necesită LLM — rămâne stub, returnează text fix)
- `AMS`, `LRI` — Nic a confirmat explicit doar `PDI`+`PIP` pentru Partner Agent
- `PriorityEngine` complet — "Priority capability" la nivel de Agent, ca la P11, folosind doar `PDI` + timp de la ultima interacțiune

---

## 3. Structura de fișiere

```
src/
├── engines/
│   └── partner/
│       ├── __init__.py
│       └── partner_engine.py
├── agents/
│   └── partner/
│       ├── __init__.py
│       └── partner_agent.py
```

---
*Contract verificat. Generarea de mesaj = stub explicit, nu funcționalitate reală.*
