# NicMar OS — Harta Motoarelor Tehnice Reale (Motorul 1, 37 Competențe)

**Status:** Audit factual, extras direct din sursa primară
**Sursă:** `docs/architecture/05-competente-37-motor1.md`
**Scop:** Inventar complet al motoarelor tehnice declarate explicit în document, ca bază pentru decizia de scope MVP-ENGINE-001.

---

## 1. Notă metodologică — corectarea unei confuzii

Documentul de 37 de competențe folosește frecvent **etichete narative în română** ca titluri de capitol repetate — de ex. `"Capitolul C — Motorul Continuității"`, `"Motorul Relației"`, `"Motorul Identității"`. Verificare directă a arătat că **acestea NU sunt motoare tehnice separate**, ci roluri conceptuale reutilizate pentru teme diferite. În spatele fiecărei apariții a `"Motorul Continuității"`, de exemplu, stă de fiecare dată alt motor tehnic real: `DailyRhythmEngine`, `ResilienceEngine`, `HabitEngine`, `FollowUpEngine` — în funcție de competența discutată.

**Regulă de citire**: singura sursă de adevăr pentru "ce motor există cu adevărat" este linia explicită `Obiect nou / Motor tehnic: <Nume>`. Etichetele narative de capitol se ignoră ca entități de arhitectură.

---

## 2. Inventarul complet — 18 motoare tehnice confirmate

### `MissionEngine`
- **Statut special**: cel mai citat motor din tot documentul (34 apariții), dar fără o declarație formală "Obiect nou" — tratat ca fundamental/preexistent din Competențele 1–13, înainte ca documentul să înceapă să declare explicit fiecare motor nou.
- Deja inclus în MVP-ENGINE-001 inițial.

### `DailyRhythmEngine`
- **Responsabilități:** calculează încărcarea optimă a zilei, stabilește ordinea activităților, evită supraîncărcarea, menține consistența.
- **Intrări:** disponibilitate timp, profil identitate, misiunea anterioară, relații active, follow-up-uri, obiective.
- **Ieșiri:** Misiunea Zilei, estimare timp, progres, configurarea zilei următoare.
- **Status oficial în sursă:** ✅ VALIDATĂ (10/10)

### `ResilienceEngine`
- **Responsabilități:** detectează blocajele, le clasifică și le contorizează frecvența, alege automat cea mai bună micro-acțiune, adaptează ritmul utilizatorului, construiește profilul de reziliență.
- **Status oficial în sursă:** ✅ VALIDATĂ (10/10)

### `HabitEngine`
- **Responsabilități:** construiește obiceiuri, urmărește consecvența, detectează întreruperile, adaptează dificultatea, sincronizează rutina cu Misiunea Zilei.
- **Intrări:** profil utilizator, MissionEngine, SuccessEngine, UnblockingEngine, Dashboard.
- **Ieșiri:** scor consecvență (Consistency Index), procent disciplină, serie activă.
- **Status oficial în sursă:** ✅ VALIDATĂ (10/10)

### `FollowUpEngine`
- **Responsabilități:** organizează relațiile active, stabilește prioritățile zilnice, recomandă strategia optimă, generează următorul follow-up.
- **Intrări:** Motorul Relației, HabitEngine, MissionEngine, Dashboard, Calendar, istoricul conversațiilor.
- **Metric nou transversal:** **Relationship Priority Score (RPS)** — indice compozit din timpul scurs de la ultima interacțiune, Scorul Relației, Scorul Interesului, istoricul răspunsurilor, etapa relației, probabilitatea de progres.
- Deja inclus în MVP-ENGINE-001 inițial.

### `PriorityEngine`
- **Responsabilități:** stabilește prioritățile zilnice, optimizează folosirea timpului, reduce încărcarea cognitivă, coordonează Dashboard-ul, recalculează permanent ordinea activităților, activează Focus Mode.
- **Notă:** declarat de 2 ori în document — apare devreme (organizare zilnică) și din nou mai târziu (coordonare Dashboard + energie).

### `CustomerRelationshipEngine`
- **Responsabilități:** administrează istoricul relației cu clienții, detectează momente importante, recomandă următorul pas, calculează satisfacția.
- **Metric nou transversal:** **Customer Relationship Health (CRH)** — indice strategic al stării relației (interacțiuni, satisfacție, regularitate, deschidere).
- Deja inclus în MVP-ENGINE-001 inițial.

