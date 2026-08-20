# Scope Proposal — Prospectare & Recrutare

Status: PROPUNERE DE SCOPE (owner, 20 august 2026). **Nu este contract
tehnic. Nu autorizează implementare.** Decizia de implementare rămâne
`OPEN`, necesită aprobare separată, explicită.

## 0. Regula de guvernanță aplicată

> Auditul produce adevărul. Decizia produce scope-ul. Contractul
> produce implementarea.

Acest document se oprește la a doua etapă. Recomandarea din secțiunea
6 e rezultatul unei analize pe criterii explicite — **nu e o decizie
deja luată**.

## 1. Problema confirmată

Confirmată direct din experiența reală de utilizare, nu dedusă din
arhitectură sau presupusă:

> **Liderii au nevoie de mai mulți prospecti noi.**

Blocajul actual în bucla `Prospect → Conversație → Obiecție →
FollowUp → Partener → Lider` e la intrare, nu la mijloc — cele 7
engine-uri deja construite (Contact, Conversation, Objection,
FollowUp, Partner, Mission, Priority) gestionează bine ce intră deja
în sistem, dar niciunul nu ajută liderul să găsească oameni noi.

## 2. Scopul etapei

> **NicMar OS trebuie să ajute liderul să genereze constant prospecti
> noi, atât offline cât și online, și să-l ghideze în transformarea
> lor în conversații reale și apoi în parteneri.**

Criteriul de succes al etapei, dacă va fi aprobată spre implementare:

> Liderul intră în NicMar OS → știe pe cine să contacteze → știe cum
> să abordeze → execută → înregistrează rezultatul → primește
> următorul pas. Măsurat prin: *"liderul a generat X prospecti noi și
> a început Y conversații"* — nu prin existența unui engine.

## 3. Bucla economică

```
                    ┌── ONLINE
                    │
PROSPECTARE ─────────┤
                    │
                    └── OFFLINE
                         ↓
                    CONVERSAȚIE
                         ↓
                    RECRUTARE
                         ↓
                     PARTENER
                         ↓
                      LIDER
                         ↓
                  NOI PROSPECTI (loop)
```

Infrastructura deja construită (Contact→Priority) rămâne neatinsă —
devine "aval" în această buclă. Etapa propusă construiește "intrarea"
și legătura dintre intrare și ce există deja.

## 4. Sursă — nimic inventat, totul recuperat din documentație existentă

Auditul de azi a găsit **12 "Conversații" originale** (documentul
`05-competente-37-motor1.md`), dintre care 3 (01, 04, 06) corespund
direct celor 3 engine-uri deja construite (Objection, FollowUp).
Celelalte 9 rămân nedocumentate în cod. Din acestea, 7 sunt candidați
direcți pentru problema confirmată la Punctul 1.

## 5. Candidați analizați

| # | Conversație | Ce face |
|---|---|---|
| 02 | Pregătire Postare | Generează text de postare pentru rețele sociale (Facebook/WhatsApp/Instagram/TikTok/LinkedIn); liderul postează manual, revine manual cu reacțiile |
| 03 | Cu Cine Pot Vorbi Astăzi | Recomandă zilnic, din baza existentă, cu cine să vorbească |
| 07 | Invitație La Cafea/Zoom | Formulează invitația la întâlnire |
| 09 | Recomandare | Cere recomandări de la contacte existente |
| 10 | Reactivare | Reactivează contacte vechi/reci |
| 18 | Lista de Relații | Entitate nouă (`Relationship`), organizează rețeaua personală a liderului cu scoruri automate |
| 19 | Inițierea Primelor Conversații | Abordarea inițială a unei persoane noi |

## 6. Evaluare pe criterii

Cinci criterii aplicate egal tuturor candidaților, nu alese să
favorizeze un răspuns dinainte stabilit:

1. Cât de direct produce prospecti noi
2. Cât de mult ajută un lider care încă nu știe să recruteze
3. Viteză de livrare (complexitate tehnică)
4. Independență de integrări externe
5. Ușurință de măsurare a rezultatului în sistem

