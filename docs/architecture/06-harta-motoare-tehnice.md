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
- ❌ Nu e în cele 5 motoare MVP inițiale.

### `ObjectionEngine`
- **Responsabilități:** analizează preocupările exprimate de persoane/clienți/parteneri, construiește răspunsuri autentice. Obiectivul e construirea încrederii, nu câștigarea unei dezbateri.
- **Intrări:** tipul preocupării, istoricul relației, Motorul Identității, CustomerRelationshipEngine, PartnerRelationshipEngine.
- **Legătură KPI:** alimentează **ORE** (Objection Resolution Effectiveness) — confirmat și în Event Catalog (`02-business-objects-5-pillars.md`).
- ❌ Nu e în cele 5 motoare MVP inițiale — deși KPI-ul lui (ORE) e activ în registru.

### `PartnerOnboardingEngine`
- **Responsabilități:** coordonează transformarea unei persoane interesate într-un partener activ — activare, verificarea pașilor, inițializarea traseului de dezvoltare, sincronizarea motoarelor implicate.
- ❌ Nu e în cele 5 motoare MVP inițiale.

### `PartnerIntegrationEngine`
- **Responsabilități:** coordonează integrarea completă a partenerului nou — personalizarea onboarding-ului, sincronizarea motoarelor operaționale, monitorizarea progresului, detectarea timpurie a blocajelor, accelerarea autonomiei.
- ❌ Nu e în cele 5 motoare MVP inițiale.

### `MentorGuidanceEngine`
- **Responsabilități:** coordonează procesul de mentorat — nu spune mentorului ce să facă pas cu pas, ci îl ajută să ia decizii bune folosind istoricul partenerului, profilul identitar, competențele parcurse, ritmul de dezvoltare.
- ❌ Nu e în cele 5 motoare MVP inițiale.

### `TeamCoordinationEngine`
- **Responsabilități:** coordonează dezvoltarea echipei prin prioritizarea intervențiilor liderului, optimizează raportul timp investit / impact.
- **Intrări:** MentorGuidanceEngine.
- ❌ Nu e în cele 5 motoare MVP inițiale.

### `LeadershipDevelopmentEngine`
- **Responsabilități:** coordonează identificarea, dezvoltarea și maturizarea viitorilor lideri din echipă.
- **Intrări:** TeamCoordinationEngine.
- ❌ Nu e în cele 5 motoare MVP inițiale.

### `ExperienceLibraryEngine`
- **Responsabilități:** colectează experiențele validate, le clasifică, elimină duplicate, recomandă experiențe similare, identifică cele mai eficiente practici, alimentează Motorul de Învățare.
- **Context:** introdus la Competența 35, marcată explicit ca "începutul inteligenței colective din NicMar OS."
- ❌ Nu e în cele 5 motoare MVP inițiale.

### `PerformanceEvaluationEngine`
- **Rol:** orchestrator central al stratului de performanță — unifică cei 12 KPI operaționali (v. `04-KPI-REG-001.md`).
- **Introdus la:** Competența 36.
- ❌ Nu e în cele 5 motoare MVP inițiale.

### `AutonomyEngine`
- **Rol:** orchestratorul final — agregă toți cei 13 KPI (inclusiv OPI, AMS), certifică nivelul de autonomie al utilizatorului.
- **Introdus la:** Competența 37 (ultima competență a Motorului 1).
- ❌ Nu e în cele 5 motoare MVP inițiale.

---

## 3. Tabel-sumar: MVP inițial vs. realitatea din Core

| Motor tehnic | În cele 5 MVP inițiale? | KPI/rol legat |
|---|---|---|
| MissionEngine | ✅ | DIS |
| FollowUpEngine | ✅ | DIS, RPS |
| CustomerRelationshipEngine | ✅ | CRH |
| PartnerRelationshipEngine | ✅ | PDI, PIP |
| RuleEvaluationEngine | ⚠️ *(fără corespondent găsit în nicio sursă primară)* | — |
| DailyRhythmEngine | ❌ | Misiunea Zilei |
| ResilienceEngine | ❌ | — |
| HabitEngine | ❌ | Consistency Index |
| PriorityEngine | ❌ | — |
| PresentationEngine | ❌ | **PES** |
| ObjectionEngine | ❌ | **ORE** |
| PartnerOnboardingEngine | ❌ | OAS |
| PartnerIntegrationEngine | ❌ | PIP |
| MentorGuidanceEngine | ❌ | MEI |
| TeamCoordinationEngine | ❌ | TDI |
| LeadershipDevelopmentEngine | ❌ | LRI |
| ExperienceLibraryEngine | ❌ | ERI |
| PerformanceEvaluationEngine | ❌ | toți cei 12 |
| AutonomyEngine | ❌ | OPI, AMS |

**Constatare factuală:** doar 4 din cele 18 motoare confirmate în Core sunt incluse în cele 5 motoare MVP inițiale. Al 5-lea motor din lista MVP (`RuleEvaluationEngine`) nu are corespondent confirmat în nicio sursă primară verificată până acum.

---

## 4. Întrebări deschise pentru decizie (nu decise aici)

Acest document prezintă doar faptele. Deciziile de scope MVP rămân la owner:

1. `RuleEvaluationEngine` — se redenumește după un motor real existent, sau rămâne mecanism separat, specific MVP, fără corespondent în Core?
2. `ObjectionEngine` — intră în MVP acum (fiindcă ORE e deja KPI activ), sau ORE rămâne în registru dar "neimplementat" până la o fază ulterioară?
3. Restul de 12 motoare excluse din MVP — toate amânate pentru fazele următoare, sau există vreunul cu prioritate ascunsă (ex. `PriorityEngine`, foarte des citat ca dependință a altor motoare deja incluse)?

---
*Document canonic pentru inventarul de motoare tehnice. Se coroborează cu `04-KPI-REG-001.md` (KPI) și `02-business-objects-5-pillars.md` (Event Catalog).*
