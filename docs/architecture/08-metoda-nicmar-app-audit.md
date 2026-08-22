# Audit 08 — Aplicația "Metoda NicMar" vs. NicMar OS

Status: DRAFT — audit factual, de verificat de owner
Data: 22 august 2026
Sursă: verificare directă în arhiva aplicației "Energia ta naturală
după 45 de ani" (React/TypeScript/Firebase) și în repo-ul `nicmar_os`
(Python/PostgreSQL)

**Nu decide o integrare. Nu propune arhitectură.** Constată ce există
în fiecare sistem, ca bază pentru o decizie viitoare — la fel ca 07B.

---

## Context

În discuția cu un alt asistent AI au apărut două documente despre
aplicația "Metoda NicMar": o descriere a aplicației (dată de owner) și
un "audit tehnic" scris de asistentul AI **integrat în chiar acea
aplicație**, pe baza propriilor sale instrucțiuni de sistem. Acesta din
urmă e o descriere de sine, nu o verificare independentă în cod — de
aceea acest document reface verificarea direct pe fișierele reale din
arhivă.

---

## 1. Ce există cu adevărat în cod (confirmat)

**Stack tehnic** (`package.json`): React 19, TypeScript, Firebase
12.9 (Firestore + Auth), i18next, Vite. Rulează ca aplicație web/PWA,
fără backend propriu-zis — logica trăiește în client, sincronizată cu
Firestore.

**Amploarea reală a aplicației** e mult mai mare decât "un cadou de
10+5 zile": peste 140 de componente React, incluzând module complete
de CRM — gestionare contacte (`ContactsView`, `ContactCard`),
follow-up (`FollowUpSuggestionsModal`), coaching pentru obiecții
(`ObjectionCoachModal`, `ObjectionHandlerCard`), onboarding parteneri
(`PartnerJourneyView`, `AcademyView`), clasament (`LeaderboardView`),
dashboard de performanță (`PerformanceDashboardView`), plus modulul de
călătorie a oaspetelui (`GuestModeView`, `GuestJourneyManager`).

**Semnalele de progres chiar există** — dar ca dâmpuri pe entitatea
`Contact` (`types.ts`), nu ca evenimente separate:
`journey_start_date`, `lastActiveDay`, `lastDayCompleted`, și un set
complet de câmpuri de trial: `trial_status`, `trial_offer_sent_at`,
`trial_start_at`, `trial_expiry_at`, `trial_gift_url`,
`trial_ref_code`.

**Regulile de acces** (`firestore.rules`) confirmă modelul descris:
un guest scrie propria activitate în
`users/{userId}/liveTracking/{guestId}`, doar mentorul (owner-ul acelui
`userId`) poate citi acele date. Admin = listă fixă de 3 email-uri.

## 2. Ce nu se confirmă — era descriere, nu fapt

Pipeline-ul de evenimente propus de celălalt asistent AI —
`GIFT_SENT → GIFT_OPENED → JOURNEY_STARTED → DAY_2 → ... →
DISCOVERY_READY → INVITE_READY` — **nu există nicăieri în cod**.
Verificat direct: zero rezultate pentru aceste nume în toată arhiva.
Era o propunere, prezentată ca și cum ar descrie ce face deja
aplicația.

## 3. Descoperirea principală: două sisteme, două identități diferite pentru aceeași persoană

| | Metoda NicMar (aplicația) | NicMar OS |
|---|---|---|
| Bază de date | Firestore (Firebase, NoSQL) | PostgreSQL (relațional) |
| Limbaj/runtime | React + TypeScript, client-side | Python, backend |
| Entitatea persoană | `Contact` (`types.ts`), identificat prin `guestId`/`id` — string Firestore | `Contact` (`contact_engine.py`), identificat prin `id: UUID`, generat de PostgreSQL |
| Owner-ul contactului | `userId` (Firebase Auth) | `owner_id` (UUID) |

**Nu există azi nicio legătură între cele două.** Dacă Elena e
"contact" în ambele sisteme, ele nu știu una de alta — sunt două
înregistrări separate, cu două istorii separate. Orice integrare
reală trebuie să răspundă întâi la o întrebare de identitate, nu de
funcționalitate: **cum recunoaște NicMar OS că un `Contact` din
Firestore corespunde unui `Contact` din PostgreSQL?** Niciunul din
documentele primite de la celălalt asistent nu pune această întrebare.

## 4. Suprapunere funcțională, nu doar tehnică

Aplicația React are deja, construite și funcționale, o parte din
lucrurile pe care `nicmar_os` le construiește separat, ca motoare
Python: sugestii de follow-up, coaching de obiecții, onboarding de
parteneri, clasament, dashboard de performanță. Asta nu e doar o
observație tehnică — e o întrebare de strategie: cele două sisteme
sunt gândite să coexiste (fiecare cu rolul lui), sau există riscul
real de a construi de două ori același lucru, în două tehnologii
diferite?

## 5. Notă separată — "Contractul 48" (corectat)

**Corecție față de versiunea anterioară a acestui audit:** la
verificarea inițială, Contractul 48 nu exista în arhiva `nicmar_os`
primită atunci — confirmat explicit, ca fișier și ca text. O arhivă
mai nouă, primită ulterior, confirmă însă că **`48-invite-contract.md`
există**, cu status "Contractul e complet — RED poate începe", și că
există deja implementare reală: `src/engines/invite/invite_engine.py`
(94 linii) și 11 teste în `tests/test_invite_engine.py` (244 linii).

Concluzia corectă: Contractul 48 (INVITE) e real și era deja în lucru
activ (fază RED/GREEN) în momentul în care celălalt asistent a propus
punerea lui pe pauză pentru acest audit — nu o lucrare ipotetică. Asta
schimbă miza deciziei: "pauză pentru audit" înseamnă întreruperea unei
implementări deja începute, nu doar amânarea unui plan. Decizia rămâne
a owner-ului, dar cu această informație corectă, nu cu presupunerea
că nu exista nimic de pus pe pauză.

**Lecție de proces:** orice afirmație de tipul "X nu există în repo"
făcută de mine e valabilă doar pentru arhiva verificată în acel
moment, nu pentru starea curentă de pe GitHub — care poate avansa în
paralel, prin alte unelte conectate direct la repo. Următoarea dată
când o discrepanță de acest fel apare, cea mai sigură verificare e o
arhivă cât mai recentă, nu presupunerea că lipsa dintr-o arhivă mai
veche înseamnă lipsă reală.

---

## Ce nu decide acest document

Nu propune un model de identitate comună, nu alege ce se integrează
și ce rămâne separat, nu decide dacă cele două sisteme fuzionează sau
coexistă. Următorul pas, dacă se dorește continuarea, e o decizie de
scope similară cu 07A — dar pentru relația dintre cele două sisteme,
nu doar pentru SOURCE.