### `PartnerRelationshipEngine`
- **Responsabilități:** gestionează dezvoltarea relației mentor-partener pe toată durata colaborării. Nu urmărește doar conversațiile — urmărește evoluția utilizatorului.
- **Intrări:** progresul în cele 37 competențe, MissionEngine, HabitEngine.
- Deja inclus în MVP-ENGINE-001 inițial.

### `PresentationEngine`
- **Responsabilități:** construiește prezentări personalizate, scurte, naturale — generează o conversație, nu un discurs standard.
- **Legătură KPI:** alimentează **PES** (Presentation Effectiveness Score) — v. `04-KPI-REG-001.md`.
- ❌ Nu e în cele 6 motoare MVP confirmate (v. Decizia 2, Decizia 3).

### `ObjectionEngine`
- **Responsabilități:** analizează preocupările exprimate de persoane/clienți/parteneri, construiește răspunsuri autentice. Obiectivul e construirea încrederii, nu câștigarea unei dezbateri.
- **Intrări:** tipul preocupării, istoricul relației, Motorul Identității, CustomerRelationshipEngine, PartnerRelationshipEngine.
- **Legătură KPI:** alimentează **ORE** (Objection Resolution Effectiveness) — confirmat și în Event Catalog (`02-business-objects-5-pillars.md`).
- ✅ Inclus — v. Decizia 2 (ObjectionEngine adăugat ca al 6-lea motor, ORE activ în registru).

### `PartnerOnboardingEngine`
- **Responsabilități:** coordonează transformarea unei persoane interesate într-un partener activ — activare, verificarea pașilor, inițializarea traseului de dezvoltare, sincronizarea motoarelor implicate.
- ❌ Nu e în cele 6 motoare MVP confirmate (v. Decizia 2, Decizia 3).

### `PartnerIntegrationEngine`
- **Responsabilități:** coordonează integrarea completă a partenerului nou — personalizarea onboarding-ului, sincronizarea motoarelor operaționale, monitorizarea progresului, detectarea timpurie a blocajelor, accelerarea autonomiei.
- ❌ Nu e în cele 6 motoare MVP confirmate (v. Decizia 2, Decizia 3).

### `MentorGuidanceEngine`
- **Responsabilități:** coordonează procesul de mentorat — nu spune mentorului ce să facă pas cu pas, ci îl ajută să ia decizii bune folosind istoricul partenerului, profilul identitar, competențele parcurse, ritmul de dezvoltare.
- ❌ Nu e în cele 6 motoare MVP confirmate (v. Decizia 2, Decizia 3).

### `TeamCoordinationEngine`
- **Responsabilități:** coordonează dezvoltarea echipei prin prioritizarea intervențiilor liderului, optimizează raportul timp investit / impact.
- **Intrări:** MentorGuidanceEngine.
- ❌ Nu e în cele 6 motoare MVP confirmate (v. Decizia 2, Decizia 3).

### `LeadershipDevelopmentEngine`
- **Responsabilități:** coordonează identificarea, dezvoltarea și maturizarea viitorilor lideri din echipă.
- **Intrări:** TeamCoordinationEngine.
- ❌ Nu e în cele 6 motoare MVP confirmate (v. Decizia 2, Decizia 3).

### `ExperienceLibraryEngine`
- **Responsabilități:** colectează experiențele validate, le clasifică, elimină duplicate, recomandă experiențe similare, identifică cele mai eficiente practici, alimentează Motorul de Învățare.
- **Context:** introdus la Competența 35, marcată explicit ca "începutul inteligenței colective din NicMar OS."
- ❌ Nu e în cele 6 motoare MVP confirmate (v. Decizia 2, Decizia 3).

### `PerformanceEvaluationEngine`
- **Rol:** orchestrator central al stratului de performanță — unifică cei 12 KPI operaționali (v. `04-KPI-REG-001.md`).
- **Introdus la:** Competența 36.
- ❌ Nu e în cele 6 motoare MVP confirmate (v. Decizia 2, Decizia 3).

