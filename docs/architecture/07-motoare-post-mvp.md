# NicMar OS — Specificații Tehnice: Cele 13 Motoare din Afara MVP

**Status:** Documentație pregătitoare, fără implementare de cod
**Scop:** Pregătește terenul pentru fazele următoare, după MVP. Nu schimbă scope-ul MVP-ENGINE-001 (rămas la 6 motoare, v. `06-harta-motoare-tehnice.md`).
**Sursă:** `docs/architecture/05-competente-37-motor1.md`
**Regulă de completare:** unde sursa nu specifică explicit un câmp (ex. "Ieșiri"), câmpul e marcat `— nespecificat explicit în sursă`, nu completat prin presupunere.

---

## Grupa 1 — Ritm & Continuitate Personală

### 1. DailyRhythmEngine
- **Responsabilități:** calculează încărcarea optimă a zilei, stabilește ordinea activităților, evită supraîncărcarea, menține consistența.
- **Intrări:** disponibilitate timp, profil identitate, misiunea anterioară, relații active, follow-up-uri, obiective.
- **Procese:** calculul încărcării optime, stabilirea ordinii activităților.
- **Ieșiri:** Misiunea Zilei, estimare timp, progres, configurarea zilei următoare.
- **Motoare conectate:** Motorul Continuității (rol conceptual, nu motor separat), Motorul Relației, Motorul Identității, Dashboard Operațional, Biblioteca Experienței.
- **Status oficial în sursă:** ✅ VALIDATĂ (10/10)

### 2. ResilienceEngine
- **Responsabilități:** detectează blocajele, le clasifică și le contorizează frecvența, alege automat cea mai bună micro-acțiune, adaptează ritmul utilizatorului, construiește profilul de reziliență, transmite informațiile către Motorul Identității și Motorul de Învățare.
- **Intrări:** — nespecificat explicit în sursă (implicit: semnal de blocaj raportat de utilizator).
- **Procese:** detectare → decizie → o singură acțiune recomandată → salvare → continuitate (tipar comun, propus ca Workflow Engine reutilizabil).
- **Ieșiri:** — nespecificat explicit ca listă, dar rezultă: o micro-acțiune unică recomandată, profil de reziliență actualizat.
- **Status oficial în sursă:** ✅ VALIDATĂ 10/10

### 3. HabitEngine
- **Responsabilități:** construiește obiceiuri, urmărește consecvența, detectează întreruperile, adaptează dificultatea, sincronizează rutina cu Misiunea Zilei.
- **Intrări:** profil utilizator, MissionEngine, SuccessEngine, UnblockingEngine, Dashboard.
- **Procese:** alegerea obiceiului optim, monitorizarea consecvenței, calculul seriilor, recalibrarea automată.
- **Ieșiri:** scor consecvență (Consistency Index), procent disciplină, serie activă, recomandări zilnice.
- **Motoare conectate:** Motorul Identității, Dashboard-ul Operațional, Motorul Învățării, SuccessEngine, MissionEngine, UnblockingEngine.
- **Status oficial în sursă:** ✅ VALIDATĂ 10/10

### 4. PriorityEngine
*(declarat de 2 ori în sursă, cu formulări ușor diferite — combinate mai jos)*
- **Responsabilități:** stabilește prioritățile zilnice, optimizează folosirea timpului, reduce încărcarea cognitivă, coordonează Dashboard-ul, recalculează permanent ordinea activităților, activează Focus Mode, optimizează energia utilizatorului.
- **Intrări:** MissionEngine, HabitEngine, FollowUpEngine, Dashboard, Calendar, Motorul Relației, Motorul Identității.
- **Procese:** — nespecificat complet în sursă (secțiunea se întrerupe imediat după titlu în ambele apariții).
- **Ieșiri:** — nespecificat explicit în sursă.
- **Notă din auditul anterior:** citat ca "motor conectat" de `HabitEngine`, `FollowUpEngine`, `CustomerRelationshipEngine` (3 din cele 6 motoare MVP) — candidat cu prioritate ridicată pentru o fază următoare timpurie.

---

## Grupa 2 — Relații Durabile & Prezentare

### 5. PresentationEngine
- **Responsabilități:** construiește prezentări personalizate, scurte și naturale, adaptate fiecărei persoane și situații. Generează o conversație, nu un discurs standard.
- **Intrări:** Motorul Relației, Motorul Identității, CustomerRelationshipEngine, PartnerRelationshipEngine, Biblioteca Experienței, istoricul conversațiilor, nivelul interesului, obiectivul persoanei.
- **Procese:** identifică nevoia dominantă (procesul se întrerupe în sursă imediat după).
- **Ieșiri:** — nespecificat explicit în sursă.
- **Legătură KPI:** alimentează **PES** (Presentation Effectiveness Score).

### 6. PartnerOnboardingEngine
- **Responsabilități:** coordonează integral procesul de transformare a unei persoane interesate într-un partener activ — activare, verificarea pașilor, inițializarea traseului de dezvoltare, sincronizarea tuturor motoarelor implicate.
- **Intrări:** PartnerRelationshipEngine, ObjectionEngine, PresentationEngine, Motorul Relației, Motorul Continuității (rol conceptual), datele noului partener.
- **Procese:** — nespecificat explicit în sursă.
- **Ieșiri:** — nespecificat explicit în sursă.

