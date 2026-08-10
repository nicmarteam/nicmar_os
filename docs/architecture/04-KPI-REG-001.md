# KPI-REG-001 — KPI Registry

**Business Domain:** Core Architecture / KPI & Performance Architecture
**Nivel:** Nivelul 6 – KPI & Performance Architecture
**Versiune:** 1.1
**Status:** 🟡 Propunere pentru validare (pregătit pentru DRAFT după reconciliere PES/ORE)
**Metodologie:** Event-Driven Performance Measurement & Deterministic KPI Architecture

**SSOT Sursă:**
- KPI-ARCH-001
- Documentul 01 – Business Objects
- DB-ARCH-001
- DB-KPI-001
- ENG-ARCH-001
- RULE-ARCH-001

**Notă de proveniență:** Acest document înlocuiește și consolidează secțiunile KPI-REG-001 și KPI-MODEL-001 §3 aflate în documentul sursă `RULE-MODEL-001` (Document 07.1/08.1/08.3). Este canonic — orice altă listă a celor 11 KPI trebuie aliniată cu acest fișier.

---

## 1. Scopul documentului

KPI-REG-001 definește registrul oficial al indicatorilor de performanță utilizați în NicMar OS. Registrul stabilește pentru fiecare KPI: codul oficial, denumirea oficială, scopul, entitatea principală măsurată, categoria, Engine-ul responsabil, obiectele Business Objects relevante, relația cu Score și cu Rules, și starea în lifecycle.

Formulele matematice și algoritmii concreți sunt definiți ulterior în **KPI-MODEL-001 — KPI Definition & Calculation Model**.

---

## 2. Registrul oficial — 11 KPI

Registrul oficial al Nivelului 6 conține **11 indicatori**, confirmați în Master Architecture:

| # | Cod | Denumire oficială | Entitate principală | Owner Engine |
|---|-----|---|---|---|
| 1 | DIS | Daily Impact Score | User | PerformanceEvaluationEngine |
| 2 | CRH | Customer Relationship Health | Client | CustomerRelationshipEngine |
| 3 | PDI | Partner Development Index | Partner | PerformanceEvaluationEngine |
| 4 | PIP | Partner Integration Progress | Partner | PerformanceEvaluationEngine |
| 5 | OAS | Onboarding Activation Success | Partner | PerformanceEvaluationEngine |
| 6 | ERI | Experience Reuse Index | — (v. KPI-MODEL-001) | PerformanceEvaluationEngine |
| 7 | LRI | Leadership Readiness Index | Partner | PerformanceEvaluationEngine |
| 8 | MEI | Mentoring Effectiveness Index | Leader / Partner | PerformanceEvaluationEngine |
| 9 | TDI | Team Development Index | Team | PerformanceEvaluationEngine |
| 10 | AMS | Autonomy Maturity Score | Partner | PerformanceEvaluationEngine |
| 11 | **OPI** | Overall Performance Index (indicator strategic compozit) | User / Partner / Team / Leader | PerformanceEvaluationEngine |

**Notă despre OPI:** OPI nu este un KPI operațional independent, ci indicatorul strategic compozit care sintetizează ceilalți 10 KPI ai Motorului 1.

---

## 3. Detaliu per KPI