### `AutonomyEngine`
- **Rol:** orchestratorul final — agregă toți cei 13 KPI (inclusiv OPI, AMS), certifică nivelul de autonomie al utilizatorului.
- **Introdus la:** Competența 37 (ultima competență a Motorului 1).
- ❌ Nu e în cele 6 motoare MVP confirmate (v. Decizia 2, Decizia 3).

---

## 3. Tabel-sumar: cele 6 motoare MVP vs. restul din Core

| Motor tehnic | În cele 6 MVP? | KPI/rol legat |
|---|---|---|
| MissionEngine | ✅ | DIS |
| FollowUpEngine | ✅ | DIS, RPS |
| CustomerRelationshipEngine | ✅ | CRH |
| PartnerRelationshipEngine | ✅ | PDI, PIP |
| RuleEngine *(fost `RuleEvaluationEngine`)* | ✅ — Decizia 1 | evaluare centralizată reguli (`RULE-MODEL-001`) |
| ObjectionEngine | ✅ — Decizia 2 | **ORE** |
| DailyRhythmEngine | ❌ | Misiunea Zilei |
| ResilienceEngine | ❌ | — |
| HabitEngine | ❌ | Consistency Index |
| PriorityEngine | ❌ | — |
| PresentationEngine | ❌ | **PES** |
| PartnerOnboardingEngine | ❌ | OAS |
| PartnerIntegrationEngine | ❌ | PIP |
| MentorGuidanceEngine | ❌ | MEI |
| TeamCoordinationEngine | ❌ | TDI |
| LeadershipDevelopmentEngine | ❌ | LRI |
| ExperienceLibraryEngine | ❌ | ERI |
| PerformanceEvaluationEngine | ❌ | toți cei 12 |
| AutonomyEngine | ❌ | OPI, AMS |

**Constatare finală:** din cele 18 motoare confirmate în Core, **6 sunt incluse în MVP** (v. Decizia 1 — `RuleEngine`, Decizia 2 — `ObjectionEngine`): `MissionEngine`, `FollowUpEngine`, `CustomerRelationshipEngine`, `PartnerRelationshipEngine`, `RuleEngine`, `ObjectionEngine`. Restul de 12 rămân post-MVP (v. `07-motoare-post-mvp.md`).

---

## 4. Decizii confirmate

### Decizia 1 — `RuleEvaluationEngine` → `RuleEngine` (confirmat 12 august 2026)

**Constatare:** numele `RuleEvaluationEngine` nu apare în nicio sursă primară. `RULE-MODEL-001` (Document 07.1) folosește generic termenul "Rule Engine", cu rol distinct de `PerformanceEvaluationEngine` — fluxul documentat e `KPI → Threshold → Rule Engine → Decision Outcome`, deci Rule Engine vine *după* evaluarea KPI, ca pas separat.

**Decizie:** motor separat, păstrat în MVP, redenumit oficial la **`RuleEngine`** (aliniat cu terminologia din Core, nu cu numele inventat în conversație). Nu se distribuie logica de evaluare a regulilor în fiecare motor individual — rămâne centralizată, conform arhitecturii deterministe din `RULE-MODEL-001`.

**Motiv:** centralizarea respectă principiul "Apărăm simplitatea" din `01_Caracter_NicMar_OS.md` — logica de reguli distribuită în 18 motoare ar contrazice scopul unui document de 4918 rânduri dedicat exact evitării acestei fragmentări.

**Cod actualizat:** `ENG-RULE-001` rămâne codul MVP, dar numele tehnic afișat în documentație devine `RuleEngine`, nu `RuleEvaluationEngine`.

### Decizia 2 — `ObjectionEngine` intră în MVP ca al 6-lea motor (confirmat 12 august 2026)

**Motiv:** ORE e deja KPI activ în `04-KPI-REG-001.md`, cu origine dublu-confirmată (Event Catalog + Competența 29). Fără `ObjectionEngine`, ORE rămâne un KPI pe care nimeni nu-l poate calcula — o gaură vizibilă în dashboard din prima zi de pilot.

**Dependințe verificate:** `ObjectionEngine` depinde explicit de `CustomerRelationshipEngine` și `PartnerRelationshipEngine` — ambele deja în MVP. Nu aduce dependințe noi nerezolvate.

**Limită explicită:** decizia se aplică *doar* lui `ObjectionEngine`. Nu redeschide scope-ul pentru celelalte 11 motoare excluse — planul de execuție inițial ("nu mai dezvoltăm încă celelalte 10 motoare") rămâne valabil pentru restul.

