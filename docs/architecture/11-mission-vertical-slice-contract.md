# MISSION VERTICAL SLICE — IMPLEMENTATION CONTRACT v1

**Status:** verificat contra `02 → 03 → 06 → 08 → 09 → 04`, pregătit pentru cod
**Data:** 12 august 2026
**Scop:** primul lanț executabil real din NicMar OS

---

## 0. Regula de bază

Structura de cod reflectă arhitectura deja aprobată — nu inventează nimic nou. Fiecare verigă de mai jos citează sursa exactă.

---

## 1. Lanțul complet, verigă cu verigă

### 1.1 Event — `MissionGenerated`
- **Sursă:** `02`, linia 126 — *"System Event ➔ Pregătesc și afișează misiunea în Dashboard (MissionEngine, PriorityEngine)"*
- **Declanșator:** nu un eveniment de business anterior — generat la cerere zilnică (Dashboard load), la fel ca Contact/Partner Agent
- **Fișier:** `src/events/mission_events.py`
- **Payload:** `{owner_id, contact_id?, conversation_id?, partner_id?, client_id?}`

### 1.2 Workflow
- **Sursă:** `02` nu numește explicit un workflow pentru `MissionGenerated` (doar `WF-MISSION-START-001` pentru `MissionStarted`, linia 127)
- **Decizie de implementare:** workflow-ul de generare e intern la `MissionEngine.generate()`, nu un modul separat — nu inventăm un `WF-MISSION-GENERATE-001` nedocumentat

### 1.3 Rule — `RuleEngine`
- **Sursă:** `03`, secțiunile 5-6 (Rule Identity, Rule Ownership) — schema generică de regulă (`rule_code`, `owner_engine`, `target_object`, `conditions_json`, `decision_outcome`, `action_output`)
- **Notă:** nicio regulă prescriptivă reală pentru Mission în `03` — doar exemple ilustrative (`GENERATE_MISSION`, `MISSION_READY`/`MISSION_BLOCKED`). Pentru v1, implementăm o regulă minimă, explicită, **nu inventată din exemple**: *"dacă owner_id are < 1 misiune activă azi → decision_outcome = MISSION_READY"*
- **Fișier:** `src/engines/rule/rule_engine.py`
- **Tabel:** `rules` (o singură intrare inițială: `rule_code = 'RULE-MISSION-DAILY-001'`)

### 1.4 Engine — `MissionEngine` (`ENG-MISSION-001`)
- **Sursă:** `02`, linia 112 — Primary Engine, Domain Activity
- **Responsabilitate confirmată** (`05`): generare, atribuire, urmărire progres
- **Fișier:** `src/engines/mission/mission_engine.py`
- **Metode:** `generate(owner_id) -> Mission`, `transition(mission_id, new_status) -> Mission`

### 1.5 Data
- **Tabel principal:** `missions` — `status CHECK IN ('GENERATED','ASSIGNED','IN_PROGRESS','COMPLETED')` (`09`)
- **Tabele de suport:** `rule_evaluations` (rezultatul evaluării `RuleEngine`), `state_history` (fiecare tranziție), `events` (fiecare eveniment emis), `audit_log` (decizia motorului)
- **Fișier conexiune DB:** `src/data/db.py` (`psycopg`, conform deciziei de azi)

### 1.6 Agent — Mission Agent
- **Sursă:** `08`, Agent 4
- **Input:** Misiunea Zilei, progresul curent, disponibilitatea de timp
- **Output:** un singur pas concret (Legea Primului Pas)
- **Fișier:** `src/agents/mission/mission_agent.py`

### 1.7 Human confirmation
- **Sursă:** `08` — buton unic *"Sunt gata, încep"*, aliniat cu Competența 12
- **Implementare v1:** funcție `confirm(mission_id) -> bool`, apelată explicit — **niciodată automată**

### 1.8 Action — `MissionStarted` → `IN_PROGRESS`
- **Sursă:** `02`, linia 127 — `WF-MISSION-START-001`
- **Efect:** `missions.status = 'IN_PROGRESS'`, rând nou în `state_history`, eveniment `MissionStarted` în `events`

### 1.9 KPI — `DIS`
- **Sursă:** `02`, linia 128 — `MissionCompleted` actualizează `DIS` (+ *"Completion Rate, Consistency Score"* — **neconfirmate în registrul de 13 KPI, nu se implementează în v1**, semnalate pentru audit viitor)
- **Declanșator:** doar la `MissionCompleted`, nu la `MissionStarted`

### 1.10 Score persistence
- **Tabel:** `scores` (`09`, adăugat azi la G4)
- **Scriere:** `{kpi_id: <DIS>, entity_type: 'mission', entity_id: mission_id, score_value, engine_source: 'MissionEngine'}`
- **Precondiție:** `kpis` trebuie populat cu cele 13 KPI înainte de prima scriere în `scores` (seed data)

---

## 2. Structura de fișiere — reflectă arhitectura, nu o reinventează

```
src/
├── engines/
│   ├── mission/
│   │   ├── __init__.py
│   │   └── mission_engine.py
│   └── rule/
│       ├── __init__.py
│       └── rule_engine.py
├── agents/
│   └── mission/
│       ├── __init__.py
│       └── mission_agent.py
├── events/
│   ├── __init__.py
│   └── mission_events.py
├── data/
│   ├── __init__.py
│   └── db.py
├── llm/            (existent, neatins)
└── runtime/        (existent, neatins)
```

**Notă:** niciun `workflows/` separat pentru v1 — justificat la 1.2, nu se creează structură pentru ceva nedocumentat explicit.

---

## 3. Ce rămâne explicit în afara v1

- `PriorityEngine` — capability locală, dacă apare nevoie, la nivel de `MissionAgent`, nu motor separat (aceeași regulă de la Partner, P11)
- `MissionSkipped`/`Expired`/`Reassigned` — FOLLOW-UP, cum a fost decis (P10)
- `HabitEngine`, `PerformanceEvaluationEngine` — menționate de `02` la `MissionCompleted`, dar non-MVP — nu le implementăm, doar scriem `DIS` direct

---

## 4. Ordinea de scriere a codului

1. `src/data/db.py` — conexiune, fără logică de business
2. `src/engines/rule/rule_engine.py` — regula minimă (1.3)
3. `src/engines/mission/mission_engine.py` — `generate()`, `transition()`
4. `src/agents/mission/mission_agent.py` — citește misiunea, produce pasul unic
5. Test izolat: `MissionGenerated → GENERATED → confirmare → IN_PROGRESS`

---
*Contract verificat. Următorul pas: scriere cod, în ordinea de la secțiunea 4, cu verificare izolată după fiecare fișier.*