| Candidat | 1. Direct | 2. Ajută lider nou | 3. Viteză | 4. Fără integrări | 5. Măsurabil |
|---|---|---|---|---|---|
| **09 — Recomandare** | 🟢🟢🟢 | 🟢🟢 | 🟢🟢🟢 zero entitate nouă | 🟢🟢🟢 | 🟢🟢🟢 |
| **10 — Reactivare** | 🟢🟢🟢 | 🟢🟢 | 🟢🟢🟢 zero entitate nouă | 🟢🟢🟢 | 🟢🟢🟢 |
| 03 — Cu cine vorbesc azi | 🟢🟢 | 🟢🟢🟢 | 🟡 parțial dependent de 18 pentru varianta completă | 🟢🟢🟢 | 🟢🟢 |
| 18 — Lista de relații | 🟡 organizează materia primă, nu produce direct | 🟢🟢🟢 | 🟡 entitate nouă, dar simplă | 🟢🟢🟢 | 🟢 indirect |
| **02 — Pregătire postare** | 🟡 valoare potențială reală pentru prospectarea online, dar rezultatul depinde de comportamentul liderului și al platformei externe | 🟢🟢 | 🟡 generator simplu, dar valoarea finală se petrece în afara aplicației | 🟢🟢🟢 (confirmat, Decizia 4 — fără API social media) | 🔴 greu de măsurat direct în MVP fără revenire manuală a liderului |
| 07 — Invitație | 🟡 convertește, nu generează prospect nou | 🟢 | 🟢🟢 | 🟢🟢🟢 | 🟢 |
| 19 — Inițierea conversațiilor | 🟡 spec incompletă în sursă (auto-corecție inline observată în document) | — | — | — | — |

## 7. Recomandare de scope

> **09 + 10 prezintă cea mai bună combinație dintre impact direct
> asupra generării de prospecti, complexitate redusă (zero entitate
> nouă în schema DB, ambele funcționează peste `contacts` deja
> existent), independență completă de integrări externe, și
> măsurabilitate directă în sistem.**
>
> **03** e candidat secundar viabil — funcțional azi peste `contacts`
> existent, cu valoare completă condiționată de 18.
>
> **02** are valoare potențială reală pentru prospectarea online, dar
> rezultatul este dependent de comportamentul liderului și al
> platformei externe, și e mai greu de măsurat direct în MVP.

Aceasta e o **recomandare rezultată din analiză**, nu o decizie.

## 8. Decizie de implementare

**Status: OPEN.**

Niciun element din secțiunea 5 nu intră automat în lucru prin simpla
prezență în acest document sau prin recomandarea din secțiunea 7.
**Nu se implementează nimic până când acest document nu este aprobat
separat**, explicit, de owner.

Dacă/când se aprobă un candidat (sau o combinație), pasul următor
respectă disciplina deja aplicată consecvent în acest proiect:

```
acest document (scope aprobat)
        ↓
audit tehnic țintit pe candidatul ales
        ↓
contract tehnic
        ↓
RED
        ↓
GREEN
        ↓
PostgreSQL real
        ↓
regresie
        ↓
CI
        ↓
verificare independentă
```

## 9. Ce rămâne neatins

- Cele 7 engine-uri deja construite (Contact→Priority) — infrastructură
  aval, neschimbată
- ORE (Decizia 44) — rămâne `BLOCKED BY DEFINITION`, neatins
- Backlog-ul din `audit-continuitate-consolidat.md` (Register, ARCHIVED,
  Password Recovery, RBAC, JWT, editare date) — rămâne clasificat, fără
  prioritizare nouă implicită prin acest document
- Competențele 15-17, 20-23, 28, 32-37 — rămân documentate, neconstruite,
  neanalizate în acest document (candidați pentru o etapă viitoare,
  "Dezvoltare Lideri", separată de "Prospectare & Recrutare")
