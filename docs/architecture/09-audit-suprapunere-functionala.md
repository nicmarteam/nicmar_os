# Audit 09 — Suprapunere Funcțională: Metoda NicMar vs. NicMar OS

Status: DRAFT — audit factual, de verificat de owner
Data: 22 august 2026
Sursă: citire directă în ambele coduri (arhiva "Metoda NicMar" și
`nicmar_os-main__2_.zip`)

**Nu decide ownership.** Doar constată ce face, ce citește/scrie și ce
e testat, în fiecare sistem, funcție cu funcție — exact inputul cerut
pentru Ownership Matrix, nu Ownership Matrix în sine.

Legendă comparație (folosită la final):
`A` = doar Metoda NicMar · `B` = doar NicMar OS · `C` = ambele, aceeași
funcție · `D` = parțial în ambele · `E` = există aparent în ambele, dar
funcționalitatea e diferită la fond

---

## 1. Follow-up

**Metoda NicMar** — `components/FollowUpSuggestionsModal.tsx`. La
deschidere, apelează `generateFollowUpSuggestions(contact)` din
`services/geminiService` — **cere text generat live de Gemini**, pe
baza datelor contactului. Nu persistă nimic structurat: sugestiile
sunt afișate și dispar, nu devin înregistrare urmăribilă. Fără
clasificare, fără status, fără test automat vizibil.

**NicMar OS** — `src/engines/followup/followup_engine.py`. Motor
persistat: creează rânduri în `follow_ups` cu status
(`PENDING/COMPLETED/POSTPONED/RESCHEDULED`), tranziții controlate
printr-o singură cale de scriere, evenimentul `FollowUpTriggered`
scrie KPI `DIS` la creare. Zero generare de text liber — exact
opusul deciziei din Metoda NicMar.

**Verdict comparație: `E`** — numele e același, funcția e opusă:
una generează text efemer prin AI, cealaltă persistă stare
structurată, testabilă, fără AI generativ.

---

## 2. Obiecții

**Metoda NicMar** — `components/ObjectionCoachModal.tsx`. Chat live cu
Gemini (`getObjectionCoachResponse`, `generateObjectionResponses`),
plus un "flux rapid" de generare de răspunsuri. Conversație ținută în
`useState` local — nu se persistă în Firestore ce obiecție a avut cine
sau ce răspuns s-a folosit.

**NicMar OS** — `src/engines/objection/objection_engine.py`
(`ObjectionEngine`, Decizia 2/21, MVP confirmat). Clasifică obiecția
într-una din 13 categorii fixe (`ALL_CATEGORIES`), persistă
`objection_text`, `response_text`, `response_variant_used`, validare
explicită human-in-the-loop pentru disclaimer de venituri. Contractul
exclude explicit generarea liberă de text (Decizia 1).

**Verdict comparație: `E`** — aceeași observație ca la Follow-up:
Metoda NicMar rezolvă obiecția prin AI generativ efemer; NicMar OS
clasifică și persistă, fără AI generativ, cu validare umană obligatorie.

---

## 3. Onboarding (parteneri)

**Metoda NicMar** — `components/AcademyView.tsx` +
`PartnerJourneyView.tsx`. Structură reală, cu etape denumite
(`PartnerJourneyType`: IGNITION, PREPARATION, DISCOVERY, CONFIDENCE,
MAIN), progres pe sarcini urmărit explicit
(`onUpdateProgress(partnerContactId, taskId, isCompleted)`), tranziții
între etape (`onTransitionJourney`). E funcțional și structurat — nu
e generat de AI.

**NicMar OS** — **absent din cod.** `PartnerOnboardingEngine` apare
doar în `docs/architecture/07-motoare-post-mvp.md` (§6), descris
narativ, marcat explicit "Procese: nespecificat" și "Ieșiri:
nespecificat" — adică document de intenție, zero implementare.

**Verdict comparație: `A`** — există doar în Metoda NicMar, și acolo e
real, testabil manual, mai matur decât orice există în `nicmar_os`
pentru acest subiect.

---

## 4. Leaderboard

**Metoda NicMar** — `components/LeaderboardView.tsx`. Afișează
`LeaderboardEntry[]` primit ca props, sortabil (lunar/săptămânal/
comenzi personale). Datele **nu vin din urmărirea automată a
aplicației** — sunt încărcate manual prin `onUpload(files)` (import de
fișier), cu opțiune de `onReset`. E un vizualizator peste un import
manual, nu un calcul automat din activitate.

**NicMar OS** — absent din cod, absent și din documentele de arhitectură
consultate (nicio mențiune "Leaderboard").

**Verdict comparație: `A`** — există doar în Metoda NicMar, dar ca
import manual de date externe, nu ca motor de calcul.

---

## 5. Performanță

**Metoda NicMar** — `components/PerformanceDashboardView.tsx` +
`services/statistics.ts`. Calculează statistici (`calculateStats`,
`getChartData`) pe baza `KeyPersonSheetHistory` (istoricul sesiunilor
de consiliere/counseling), afișate ca playere de tip "variație vs.
perioada anterioară". Calcul client-side, pe date introduse manual de
lider prin fișele de consiliere.

