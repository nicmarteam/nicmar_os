# KPI DEPENDENCY MAP — v1

**Status:** verificat exhaustiv, direct din `main`, comenzi reale — nicio presupunere
**Data:** 12 august 2026 (continuare, aceeași sesiune)
**Scop:** stabilește ordinea reală de implementare a celor 13 KPI, pe baza fezabilității tehnice constatate, nu pe ordinea din `04-KPI-REG-001.md`

---

## 0. Distincție critică — nu amestecăm 2 lucruri diferite

**Dependență inter-KPI** (KPI-ul X are nevoie de valoarea altui KPI ca input) ≠ **Blocaj tehnic propriu** (KPI-ul X are nevoie de un motor/tabel/eveniment care nu există).

Verificat: **doar `AMS` și `OPI` au dependențe inter-KPI reale** (documentate explicit în `04`: `AMS` cere *"OPI + toți ceilalți 11 KPI"*, `OPI` cere *"toți cei 12 KPI operaționali"*). Toți ceilalți 11 KPI sunt **independenți unul de altul** — blocajele lor sunt proprii (motor lipsă, eveniment lipsă), nu inter-condiționate.

**Consecință:** ordinea de mai jos e o **ierarhie de fezabilitate** (cât de aproape e fiecare de a fi construibil), nu o ordine impusă de dependențe — cu excepția `AMS`/`OPI`, care sunt structural ultimele, indiferent de orice altceva.

---

## 1. Fapte de bază, valabile pentru tot documentul

| Categorie | Ce există real, verificat în cod |
|---|---|
| Motoare | `MissionEngine`, `FollowUpEngine`, `PartnerEngine`, `RuleEngine` — doar 4 |
| Evenimente | 10 total: `MissionGenerated/Assigned/Started/Completed`, `FollowUpTriggered/Completed/Postponed/Rescheduled`, `PartnerDiagnosticGenerated/InteractionCompleted` |
| Tabele cu schemă dar goale prin construcție (nimic nu scrie) | `clients`, `objections`, `meetings` |
| Business Objects fără niciun tabel | `Habit`, `Assessment`, `Experience`, `Team`, `Leader` |
| Mecanism de persistență KPI | `kpis`+`scores` — funcțional, dar scrie doar placeholder `1.0` unde e folosit (`DIS` via Mission/FollowUp, `PDI`/`PIP` via Partner) |

---

## 2. Harta completă, KPI cu KPI

### KPI-001 — DIS (Daily Impact Score)
- **Componente:** Activități finalizate ✅, Impact ❌, Timp ⚠️, Prioritate ⚠️
- **Date necesare:** `state_history` (timp), `contacts.created_at` (vechime relație), `events` (frecvență), `follow_ups.status` (responsivitate) — toate reale
- **Tabele:** existente, folosite parțial
- **Evenimente:** `MissionCompleted`, `FollowUpCompleted`, `PartnerInteractionCompleted` (definite azi ca "finalizare reală")
- **Motor:** `MissionEngine`/`FollowUpEngine` există; `PriorityEngine` lipsește complet
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** **Impact — definiție operațională lipsă** (nu date, concept)
- **Nivel de fezabilitate:** 1 — cel mai aproape

### KPI-002 — ORE (Objection Resolution Effectiveness)
- **Componente:** nespecificate în sursă
- **Date necesare:** nedefinite
- **Tabele:** `objections` — schemă completă, **goală** (nimic nu scrie)
- **Evenimente:** `ObjectionRaised` menționat în `02`, nu există în cod
- **Motor:** `ObjectionEngine`, `RelationshipEngine` — ambele lipsă
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** motor + formulă, dar bază de date pregătită
- **Nivel de fezabilitate:** 2

### KPI-003 — CRH (Customer Relationship Health)
- **Componente:** nespecificate
- **Date necesare:** nedefinite
- **Tabele:** `contacts`/`conversations` reale; `clients`/`meetings` goale; `Experience`/`Assessment` inexistente
- **Evenimente:** nespecificate explicit
- **Motor:** 0/4 (`RelationshipEngine`, `ContinuityEngine`, `PerformanceEvaluationEngine` lipsă; `FollowUpEngine` există dar nu calculează sănătate)
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** motor + formulă + 2 Business Objects fără tabel
- **Nivel de fezabilitate:** 3

