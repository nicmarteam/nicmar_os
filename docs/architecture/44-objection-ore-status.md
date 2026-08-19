# Decizia 44 — Objection ORE

Status: **BLOCKED BY DEFINITION** (owner, 19 august 2026)

## 1. Rezultatul auditului

Verificate exhaustiv toate cele 16 fișiere din `docs/architecture/` +
`migrations/` care menționează `ORE`. Concluzie, verbatim din surse:

| Sursă | Constatare |
|---|---|
| `04-KPI-REG-001.md` (registru oficial) | "Formula: va fi definită în KPI-MODEL-001" — document **inexistent** în repo |
| `17-kpi-dependency-map.md` | "Componente: nespecificate în sursă", "Date necesare: nedefinite" |
| `02-business-objects-5-pillars.md` | Doar menționează evenimentul teoretic `ObjectionRaised → KPI influențați: ORE`, fără formulă |
| `05-competente-37-motor1.md`, Competența 29 | Nu menționează ORE explicit — descrie doar actualizarea `CRH`/`PDI` |
| `migrations/002_seed_minimal.sql` | `ORE` există doar ca rând `status='PROPOSED'`, niciodată avansat |
| `21-objection-engine-decizii-preliminare.md` | O singură mențiune speculativă, nu o formulă |

**Concluzie:** ORE e singurul KPI din registru fără niciun precedent de
calcul — nici măcar un placeholder documentat, spre deosebire de
DIS/PDI/PIP (care au `1.0` fix, dar cel puțin un producător
funcțional și o justificare explicită a valorii placeholder).

## 2. Decizie explicită a owner-ului

**Varianta B aleasă**, respinsă Varianta A (`ORE = 1.0` fix,
simetric cu DIS/PDI/PIP): un placeholder ar transforma un KPI menit
să măsoare eficiență într-un simplu indicator de prezență, cu risc de
contaminare a `OPI` (compozit, depinde de toți cei 12 KPI
operaționali) și a oricărei decizii bazate ulterior pe ORE.

**Implementarea tehnică a ORE este interzisă** până la aprobarea unei
definiții business explicite — ce măsoară exact, ce semnal real îl
demonstrează, ce date sunt necesare pentru calcul.

## 3. Motiv oficial (pentru harta deciziilor)

> ORE este declarat în registrul KPI, însă nu există în repository o
> definiție validată a formulei, componentelor sau datelor necesare.
> Implementarea ar necesita inventarea unei formule și este interzisă
> până la aprobarea definiției business.

## 4. Ordinea corectă, stabilită explicit

```
ORE
 ↓
Definiție business  (Decizia 44A — de făcut acum, NU tehnic)
 ↓
Ce înseamnă „eficiența răspunsului”?
 ↓
Semnal real colectat
 ↓
Date necesare
 ↓
Formula
 ↓
Normalizare 0–100
 ↓
Contract tehnic 44
 ↓
RED
 ↓
GREEN
 ↓
PostgreSQL
 ↓
API / Workbench
```

Nici semnalul candidat ("A funcționat răspunsul?", Ecranul 9,
Competența 29) nu se implementează încă — definirea precede colectarea
datelor, nu invers.

## 5. Harta oficială

```
37  Partner Workbench          🟢 CLOSED
38  Mission Workbench          🟢 CLOSED
39  Priority API               🟢 CLOSED
40  Priority Workbench         🟢 CLOSED
41  Audit final E2E            🟢 VALIDATED
42  Contact Events             🟢 CLOSED
43  Objection Events           🟢 CLOSED

44  Objection ORE              🔴 BLOCKED BY DEFINITION
44A ORE Business Definition    ⏳ URMEAZĂ (decizie de business, nu de cod)
45  FollowUp DIS → Workbench   🔴 BACKLOG
```

## 6. Baseline

**463/463 PASSED** — neschimbat, niciun cod atins de această decizie.
