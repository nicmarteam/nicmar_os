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

## 2. Registrul oficial — 13 KPI (revizuit, versiune finală)

**Sursă primară nouă, cea mai completă găsită**: `docs/architecture/05-competente-37-motor1.md` (fost `01_Raspuns_Mesaj.txt`), documentul care construiește secvențial toate cele 37 de competențe ale Motorului 1. Competența 36 (`Evaluarea_Performanței`) și Competența 37 (`Autonomia_Completă_a_Utilizatorului`) confirmă structura finală: **12 KPI operaționali + 1 indicator strategic compozit (OPI) care le sintetizează pe toate**.

| # | Cod | Denumire oficială | Tip |
|---|-----|---|---|
| 1 | DIS | Daily Impact Score | operațional |
| 2 | CRH | Customer Relationship Health | operațional |
| 3 | PDI | Partner Development Index | operațional |
| 4 | PIP | Partner Integration Progress | operațional |
| 5 | OAS | Onboarding Activation Success | operațional |
| 6 | ERI | Experience Reuse Index | operațional |
| 7 | LRI | Leadership Readiness Index | operațional |
| 8 | MEI | Mentoring Effectiveness Index | operațional |
| 9 | TDI | Team Development Index | operațional |
| 10 | AMS | Autonomy Maturity Score | operațional (introdus la Competența 37, `AutonomyEngine`) |
| 11 | **PES** | Presentation Effectiveness Score | operațional (introdus la Competența 28/36, `PresentationEngine`) |
| 12 | **ORE** | Objection Resolution Effectiveness | operațional (introdus la Competența 29/36, `ObjectionEngine`) |
| 13 | **OPI** | Overall Performance Index | **strategic, compozit** — sintetizează toți cei 12 de mai sus |

**Owner Engine central pentru cei 12 operaționali:** `PerformanceEvaluationEngine` (Competența 36).
**Owner Engine pentru OPI + orchestrarea finală:** `AutonomyEngine` (Competența 37) — folosește OPI + toți cei 12 KPI ca input pentru certificarea nivelului de autonomie.

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

### KPI-008 — MEI (Mentoring Effectiveness Index)
- **Categorie:** Mentoring / Leadership Development
- **Scop:** Măsoară eficiența activității de mentorat în dezvoltarea partenerilor și liderilor.
- **Business Objects relevante:** Partner, Leader, Team, Mission, Assessment, Experience
- **Engine-uri asociate:** MentorGuidanceEngine, LeadershipDevelopmentEngine, TeamCoordinationEngine
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-009 — TDI (Team Development Index)
- **Categorie:** Team Development
- **Scop:** Măsoară dezvoltarea și evoluția unei echipe.
- **Business Objects relevante:** Team, Partner, Leader, Mission, Assessment, KPI, Score
- **Owner Engine:** PerformanceEvaluationEngine
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-010 — AMS (Autonomy Maturity Score)
- **Categorie:** Autonomy / Strategic Maturity
- **Scop:** Măsoară gradul de autonomie operațională al utilizatorului/partenerului, rezultat din integrarea tuturor KPI-urilor Motorului 1 și din capacitatea de a produce rezultate constante, de a dezvolta relații, parteneri și lideri folosind NicMar OS ca sistem de ghidare.
- **Business Objects relevante:** Partner, Mission, Habit, Assessment, Leader, Team
- **Sursă:** Competența 37 (`Autonomia_Completă_a_Utilizatorului`, ultima din Motorul 1), motor `AutonomyEngine`
- **Engine-uri asociate:** PartnerRelationshipEngine, MentorGuidanceEngine, LeadershipDevelopmentEngine, AutonomyEngine
- **Input-uri:** OPI + toți ceilalți 11 KPI + HabitEngine, MissionEngine, PriorityEngine, FollowUpEngine
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-011 — PES (Presentation Effectiveness Score)
- **Categorie:** Presentation / Conversation Performance
- **Scop:** Măsoară eficiența unei prezentări prin combinarea: nivelului de interes generat, gradului de implicare în conversație, continuării relației (follow-up sau întâlnire), autenticității percepute, progresului persoanei după prezentare.
- **Sursă:** Competența 28 (`Prezentarea_Simplă_a_Soluțiilor`), motor propriu `PresentationEngine`
- **Engine-uri conectate:** PresentationEngine, Motorul Relației, Motorul Continuității, Motorul Identității, CustomerRelationshipEngine, PartnerRelationshipEngine
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-012 — ORE (Objection Resolution Effectiveness)
- **Categorie:** Relationship / Objection Handling Performance
- **Scop:** Măsoară eficiența cu care sunt gestionate și rezolvate obiecțiile ridicate de Contact/Client în conversații.
- **Sursă:** Competența 29 (`Gestionarea_Obiecțiilor_Avansate`) + confirmat în Event Catalog: evenimentul `ObjectionRaised` → `WF-OBJECTION-CREATE-001`
- **Engine-uri asociate:** RelationshipEngine, ObjectionEngine
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

