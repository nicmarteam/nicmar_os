# DECIZIA 35 — `Objection → FollowUp` — AUDIT CLOSED / NO IMPLEMENTATION

**Status:** audit complet, verificat direct din 3 documente sursă independente și din schema
DB reală. **Concluzie: nu se scrie cod.** Documentul de față e sursa de adevăr pentru orice
discuție viitoare despre această relație — previne re-deschiderea ei ca "gol uitat".

---

## Constatarea centrală

`Objection → FollowUp` **nu este o relație arhitecturală documentată, nicăieri**. Presupunerea
inițială (că un `BLOCK`/`HUMAN_REVIEW` la o obiecție ar trebui să declanșeze automat un
follow-up) era plauzibilă, dar **nesusținută de nicio sursă** — exact genul de asumpție pe care
disciplina acestui proiect a interzis-o explicit de la început.

## Dovezile, din 3 surse independente

**`01-business-objects-database.md`, linia 3171-3175:**
```
Contact
  ├─► Conversation ──► Objections / FollowUps
```
`Objection` și `FollowUp` sunt **obiecte frate**, generate ambele direct din `Conversation` —
niciodată unul din celălalt.

**`02-business-objects-5-pillars.md`, linia 60-62:**
```
NoResponseTimeout: System Event (Waiting) ➔ WF-FOLLOWUP-AUTO-001 (ContinuityEngine, FollowUpEngine)
InterestExpressed / ObjectionRaised / MeetingRequested: Business Events (Resolved) ➔
    Generează automat obiectele aferente (Objection, Meeting)
```
Trigger-ul documentat pentru `FollowUp` e **`NoResponseTimeout`** (tăcerea prospectului) — nu
rezultatul unei obiecții.

**`10-audit-general-nicmar-os.md`, linia 54:**
```
Clasificate, excluse din MVP: ContinuityEngine (contradicție 02/05, investigat)
```
Motorul care ar produce efectiv `NoResponseTimeout` **a fost deja exclus explicit din MVP**.

**Confirmare structurală, din schema reală**: `follow_ups` **nu are nicio coloană
`objection_id`** — doar `contact_id`, `conversation_id`. Schema n-a fost proiectată niciodată
să lege un follow-up de o obiecție anume.

## Ce NU se construiește, explicit

- `ObjectionCreated → FollowUp` (automatizare) — nesusținută de sursă
- `BLOCK → FollowUp` — nesusținută de sursă
- `HUMAN_REVIEW → FollowUp` — nesusținută de sursă
- Coloana `follow_ups.objection_id` — schema nu o cere, nicio sursă n-o documentează

## Harta corectă, actualizată

```
Contact
   ↓
Conversation
   ├──→ Objection   🟢 (Decizia 33/34)
   │
   └──→ FollowUp    🟢 (motor + API, dar trigger manual, nu automat)
```

Trigger-ul documentat pentru `FollowUp` rămâne:
```
NoResponseTimeout → ContinuityEngine → FollowUpEngine     🔴 (motor exclus din MVP)
```

## Clasificarea finală a zonei

| Element | Status |
|---|---|
| `Objection → FollowUp` (automatizare) | ⚪ nu e relație arhitecturală — nu se construiește |
| `FollowUp → Mission` | ⚪ decizie amânată intenționat, documentată deja în cod (`followup_engine.py`) |
| `NoResponseTimeout → FollowUp` | 🔴 motor (`ContinuityEngine`) exclus explicit din MVP |
| `FollowUpEngine`/API (creare manuală) | 🟢 funcțional, testat |
| `PriorityEngine ← FollowUp` (citire) | 🟢 funcțional real |

## Dacă apare vreodată nevoia

Dacă va exista o decizie de business explicită (a owner-ului, nu inventată tehnic) care leagă
un rezultat de obiecție de un follow-up, ea intră ca **decizie nouă**, cu propriul audit,
contract, RED/GREEN — niciodată ca "reparație" a acestei runde, pentru că nu exista nimic de
reparat.