**Efect asupra MVP-ENGINE-001:** lista devine 6 motoare: `MissionEngine`, `FollowUpEngine`, `CustomerRelationshipEngine`, `PartnerRelationshipEngine`, `RuleEngine`, `ObjectionEngine`.

---

### Decizia 3 — `PresentationEngine` rămâne exclus din MVP; Conversation Agent scope redus (confirmat 12 august 2026)

**Context:** verificare a arătat suprapunere conceptuală clară între rolul `PresentationEngine` ("construiește prezentări personalizate... generează o conversație, nu un discurs standard") și rolul descris pentru `Conversation Agent` din MVP-AGENT-001 ("Ce îi spun? — produce mesajul concret").

**Decizie:** spre deosebire de `ObjectionEngine` (inclus, Decizia 2), `PresentationEngine` **rămâne exclus** din MVP, menținând strict scope-ul stabilit inițial.

**Efect direct asupra `Conversation Agent`:** în MVP v1, agentul funcționează cu scope redus — acoperă gestionarea interacțiunilor și a obiecțiilor (prin `ObjectionEngine`, deja activ), **fără** generare sintetică de prezentări personalizate. Capabilitatea se adaugă într-o fază ulterioară, când `PresentationEngine` intră în scope.

**Motiv:** menținerea simplității și rigorii vertical slice-ului MVP — nu orice suprapunere conceptuală justifică extinderea scope-ului. Criteriul rămâne cel aplicat la ORE (KPI activ fără motor = gaură vizibilă), nu orice paralelă tematică.

### Decizia 4 — MVP acoperă strict recrutare organică; reclama plătită rămâne post-MVP (confirmat 12 august 2026)

**Context:** documentul de 37 de competențe descrie deja un flux complet de recrutare **organică** (postare pe Facebook/WhatsApp/Instagram/TikTok/LinkedIn → reacție/comentariu → conversație ghidată → obiecție → partener nou), fără niciun concept de reclamă plătită (Ads) în arhitectura documentată.

**Decizie:** NicMar OS MVP acoperă exclusiv fluxul organic deja construit. Reclama plătită (Meta/Facebook Ads etc.) **nu intră în scope-ul MVP** — nu se construiește niciun agent sau motor dedicat pentru asta în această fază.

**Motiv:** "Construim ceva funcțional, apoi ne extindem" — aceeași logică de secvențiere aplicată consecvent la Deciziile 1-3. Recrutarea organică e deja documentată, aliniată cu Avatar și Limbajul Avatarului; reclama plătită ar necesita conținut și validare complet noi (hook-uri de ad, targetare, buget), nevalidate încă.

**Status reclamă plătită:** rămâne o extindere viitoare posibilă, de reconsiderat după ce MVP-ul organic e funcțional și testat cu liderii pilot.

---

## 6. Ultima întrebare deschisă

Restul de 11 motoare excluse din MVP — toate amânate pentru fazele următoare, sau există vreunul cu prioritate ascunsă?

**Un candidat de verificat, nu de decis automat: `PriorityEngine`.** E citat explicit ca "motor conectat" de 3 din cele 6 motoare deja incluse în MVP (`HabitEngine`, `FollowUpEngine`, `CustomerRelationshipEngine`), deși niciunul din ele nu-l are ca dependință *obligatorie* declarată — apare mai degrabă ca motor de coordonare/optimizare transversal (Dashboard, alocare timp), nu ca blocaj funcțional direct.

**Actualizare P11 (12 august 2026):** pentru Partner Agent, dependința e obligatorie (selecția partenerului prioritar, Competența 27, Ecranul 1), dar acoperită printr-o **Priority capability** la nivel de Agent, cu date MVP existente (`PDI`, timp de la ultima interacțiune), fără `PriorityEngine` complet — v. `08-MVP-AGENT-001.md`, Agent 5. Verdictul rămâne neschimbat: `PriorityEngine` ❌, în afara celor 6 motoare MVP.

---
*Document canonic pentru inventarul de motoare tehnice. Se coroborează cu `04-KPI-REG-001.md` (KPI) și `02-business-objects-5-pillars.md` (Event Catalog).*