### 7. PartnerIntegrationEngine
- **Responsabilități:** coordonează integrarea completă a partenerului nou în ecosistemul NicMar OS — personalizarea onboarding-ului, sincronizarea motoarelor operaționale, monitorizarea progresului, detectarea timpurie a blocajelor, accelerarea autonomiei.
- **Intrări:** PartnerOnboardingEngine, Motorul Relației, Motorul Identității, MissionEngine, HabitEngine, PriorityEngine, istoricul partenerului.
- **Procese:** — nespecificat explicit în sursă.
- **Ieșiri:** — nespecificat explicit în sursă.
- **Legătură KPI:** PIP (Partner Integration Progress) — pe baza denumirii, nu confirmat literal ca legătură directă în text.

---

## Grupa 3 — Liderul și Mentorul Autonom

### 8. MentorGuidanceEngine
- **Responsabilități:** coordonează întregul proces de mentorat. Nu spune mentorului ce să facă pas cu pas — îl ajută să ia cele mai bune decizii folosind istoricul partenerului, profilul identitar, competențele parcurse, ritmul de dezvoltare, experiențele validate.
- **Intrări:** PartnerIntegrationEngine, Motorul Relației, Motorul Identității, Biblioteca Experienței, PDI, PIP.
- **Procese:** — nespecificat explicit în sursă.
- **Ieșiri:** — nespecificat explicit în sursă.

### 9. TeamCoordinationEngine
- **Responsabilități:** coordonează dezvoltarea întregii echipe prin prioritizarea inteligentă a intervențiilor liderului. Optimizează permanent raportul timp investit / impact obținut.
- **Intrări:** MentorGuidanceEngine, PartnerIntegrationEngine, Motorul Relației, Motorul Continuității (rol conceptual), Motorul Identității, PDI, PIP, MEI.
- **Procese:** evaluează starea fiecărui partener, stabilește prioritățile zilnice (procesul se întrerupe în sursă imediat după).
- **Ieșiri:** — nespecificat explicit în sursă.

### 10. LeadershipDevelopmentEngine
- **Responsabilități:** coordonează identificarea, dezvoltarea și maturizarea viitorilor lideri din echipă. Construiește trasee personalizate de leadership.
- **Intrări:** TeamCoordinationEngine, MentorGuidanceEngine, PartnerIntegrationEngine, Motorul Relației, Motorul Continuității (rol conceptual), Motorul Identității, PDI, PIP, MEI, TDI.
- **Procese:** — nespecificat explicit în sursă.
- **Ieșiri:** — nespecificat explicit în sursă.

---

## Grupa 4 — Învățare Colectivă & Evaluare Finală

### 11. ExperienceLibraryEngine
- **Responsabilități:** colectează experiențele validate, le clasifică automat, elimină duplicatele, recomandă experiențe similare, identifică cele mai eficiente practici, conectează experiențele cu toate competențele, alimentează Motorul de Învățare.
- **Intrări:** rezultate validate, experiențe raportate, feedback, KPI-urile tuturor motoarelor, istoricul utilizatorilor.
- **Procese:** — nespecificat explicit în sursă.
- **Ieșiri:** — nespecificat explicit în sursă.
- **Context:** introdus la Competența 35, marcat explicit ca "începutul inteligenței colective din NicMar OS."
- **Legătură KPI:** ERI (Experience Reuse Index) — pe baza denumirii/rolului, nu confirmat literal ca legătură directă în text.

### 12. PerformanceEvaluationEngine
- **Capitol sursă:** "Performance & Intelligence Layer"
- **Responsabilități:** centralizează toate KPI-urile, analizează evoluția utilizatorului, detectează tendințe, identifică punctele forte, identifică oportunitățile de dezvoltare, generează recomandarea cu impact maxim, furnizează tabloul unic de performanță.
- **KPI-uri unificate oficial (citat direct din sursă):** Daily Impact Score (DIS), Customer Relationship Health (CRH), Partner Development Index (PDI), Presentation Effectiveness Score (PES), Objection Resolution Effectiveness (ORE) — plus restul din registrul de 12 operaționali (v. `04-KPI-REG-001.md`).
- **Intrări/Ieșiri detaliate:** — nespecificat ca listă explicită în sursă (rolul e descris narativ, nu ca schemă de date).

### 13. AutonomyEngine
- **Rol:** orchestratorul final al întregului Motor 1 — agregă toate cele 12 KPI-uri strategice (inclusiv AMS).
- **Introdus la:** Competența 37, ultima din Motorul 1 ("Autonomia Completă a Utilizatorului").
- **KPI nou strategic asociat:** AMS (Autonomy Maturity Score) — definiție completă deja inclusă în `04-KPI-REG-001.md`, KPI-013.
- **Status oficial în sursă:** ✅ PROPUSĂ PENTRU VALIDARE
- **Notă din sursă:** "Elimină senzația de sfârșit de drum. Înlocuiește finalizarea cu începutul unui nou ciclu de dezvoltare." — utilizatorul alege doar direcția strategică, sistemul configurează automat traseul următor (decizie asistată).

---

## Observație generală asupra completitudinii

Pentru 8 din cele 13 motoare, secțiunea "Procese" și/sau "Ieșiri" **se întrerupe brusc în document** (sursa pare trunchiată la acele puncte, posibil o limitare de lungime la generarea inițială a documentului). Aceste goluri sunt marcate explicit mai sus, nu completate prin presupunere. Dacă există o continuare a acestor secțiuni salvată separat (alt fișier sau altă conversație), ar trebui căutată înainte ca aceste 13 motoare să treacă la faza de specificare completă pentru implementare.

---
*Document pregătitor. Nu modifică scope-ul MVP-ENGINE-001 (6 motoare, v. `06-harta-motoare-tehnice.md`).*