### KPI-004 — PDI (Partner Development Index)
- **Componente:** nespecificate
- **Date necesare:** doar placeholder `1.0` scris azi
- **Tabele:** `partners` real; `Habit`/`Assessment`/`Experience`/`Team`/`Leader` inexistente (5/9 Business Objects)
- **Evenimente:** 0/7 specificate există (`PartnerActivated`, `OnboardingCompleted`, `FirstResultAchieved`, `AutonomyReached`, `LeadershipActivated`, `PartnerReactivated`, `InactivityDetected`)
- **Motor:** `PartnerEngine` există, nu implementează logică PDI
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** evenimente + formulă + 5 tabele lipsă
- **Nivel de fezabilitate:** 4

### KPI-005 — PIP (Partner Integration Progress)
- **Componente:** nespecificate
- **Date necesare:** doar placeholder `1.0`
- **Tabele:** ca la PDI
- **Evenimente:** 0/4 specificate există (`PartnerActivated`, `OnboardingStarted`, `OnboardingCompleted`, `OnboardingTimeout`)
- **Motor:** `PartnerEngine`, aceeași limitare ca PDI
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** identic cu PDI
- **Nivel de fezabilitate:** 4 (egal cu PDI)

### KPI-006 — OAS (Onboarding Activation Success)
- **Componente:** nedefinite — sursa însăși spune *"definiția semantică extinsă e încă în lucru"*
- **Date/Tabele/Evenimente:** nespecificate
- **Motor:** `PerformanceEvaluationEngine` — lipsă
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** conceptual, nu doar tehnic
- **Nivel de fezabilitate:** 5

### KPI-007 — ERI (Experience Reuse Index)
- **Componente:** nedefinite — marcat explicit "TBD" în `04`
- **Motor:** `PerformanceEvaluationEngine` — lipsă
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** conceptual, nu doar tehnic
- **Nivel de fezabilitate:** 5

### KPI-008 — LRI (Leadership Readiness Index)
- **Tabele:** `Leader`/`Team`/`Assessment` — niciunul nu există
- **Motor:** 0/3 (`LeadershipDevelopmentEngine`, `TeamCoordinationEngine`, `MentorGuidanceEngine`)
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** infrastructură completă lipsă
- **Nivel de fezabilitate:** 5

### KPI-009 — MEI (Mentoring Effectiveness Index)
- **Motor:** aceleași 3 motoare lipsă ca LRI
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** identic cu LRI
- **Nivel de fezabilitate:** 5

### KPI-010 — TDI (Team Development Index)
- **Tabele:** `Team`/`Leader`/`Assessment` inexistente
- **Motor:** `PerformanceEvaluationEngine` lipsă
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** infrastructură completă lipsă
- **Nivel de fezabilitate:** 5

### KPI-011 — PES (Presentation Effectiveness Score)
- **Motor:** `PresentationEngine` lipsă — nici Conversation n-are motor propriu
- **Dependențe inter-KPI:** niciuna
- **Blocaj:** infrastructură completă lipsă
- **Nivel de fezabilitate:** 5

### KPI-012 — AMS (Autonomy Maturity Score)
- **Motor:** `AutonomyEngine` — lipsă
- **Dependențe inter-KPI:** **explicit — necesită OPI + toți ceilalți 11 KPI**
- **Blocaj:** structural, imposibil primul
- **Nivel de fezabilitate:** 6

### KPI-013 — OPI (Overall Performance Index)
- **Motor:** niciun agregator existent
- **Dependențe inter-KPI:** **explicit — necesită toți cei 12 KPI operaționali**
- **Blocaj:** structural, imposibil înaintea celorlalți 12
- **Nivel de fezabilitate:** 7 — ultimul, prin definiție matematică

---

## 3. Ordinea de fezabilitate rezultată (nu oficializată ca plan de construcție, doar ca hartă)

```
Nivel 1: DIS
Nivel 2: ORE
Nivel 3: CRH
Nivel 4: PDI, PIP (egale)
Nivel 5: OAS, ERI, LRI, MEI, TDI, PES (egale — toate necesită infrastructură comparabilă)
Nivel 6: AMS (dependent de nivelurile 1-5 + OPI)
Nivel 7: OPI (dependent de nivelurile 1-5 + AMS... de fapt de toți cei 12)
```

**Notă:** Nivelul 5 conține 6 KPI cu blocaje comparabile — ordinea internă dintre ele nu e determinată de acest audit, ar necesita o analiză separată dacă/când devine relevant.

---

## 4. Ce NU face acest document

- Nu decide formula pentru niciun KPI
- Nu adaugă niciun câmp în schemă
- Nu construiește niciun motor
- Nu oficializează ordinea de construcție — rămâne hartă de referință, decizia de a începe cu `DIS` (sau altceva) rămâne separată

---
*Document canonic de referință. Reconstituit din auditul complet al sesiunii — DIS/PriorityEngine (verificare adâncă) + ceilalți 12 KPI (verificare comparativă, pe aceleași criterii).*
