# Decizia 07A — SOURCE Scope Decision

Status: DRAFT — de aprobat de owner
Data: 22 august 2026
Sursă: `docs/architecture/source-1.0-metodologie.md` (BUSINESS TRUTH),
`docs/market-listening/Saptamana_1.md` (Experiment 01)

**Nu este contract tehnic. Nu autorizează implementare.** E o decizie
de scope: unde se poziționează SOURCE față de arhitectura existentă,
înainte de orice audit sau cod.

---

## §0 — Purpose

Stabilește dacă și cum SOURCE intră în roadmap-ul NicMar OS, fără să
decidă încă forma lui tehnică (motor separat, modul, capability
layer). Separă explicit **decizia de scope** de **proiectarea
tehnică** — cele două nu se fac în același document, ca să nu alunece
una în cealaltă.

---

## §1 — Business Context

MVP-ENGINE-001 (6 motoare, v. `06-harta-motoare-tehnice.md`) pornește
din punctul în care persoana e deja contact:

`CONTACT → CONVERSAȚIE → RELAȚIE → PARTENER`

Metodologia SOURCE 1.0 (`source-1.0-metodologie.md`) descrie ce se
întâmplă **înainte** de acel punct, ca practică deja testată de owner,
nu ca idee nouă:

`OM NOU → ATRACȚIE → CONECTARE → PROSPECT`

Fără acest flux, toate cele 6 motoare MVP lucrează pe aceeași bază de
oameni, care se epuizează. SOURCE este condiția care alimentează
restul sistemului, nu o funcționalitate adițională.

---

## §2 — What Is Validated

Validat ca practică reală de owner, în `source-1.0-metodologie.md`:

- Cele trei căi: **ONLINE** (prospectare directă, conținut, Market
  Listening), **OFFLINE** (persoane noi, conectare, capturare
  contact), **REACTIVARE** (Black Box, revenire după 3-6 luni)
- Metoda concretă de găsire a audienței pe Facebook (Etapa 2 din
  metodologie) — pas cu pas, cu volum și rată de conversie reale
- Market Listening ca etapă — testat o dată ca Experiment 01
  (`docs/market-listening/Saptamana_1.md`), cu ipoteze nevalidate
  încă de un om real din avatar

Ce **nu** e validat încă: nicio ipoteză din Experiment 01, nicio
performanță de conținut, niciun rezultat de Reel testat. Rămân
ipoteze până la bucla de validare din acel document.

---

## §3 — What SOURCE Means

> SOURCE este stratul de generare și captare a fluxului de persoane
> noi până la statutul de prospect. Recrutarea începe cu lucrul
> prospectului și continuă prin `CONNECT → DISCOVER → INVITE →
> PRESENT → CLIENT/PARTNER`.

SOURCE nu este separat de recrutare — **o alimentează**. Fără flux
continuu de persoane noi, etapele de recrutare lucrează pe aceeași
bază de oameni, care se epuizează. Delimitarea de mai sus separă unde
începe munca de fiecare tip (generare de flux vs. lucrul propriu-zis
al prospectului), nu declară SOURCE ca fiind în afara recrutării.

**Ideea centrală a acestei decizii:** SOURCE e tratat ca necesitate de
business înainte de a fi tratat ca arhitectură software. Asta previne
două extreme simetrice: (a) amânarea recrutării până "după ce avem
toate motoarele", și (b) începerea implementării (Content Engine, AI,
automatizări) fără să se știe încă ce anume trebuie sistemul să facă.

---

## §4 — What Is Missing — Business Capability Categories

Categorii de capacitate de business care nu au azi niciun corespondent
în arhitectură — enumerate ca **întrebări de investigat la audit**, nu
ca specificație:

- 🔴 Captarea și stocarea unei persoane găsite prin SOURCE, înainte
  să devină `Contact` în sensul actual al sistemului
- 🔴 Fluxul de prospectare directă (găsire → cerere → status
  necunoscut la acceptare → prima interacțiune observabilă)
- 🟡 Market Listening ca sursă de date recurentă (nu doar document
  scris manual o dată)
- 🔴 Fluxul audiență/conținut (ce se publică, ce reacție se
  urmărește, cum ajunge înapoi în Market Listening)
- 🔴 Reactivarea persoanelor vechi (Black Box) după 3-6 luni

Fiecare categorie de mai sus rămâne o **întrebare pentru audit**, nu o
componentă de construit. Care dintre ele devine prima competență
tehnică SOURCE se decide după audit, nu aici.

---

## §5 — What Is Explicitly NOT Being Built

Nu se construiește, la această decizie sau ca urmare directă a ei:

- AI care caută sau selectează automat oameni pe Facebook
- Trimitere automată de cereri de prietenie
- Scraping de orice fel
- Automatizare agresivă/spam pe Messenger sau alt canal
- Content Engine complet (generare automată de conținut)
- Orice componentă care înlocuiește judecata liderului în interacțiunea
  cu o persoană reală

Metodologia SOURCE rămâne execuție umană. Ce se decide aici e doar
dacă și cum sistemul o poate sprijini — nu dacă o poate înlocui.

---

## §6 — Relationship to MVP-ENGINE-001

SOURCE **nu modifică** scope-ul MVP-ENGINE-001 și nu introduce niciun
motor nou în MVP (v. `06-harta-motoare-tehnice.md` pentru lista
curentă a celor 6 motoare confirmate — neenumerate aici, ca să nu
riscăm o listă neactualizată sau neverificată în acest document). Nu
se declară aici "Motorul 0", nici vreo poziție tehnică definitivă —
poziționarea (motor separat, modul, capability layer) se stabilește
**după** audit arhitectural, nu prin presupunere în acest document.

---

## §7 — Scope Decision

**SOURCE intră în roadmap-ul strategic al NicMar OS ca necesitate de
business pentru recrutare, dar nu modifică în acest moment
MVP-ENGINE-001 și nu este declarat încă "Motorul 0".**

---

## §8 — Prioritization Criterion

Pentru orice decizie tehnică viitoare legată de SOURCE:

> **Cum contribuie concret la creșterea fluxului de persoane noi care
> pot deveni prospecți și parteneri?**

Dacă o propunere nu poate răspunde clar la această întrebare, nu se
prioritizează.

---

## §9 — Next Decision

Ordinea de continuare, în această secvență, fără pași săriți:

1. SOURCE 1.0 metodologie ✅ (`source-1.0-metodologie.md`)
2. Experiment 01 / Market Listening ✅ (`Saptamana_1.md`)
3. **07A — Scope Decision** ✅ (acest document)
4. Audit arhitectural — ce există deja în repo care atinge categoriile
   din §4
5. Identificarea primei competențe tehnice SOURCE (una singură, nu
   toate categoriile din §4 deodată)
6. Contract tehnic pentru acea competență
7. RED → GREEN

Următorul document de scris este auditul de la pasul 4 — nu un
contract, nu cod.
