# CONTACT → FOLLOWUP VERTICAL SLICE — IMPLEMENTATION CONTRACT v1

**Status:** verificat contra `02 → 03 → 06 → 08 → 09 → 04`, pregătit pentru cod
**Data:** 12 august 2026
**Precedent:** aceeași disciplină ca `11-mission-vertical-slice-contract.md` — verificat, apoi cod, apoi 3 verificări, apoi test de integrare stateful

---

## 1. Lanțul complet, verigă cu verigă

### 1.1 Event — `FollowUpTriggered`
- **Sursă:** `02`, linia 820-826 (bloc detaliat, autoritate stabilită azi la audit G1)
- **Trigger:** Conversation, tranziție `Waiting → FollowUpNeeded`
- **Motoare care reacționează:** `FollowUpEngine`, `MissionEngine` — ambele confirmate MVP
- **Fișier:** `src/events/followup_events.py`

### 1.2 Workflow
- **Sursă:** `WF-FOLLOWUP-CREATE-001` (`02`, linia 826)
- **Decizie de implementare:** ca la Mission, workflow-ul e intern la `FollowUpEngine.create_from_trigger()`, nu modul separat

### 1.3 Rule — `RuleEngine`
- **Sursă:** `03` — doar vocabular ilustrativ (`FOLLOWUP_REQUIRED`, `REQUEST_FOLLOWUP`, `CREATE_FOLLOW_UP`), nicio regulă prescriptivă reală
- **Regulă minimă pentru v1** (explicită, nu inventată din exemple): *"dacă o Conversation e în `FOLLOWUP_NEEDED` și nu are deja un `follow_up` cu `status='PENDING'` asociat → `FOLLOWUP_READY`, altfel `FOLLOWUP_DUPLICATE`"*
- **Rule code:** `RULE-FOLLOWUP-DUPLICATE-001`
- **Reutilizare:** aceeași clasă `RuleEngine` din Mission Slice, o metodă nouă, nu un motor nou

### 1.4 Engine — `FollowUpEngine`
- **Sursă:** `02`, linia 9 (Pilonul FollowUp în `06-harta-motoare-tehnice.md`), motor MVP confirmat (Decizia inițială, nu Decizia 2)
- **Cod oficial:** ⚠️ **neconfirmat** — nu există `ENG-FOLLOWUP-XXX` în `03` (spre deosebire de `ENG-MISSION-001`, `ENG-PRE-001`). Nu inventăm unul — îl las necompletat în cod, marcat explicit.
- **Responsabilitate confirmată** (`05`): *"organizează relațiile active... detectează relațiile inactive... generează următorul follow-up"*
- **Fișier:** `src/engines/followup/followup_engine.py`
- **Metode:** `create_from_trigger(conversation_id, contact_id, owner_id) -> FollowUp`, `transition(followup_id, new_status) -> FollowUp`

### 1.5 Data
- **Tabel principal:** `follow_ups` — `status CHECK IN ('PENDING','COMPLETED','POSTPONED','RESCHEDULED')` (`09`, corectat azi la G3)
- **Tabele de suport:** `rule_evaluations`, `state_history`, `events`, `audit_log` — identic cu Mission Slice
- **Fișier conexiune:** `src/data/db.py` — **reutilizat, nu duplicat**

### 1.6 KPI — `DIS`, nu `RPS`
- **Sursă:** `02`, linia 826 — `FollowUpTriggered` influențează `DIS`
- **`RPS` — exclus explicit** (Decizia G2, azi): scor operațional de ordonare, nu KPI oficial. **Nu se persistă în `scores`.**
- **Persistență:** `kpis` + `scores`, identic cu Mission Slice (G4) — niciun tabel nou

### 1.7 Agent — FollowUp Agent
- **Sursă:** `08`, Agent 3
- **Input:** FollowUp-uri programate, timp scurs de la ultima interacțiune, `RPS` (folosit doar pentru *ordonare în memorie*, niciodată persistat)
- **Output:** listă de follow-up-uri de azi, ordonate după prioritate
- **Fișier:** `src/agents/followup/followup_agent.py`

### 1.8 Human confirmation
- **Sursă:** `08` — *"liderul confirmă fiecare follow-up înainte să fie marcat ca realizat"*
- **Implementare:** `confirm_completed(followup_id, confirmed: bool)` — parametru explicit, fără valoare implicită, identic cu tiparul `start_mission(confirmed: bool)`

### 1.9 Regula arhitecturală, identică cu Mission Slice
`FollowUpAgent` nu devine al doilea `FollowUpEngine`. Citește, prezintă, cere confirmare, deleagă. Orice scriere trece exclusiv prin `FollowUpEngine`.

---

## 2. Diferențe reale față de Mission Slice (nu presupuse, verificate)

| Aspect | Mission Slice | Contact→FollowUp Slice |
|---|---|---|
| Cod oficial motor | `ENG-MISSION-001` (confirmat) | ⚠️ neconfirmat — lăsat necompletat |
| KPI | `DIS`, formulă placeholder | `DIS` (formulă placeholder) + `RPS` explicit exclus din persistență |
| Regulă | `RULE-MISSION-DAILY-001` (owner < 1 misiune activă) | `RULE-FOLLOWUP-DUPLICATE-001` (evită duplicate pe aceeași conversație) |
| Motoare la eveniment | doar `MissionEngine` (indirect) | **2 motoare reacționează** (`FollowUpEngine` + `MissionEngine`) — v1 implementează doar `FollowUpEngine`; interacțiunea cu `MissionEngine` la acest eveniment rămâne FOLLOW-UP, nu inventăm logică nedocumentată |

---

## 3. Structura de fișiere — extensie, nu duplicare

```
src/
├── data/
│   └── db.py                          (existent, reutilizat)
├── engines/
│   ├── rule/
│   │   └── rule_engine.py             (existent, extins cu 1 metodă nouă)
│   ├── mission/                       (existent, neatins)
│   └── followup/
│       ├── __init__.py
│       └── followup_engine.py         (NOU)
├── agents/
│   ├── mission/                       (existent, neatins)
│   └── followup/
│       ├── __init__.py
│       └── followup_agent.py          (NOU)
```

---

## 4. Ordinea de scriere

1. Extindem `rule_engine.py` — metodă nouă `evaluate_followup_readiness()`, fără să atingem regula Mission existentă
2. `src/engines/followup/followup_engine.py`
3. `src/agents/followup/followup_agent.py`
4. Test de integrare stateful, extins din `test_integration_mission_slice.py`

---
*Contract verificat. Motor fără cod oficial (`FollowUpEngine`) — semnalat, nu inventat.*