### KPI-001 — DIS (Daily Impact Score)
- **Categorie:** Operational Performance / Daily Execution
- **Scop:** Măsoară impactul operațional realizat într-o perioadă zilnică de activitate.
- **Business Objects relevante:** Mission, Task, DailyPlan, DailyReview, Habit, FollowUp, Meeting, Conversation, Partner, Client
- **Engine-uri asociate:** MissionEngine, PriorityEngine, ContinuityEngine
- **Evenimente relevante:** MissionGenerated, MissionCompleted, MissionValidated
- **Dashboard:** scor zilnic, evoluție, trend, comparație planificat/realizat
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-002 — CRH (Customer Relationship Health)
- **Categorie:** Relationship Performance
- **Scop:** Măsoară sănătatea relației cu clientul și calitatea relației comerciale.
- **Business Objects relevante:** Client, Contact, Conversation, FollowUp, Meeting, Experience, Objection, Assessment
- **Engine-uri asociate:** RelationshipEngine, FollowUpEngine, ContinuityEngine, PerformanceEvaluationEngine
- **Dashboard:** scor relațional, trend, status relație, segmente de sănătate relațională
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-003 — PDI (Partner Development Index)
- **Categorie:** Partner Development
- **Scop:** Măsoară evoluția și dezvoltarea partenerului de-a lungul parcursului operațional.
- **Business Objects relevante:** Partner, Mission, Habit, Assessment, Experience, Team, Leader, Conversation, Contact
- **Engine-uri asociate:** PartnerRelationshipEngine, ContinuityEngine, MissionEngine, LeadershipDevelopmentEngine, MentorGuidanceEngine
- **Evenimente relevante:** PartnerActivated, OnboardingCompleted, FirstResultAchieved, AutonomyReached, LeadershipActivated, PartnerReactivated, InactivityDetected
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-004 — PIP (Partner Integration Progress)
- **Categorie:** Partner Integration
- **Scop:** Măsoară progresul partenerului prin etapa de integrare și onboarding.
- **Business Objects relevante:** Partner, Mission, Habit, Assessment, Contact, Conversation
- **Engine-uri asociate:** PartnerRelationshipEngine, MissionEngine, HabitEngine, ContinuityEngine
- **Evenimente relevante:** PartnerActivated, OnboardingStarted, OnboardingCompleted, OnboardingTimeout
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-005 — OAS (Onboarding Activation Success)
- **Categorie:** Performance / Operational Assessment
- **Scop:** Indicator oficial al arhitecturii NicMar OS legat de activarea reușită în onboarding.
- **Owner Engine:** PerformanceEvaluationEngine
- **Formula:** va fi definită în KPI-MODEL-001 (definiția semantică extinsă e încă în lucru)
- **Status:** PROPOSED

### KPI-006 — ERI (Experience Reuse Index)
- **Categorie:** Performance / Relationship / Operational Evaluation
- **Scop:** Indicator oficial al arhitecturii NicMar OS legat de reutilizarea experienței acumulate.
- **Owner Engine:** PerformanceEvaluationEngine
- **Formula:** va fi definită în KPI-MODEL-001 (definiția semantică extinsă e încă în lucru)
- **Status:** PROPOSED

### KPI-007 — LRI (Leadership Readiness Index)
- **Categorie:** Leadership Development
- **Scop:** Măsoară nivelul de pregătire al partenerului pentru asumarea rolului de leadership.
- **Business Objects relevante:** Partner, Leader, Team, Assessment, Mission, Habit, Experience
- **Engine-uri asociate:** LeadershipDevelopmentEngine, TeamCoordinationEngine, MentorGuidanceEngine
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-008 — AMS (Autonomy Maturity Score)
- **Categorie:** Partner Maturity / Autonomy
- **Scop:** Măsoară nivelul de maturitate și autonomie operațională al partenerului.
- **Business Objects relevante:** Partner, Mission, Habit, Assessment, Leader, Team
- **Engine-uri asociate:** PartnerRelationshipEngine, MentorGuidanceEngine, ContinuityEngine, LeadershipDevelopmentEngine
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-009 — MEI (Mentoring Effectiveness Index)
- **Categorie:** Mentoring / Leadership Development
- **Scop:** Măsoară eficiența activității de mentorat în dezvoltarea partenerilor și liderilor.
- **Business Objects relevante:** Partner, Leader, Team, Mission, Assessment, Experience
- **Engine-uri asociate:** MentorGuidanceEngine, LeadershipDevelopmentEngine, TeamCoordinationEngine
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-010 — TDI (Team Development Index)
- **Categorie:** Team Development
- **Scop:** Măsoară dezvoltarea și evoluția unei echipe.
- **Business Objects relevante:** Team, Partner, Leader, Mission, Assessment, KPI, Score
- **Owner Engine:** PerformanceEvaluationEngine
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-011 — OPI (Overall Performance Index)
- **Categorie:** Overall Performance (indicator strategic compozit)
- **Scop:** Măsoară performanța generală prin agregarea celorlalți 10 KPI ai sistemului.
- **Entități:** User (principal); Partner, Team, Leader (secundare)
- **Input-uri:** KPI operaționali, relaționali, de dezvoltare, de leadership, de autonomie
- **Dashboard:** scor general, trend, componente, evoluție temporală
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