**NicMar OS** — `PerformanceEvaluationEngine` apare doar în
`07-motoare-post-mvp.md` (§12), descris ca centralizator de KPI
(DIS, CRH, PDI, PES, ORE), cu "Intrări/Ieșiri: nespecificat ca listă
explicită" — document de intenție, zero cod.

**Verdict comparație: `A`** — există doar în Metoda NicMar, calculat pe
alt tip de date (fișe de consiliere) decât KPI-urile pe care
`PerformanceEvaluationEngine` intenționează să le centralizeze
(DIS/CRH/PDI/PES/ORE — evenimente din motoarele Python).

---

## 6. Contact (persoana)

Deja documentat detaliat în `08-metoda-nicmar-app-audit.md` §3 — repet
aici doar esența pentru tabelul de sinteză:

**Metoda NicMar** — `Contact` (`types.ts`), în Firestore, identificat
prin `id`/`guestId` (string). Câmpuri proprii: `journey_start_date`,
`lastActiveDay`, `lastDayCompleted`, `trial_status` și restul
câmpurilor de trial.

**NicMar OS** — `Contact` (`contact_engine.py`), în PostgreSQL,
identificat prin `id: UUID`. Câmpuri proprii: `relationship_category`,
`relationship_level`, `perceived_interest` (Decizia 47).

**Verdict comparație: `D`** — parțial în ambele: e conceptul aceleiași
persoane, cu câmpuri complementare (una urmărește parcursul de 15
zile, cealaltă urmărește relația percepută de lider), dar identitatea
nu e comună — vezi 08 §3.

---

## 7. Misiuni / acțiuni prioritare

**Metoda NicMar** — `PriorityAction` (`types.ts`) +
`PriorityActionCard.tsx`/`PriorityActionModal.tsx`. Structură simplă:
o acțiune cu titlu, descriere, un contact asociat și un mesaj
pre-completat — gândită ca sugestie punctuală pentru lider, nu ca
proces cu stare/tranziții.

**NicMar OS** — `MissionEngine` (`mission_engine.py`), motor complet:
stări (`missions.status`), tranziții controlate, `MissionGenerated/
Started/Completed`, KPI `DIS` persistat la completare. Plus
`PriorityEngine` (`priority_engine.py`) — strict read-only, derivă
prioritate din Mission + FollowUp active, fără să scrie nimic.

**Verdict comparație: `E`** — numele "acțiune prioritară" seamănă, dar
Metoda NicMar are un obiect static de afișare, iar NicMar OS are un
motor de stare persistată plus un motor separat de calcul al
priorității. Nu sunt aceeași funcție.

---

## 8. Coaching

**Metoda NicMar** — `NicMarCoachModal.tsx`. Chat live cu Gemini
(`getCoachResponse`), conversație generică de coaching, ținută doar în
`useState` — nu persistă în Firestore.

**NicMar OS** — **absent din cod.** Niciun engine sau agent dedicat
"coaching" — cel mai apropiat conceptual e `ObjectionEngine` (răspuns
la obiecții specifice, nu coaching general), care e explicit altceva
(v. §2).

**Verdict comparație: `A`** — există doar în Metoda NicMar, ca sesiune
AI generativă efemeră.

---

## Sinteză

| Funcție | Verdict | De ce |
|---|---|---|
| Follow-up | `E` | Nume identic, funcție opusă (AI generativ efemer vs. stare persistată fără AI) |
| Obiecții | `E` | Idem — coaching AI efemer vs. clasificare persistată cu validare umană |
| Onboarding parteneri | `A` | Doar în Metoda NicMar, structurat și funcțional |
| Leaderboard | `A` | Doar în Metoda NicMar, dar pe import manual, nu calcul automat |
| Performanță | `A` | Doar în Metoda NicMar, pe date de consiliere, nu pe KPI-urile Python |
| Contact | `D` | Parțial în ambele, câmpuri complementare, identitate necomună (v. 08 §3) |
| Misiuni/acțiuni | `E` | Obiect static de afișare vs. motor de stare + motor separat de prioritate |
| Coaching | `A` | Doar în Metoda NicMar, sesiune AI generativă |

**Observație centrală, utilă pentru Ownership Matrix:** nu există
niciun caz curat de duplicare (`C`) în acest audit. Cele trei cazuri
`E` (Follow-up, Obiecții, Misiuni) sunt cele mai importante de
clarificat înainte de orice decizie de ownership — pentru că numele
identic ascunde o diferență reală de fond (AI generativ, efemer, fără
persistare vs. stare persistată, testată, fără AI). A decide
"ownership" pe baza numelui, fără această distincție, ar însemna
alegerea sistemului greșit pentru nevoia greșită.

---

## Ce nu decide acest document

Nu alege sistemul responsabil pentru fiecare funcție. Asta rămâne
pasul următor (Ownership Matrix), pe baza distincțiilor de fond
constatate aici — în special observația `E` de mai sus.