### KPI-013 — OPI (Overall Performance Index)
- **Categorie:** Overall Performance (indicator strategic compozit)
- **Scop:** Măsoară performanța generală prin agregarea celorlalți 12 KPI operaționali ai sistemului.
- **Entități:** User (principal); Partner, Team, Leader (secundare)
- **Input-uri:** toți cei 12 KPI operaționali
- **Dashboard:** scor general, trend, componente, evoluție temporală
- **Formula:** va fi definită în KPI-MODEL-001
- **Status:** PROPOSED

---

## 4. Istoricul reconcilierii PES / ORE / AMS (decizie finală)

**Decident:** Nic (owner proiect) | **Ultima revizuire:** 12 august 2026

### Etapa 1 — decizie inițială (bazată pe istoricul de conversație)
Nu s-a găsit nicio sursă care să confirme originea PES/ORE. **Decizie:** ambii arhivați.

### Etapa 2 — revizuire (bazată pe Event Catalog, `02-business-objects-5-pillars.md`)
Verificare directă în sursă a arătat că **ORE are origine confirmată**: evenimentul `ObjectionRaised` → `WF-OBJECTION-CREATE-001` → `KPI influențați: ORE`. **PES rămâne fără sursă găsită** la acest pas. **Decizie revizuită:** ORE reactivat, PES rămâne arhivat.

### Etapa 3 — revizuire finală (bazată pe documentul celor 37 de competențe, `05-competente-37-motor1.md`)
Documentul complet al Motorului 1 (37 de competențe, construite secvențial) conține definiția PES la Competența 28 (`Prezentarea_Simplă_a_Soluțiilor`), cu motor propriu `PresentationEngine`, și confirmă unificarea lui în `PerformanceEvaluationEngine` la Competența 36. **PES are, de fapt, origine solidă** — pur și simplu nu era încă documentată în fișierele consultate până la acel punct.

În plus, același document introduce **AMS** ca al 12-lea KPI operațional, prin `AutonomyEngine` (Competența 37), și confirmă **OPI** ca indicator strategic compozit de nivel superior, separat de cei 12.

### Decizia finală
Toți cei 3 indicatori sunt **activi**: PES, ORE și AMS fac parte din registrul oficial de 12 KPI operaționali + OPI compozit = **13 total**. Niciunul nu rămâne arhivat.

### Lecție de proces (actualizată)
O decizie de arhivare/reconciliere KPI nu poate fi considerată definitivă doar pe baza documentelor disponibile la momentul respectiv. De fiecare dată când apare un document primar nou (chiar dacă vine dintr-o sursă externă, ca acest fișier salvat separat pe Drive), registrul trebuie re-verificat. Motivul recurent al erorilor anterioare: informația exista deja, doar nu fusese încă adusă în context.

**Efect asupra lifecycle-ului:** KPI-MODEL-001 poate trece din PROPOSED în DRAFT cu registrul complet de 13.

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