---

## 4. Decizie oficială — Reconcilierea PES / ORE

**Data deciziei:** 10 august 2026
**Decident:** Nic (owner proiect)

În modelul Business Object existent apăreau și doi indicatori suplimentari, absenți din registrul oficial de mai sus:
- **PES** — Presentation Effectiveness Score
- **ORE** — Objection Resolution Effectiveness

**Investigație:** nu s-a găsit nicio sursă/conversație care să confirme originea sau intenția din spatele acestor doi indicatori. Nu există nicio suprapunere matematică demonstrată cu KPI-urile oficiale (doar legături conceptuale slabe cu CRH și PDI).

**Decizie:** PES și ORE sunt **ARHIVATE**, nu fac parte din registrul activ de 11 KPI.
- Statutul lor rămâne păstrat istoric în modelul Business Object, marcat explicit ca arhivat.
- Motiv: fără origine confirmată, fără suprapunere demonstrată, efectul lor e absorbit conceptual de CRH și PDI.
- Dacă în pilotul cu liderii apare o nevoie reală, documentată, de a măsura separat eficiența prezentărilor sau a rezolvării obiecțiilor, se reintroduc pe bază de evidență, nu de presupunere.

**Efect asupra lifecycle-ului:** blocajul de reconciliere pentru KPI-MODEL-001 este rezolvat. KPI-MODEL-001 poate trece din PROPOSED în DRAFT.

---

## 5. Corecție editorială

În draftul anterior al listei (Document 08.3 §3), codul **ERI apărea duplicat** (pozițiile 6 și 11 din 11), eroare de formatare fără impact asupra conținutului — toate cele 10 coduri operaționale + OPI erau deja prezente o singură dată fiecare. Corectat în tabelul din secțiunea 2 de mai sus.

---

## 6. Condiția de validare a registrului

KPI-REG-001 poate fi validat oficial (🔒 ÎNGHEȚAT) după confirmarea:
1. listei finale de KPI — ✅ confirmată (11, PES/ORE arhivate)
2. denumirii oficiale — ✅ confirmată pentru toate cele 11
3. entității principale — parțial (OAS, ERI: TBD în KPI-MODEL-001)
4. categoriei — ✅
5. Owner Engine — ✅
6. relației KPI → Score — ✅
7. relației KPI → Rules — ✅
8. relației KPI → Event Store — de confirmat în KPI-MODEL-001

---

## 7. Lifecycle

```
PROPOSED
   ↓
DRAFT          ← toți cei 11 KPI sunt aici acum, blocajul PES/ORE fiind rezolvat
   ↓
VALIDATED
   ↓
ACTIVE
   ↓
DEPRECATED
   ↓
ARCHIVED
```

Trecerea în ACTIVE se realizează după finalizarea KPI-MODEL-001 + KPI-TEST-001.

---

## 8. Coerență cu Living Vision

Această decizie (arhivarea PES/ORE, §4) respectă **Regula Coerenței** din `docs/living-vision/01_Caracter_NicMar_OS.md`: *"Dacă nu îl ajută pe om, nu îl construim."* Doi indicatori fără origine confirmată și fără suprapunere demonstrată ar fi adăugat complexitate fără beneficiu clar pentru liderul care folosește dashboard-ul — exact ce pilonul **"Apărăm simplitatea"** cere să evităm.

Orice extindere viitoare a acestui registru (KPI noi, redenumiri, restructurări) ar trebui verificată față de:
- `docs/living-vision/00_Manifest_NicMar.md` — de ce există NicMar OS
- `docs/living-vision/01_Caracter_NicMar_OS.md` — cei 5 piloni, cele 4 linii roșii, testul suprem al fiecărei decizii

---
*Document canonic. Înlocuiește secțiunile KPI-REG-001/KPI-MODEL-001 §3 din draftul original RULE-MODEL-001.*
