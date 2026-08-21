# Audit 07B — SOURCE vs. Repo Existent

Status: DRAFT — audit factual, de verificat de owner
Data: 22 august 2026
Sursă: verificare directă în `src/`, `migrations/`, `docs/architecture/`
Răspunde la întrebarea din Decizia 07A §9, pasul 4: **din tot ce
SOURCE trebuie să facă în business, ce există deja în NicMar OS și ce
este cu adevărat absent?**

**Nu alege prima competență tehnică.** Doar constată ce există. Alegerea
rămâne pas separat (07A §9, pasul 5).

---

## Metodă

Fiecare din cele 5 categorii din `07A-source-scope-decizie.md` §4 a
fost verificată direct în cod (`src/engines/`, `migrations/`), nu
presupusă din documentație.

---

## 1. 🔴 Captarea unei persoane găsite prin SOURCE, înainte de Contact

**Nu există.** Confirmat direct în `outreach_engine.py`: outcome-ul
`REFERRAL_RECEIVED` — momentul în care apare o persoană complet nouă
(o recomandare primită) — **explicit nu creează `Contact`**. Sursa
proprie a codului spune: *"Nu creează Contact nou pentru
REFERRAL_RECEIVED — pas explicit separat, prin POST /api/v1/contacts
deja existent."*

Deci: mecanismul de a *înregistra faptul* că a apărut o persoană nouă
există parțial (outcome-ul se salvează), dar pasul de a o transforma
efectiv în `Contact` e manual, prin endpoint-ul general de creare
contact — nimic specific fluxului SOURCE.

## 2. 🔴 Fluxul de prospectare directă (Facebook: găsire → cerere → acceptare necunoscută → prima interacțiune)

**Nu există deloc în cod.** Etapa 2 din `source-1.0-metodologie.md`
(găsirea audienței pe Facebook, cererile de prietenie, rata de
acceptare, semnalul de interacțiune) e descrisă integral ca practică
manuală a liderului. Zero cod, zero schemă DB, zero test o atinge.
Rămâne, azi, 100% execuție umană — nici nu ar trebui automatizată (v.
07A §5).

## 3. 🟡 Market Listening ca sursă de date recurentă

**Există un singur experiment scris manual** —
`docs/market-listening/Saptamana_1.md` — dar **nu ca sursă de date în
sistem**: e un document Markdown, nu o tabelă, nu un API, nu ceva ce
un motor poate citi sau scrie. Sursa proprie a metodologiei
(`source-1.0-metodologie.md`, §9) recunoaște explicit acest gol:
*"sursa temelor e Market Listening, el însuși marcat cu dependență
nerezolvată."* Nu există infrastructură — doar o primă instanță
manuală a conținutului pe care ar trebui, într-un viitor, să-l producă.

## 4. 🔴 Fluxul audiență/conținut (ce se publică, ce reacție se urmărește, cum ajunge înapoi în Market Listening)

**Nu există.** Nimic în `src/` produce, programează sau urmărește
conținut (Reels, postări, stories). Bucla de validare din Experiment
01 (Semnal → Conținut testat → Răspuns → Verdict) e azi complet
manuală, ținută într-un tabel Markdown completat de mână.

## 5. 🟡 Reactivarea persoanelor vechi (Black Box)

**Parțial construit — mecanismul de trimitere există, criteriul de
intrare nu.** `OutreachEngine` (Decizia 46, migrarea
`005_outreach_relational.sql`) are un `purpose = REACTIVATION` complet
funcțional: liderul poate trimite o reactivare către un `Contact`
existent, înregistra rezultatul (`QUESTION_ASKED`, `HESITATION`,
`WILL_RESPOND_LATER`, `POSITIVE_RESPONSE`), cu handoff automat spre
`Conversation` pentru primele trei. Confirmat cu teste reale (494/494
PASSED, conform `46A-workbench-prospectare-contract.md`).

**Dar** — chiar sursa de business (`source-1.0-metodologie.md`, §9,
"Ce rămâne nedefinit") spune explicit: *"Cine decide intrarea în Black
Box — partenerul manual, sau sistemul propune? Nedecis."* Deci
sistemul poate **executa** o reactivare pe un contact deja ales de
lider, dar nu există niciun concept de "listă Black Box" sau criteriu
automat de "cine intră acolo" — asta rămâne, azi, integral decizia
liderului, fără sprijin din sistem.

---

## Sinteză

| Categorie (07A §4) | Stare reală în repo |
|---|---|
| 1. Captare persoană nouă → Contact | 🔴 Nimic specific — doar endpoint-ul general de Contact, manual |
| 2. Prospectare directă (Facebook) | 🔴 Zero cod — 100% practică umană, corect așa |
| 3. Market Listening ca sursă de date | 🟡 Un document manual; zero infrastructură |
| 4. Flux audiență/conținut | 🔴 Zero cod |
| 5. Reactivare (Black Box) | 🟡 Mecanismul de trimitere există și e testat (`OutreachEngine`/REACTIVATION); criteriul de intrare în Black Box e nedecis chiar la nivel de business |

**Observație generală:** cea mai avansată piesă deja construită legată
de SOURCE e `OutreachEngine` (Decizia 46) — dar acoperă doar
**execuția** unei reactivări/recomandări pe o persoană deja aleasă de
lider, nu **generarea** fluxului de persoane noi, care rămâne scopul
central al SOURCE (07A §0). Cele patru categorii cu adevărat goale
(1, 2, 3, 4) sunt exact cele care privesc *crearea* fluxului, nu
gestionarea lui după ce există.

---

## Ce nu decide acest document

Nu alege care dintre categoriile 🔴/🟡 devine prima competență tehnică
— asta rămâne pasul 5 din 07A §9, decizie separată a owner-ului,
folosind criteriul din 07A §8 (*"cum contribuie concret la creșterea
fluxului de persoane noi care pot deveni prospecți și parteneri?"*).
