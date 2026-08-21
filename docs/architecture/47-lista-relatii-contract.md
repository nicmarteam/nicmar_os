# Decizia 47 — Construirea Listei de Relații (Competența 18)

Status: PROPUNERE DE CONTRACT (owner, 20 august 2026). Sursă:
`05-competente-37-motor1.md`, Competența 18, **✅ VALIDATĂ (10/10)** —
nu se reinventează business, se traduce în cod o competență deja
aprobată.

## 1. Problema rezolvată

Verbatim din sursă: *"Utilizatorul trece de la «nu știu cu cine să
vorbesc» la «am o listă clară și organizată de relații»."*

Corespunde direct blocajului confirmat din teren ("nu am prospecti
noi") și e prima piesă din lanțul de recrutare — fără listă, nimic
altceva nu are input.

## 2. Decizie de arhitectură — extindem `Contact`, NU creăm `Relationship`

**Regulă explicită, înghețată:**

> **Nu se creează entitatea `Relationship`.** O persoană = un
> `Contact`, un singur traseu pe tot parcursul transformării ei:
> persoană cunoscută → contact → prospect → conversație → nevoie →
> client/partener → lider.

Motiv: `Contact` **este deja** ce descrie Competența 18 ca
"Relationship" — o persoană cunoscută de lider, cu status și istoric.
Specificația a fost scrisă înainte să existe `ContactEngine`. Două
entități concurente pentru aceeași persoană ar rupe traseul ("am
cunoscut-o în lista de relații, dar unde a ajuns — în Contacts? în
FollowUp? în Partner?").

**Consecință imediată, verificată**: persoanele adăugate prin acest
flux apar automat în 46A (Prospectare Relațională), în `PriorityEngine`,
în `FollowUpEngine` — tot ce e deja construit, fără nicio integrare
suplimentară.

## 3. Triere câmpuri — ce intră acum, ce rămâne afară

Filtru aplicat: **intră doar ce e ales/scris explicit de lider și
verificabil**; rămâne afară tot ce presupune un motor de calcul
inexistent.

**IN (5 câmpuri, toate din alegeri explicite ale liderului):**

| Câmp | Sursă în spec | Tip |
|---|---|---|
| `relationship_category` | Ecranul 2 | enum: `FAMILIE`, `PRIETENI`, `COLEGI`, `VECINI`, `FOSTI_COLEGI`, `CUNOSTINTE`, `ALTA` |
| `relationship_level` | Ecranul 4 | enum: `FOARTE_APROPIATA`, `BUNA`, `OCAZIONALA`, `DE_RELUAT` |
| `last_contact_approx` | Ecranul 5 | enum: `ASTAZI`, `SAPTAMANA_ACEASTA`, `LUNA_ACEASTA`, `MAI_DEMULT`, `NU_IMI_AMINTESC` — **aproximare, nu timestamp**, exact cum cere sursa |
| `significant_context` | Ecranul 5.1 | text liber, opțional |
| `perceived_interest` | Ecranul 6 | enum: `FOARTE_DESCHISA`, `PROBABIL`, `NU_STIU_INCA` |

**OUT — excluse explicit, cu motiv:**

| Element | Motiv excludere |
|---|---|
| `scorRelație`, `scorInteres`, `prioritate follow-up` | Sursa spune că sunt calculate de "Motorul Relației" — **motor inexistent în cod**. A le adăuga cu valoare placeholder ar repeta exact eroarea refuzată la ORE (Decizia 44). Dacă vor fi nevoie, trec prin propriul proces de definire |
| "Motorul de Învățare" (calibrare după 10 persoane, Pasul 9) | Inferență inexistentă, `src/llm/` deconectat |
| Validare progres după 5 persoane (Pasul 4) | Comportament de UI, aparține unei decizii de Workbench (47A), nu schemei |

## 4. Modificări propuse

**Schema** (migrare `006`), toate coloanele **nullable** — contactele
existente rămân valide, zero breaking change:

```
ALTER TABLE contacts ADD COLUMN relationship_category TEXT CHECK (...)
ALTER TABLE contacts ADD COLUMN relationship_level TEXT CHECK (...)
ALTER TABLE contacts ADD COLUMN last_contact_approx TEXT CHECK (...)
ALTER TABLE contacts ADD COLUMN significant_context TEXT
ALTER TABLE contacts ADD COLUMN perceived_interest TEXT CHECK (...)
```

**`ContactEngine.create_contact()`** — extindere aditivă, toți
parametrii noi opționali, semnătura existentă rămâne funcțională
(tipar identic cu extinderea `get_or_create_conversation` de la
Decizia 46).

**`CreateContactRequest`** + **`ContactResponse`** — cele 5 câmpuri,
opționale.

**Evenimentul `ContactCreated`** — neschimbat, deja emis (Decizia 42).

## 5. Explicit exclus

- Entitatea `Relationship` — nu se creează, regulă înghețată (§2)
- Orice scor calculat automat
- Workbench — fluxul de ecrane (7 ecrane din spec) rămâne **Decizia
  47A**, separată, după ce backend-ul e verde
- `ContactAgent`, `PriorityEngine`, `FollowUpEngine`, 46A — neatinse
  (beneficiază automat de câmpurile noi, fără modificare)
- Competența 19 (Inițierea Conversațiilor) — nu se atinge până când 47
  nu e complet

## 6. Criterii de acceptare (RED)

**Unitare** (`tests/test_contact_engine.py`):
1. `test_create_contact_accepta_campurile_de_relatie` — toate 5 transmise, ajung în `INSERT`
2. `test_create_contact_fara_campuri_de_relatie_ramane_valid` — regresie: semnătura veche funcționează, câmpurile devin `None`
3. `test_create_contact_categorie_invalida_ridica_eroare` — validare la nivel de aplicație, înainte de DB (tipar `InvalidDiagnosticTypeError`)

**PostgreSQL real** (`tests/test_real_postgres.py`,
`TestContactEngineOnRealPostgres` — clasă deja existentă, Decizia 42):
4. `test_campurile_de_relatie_persistate_real` — verificate direct în DB
5. `test_contact_fara_campuri_de_relatie_are_null` — coloanele noi acceptă `NULL`

**HTTP** (`tests/test_contacts_api.py`):
6. `test_post_contact_cu_campuri_de_relatie_returneaza_201`
7. `test_post_contact_categorie_invalida_returneaza_400`
8. `test_get_contacts_expune_campurile_de_relatie`

## 7. Ordinea de lucru

```
contract (acest document) + confirmare
        ↓
RED (8 teste)
        ↓
GREEN
        ↓
regresie completă (504 + 8)
        ↓
CI
        ↓
verificare independentă
        ↓
47A — Workbench (fluxul de 7 ecrane), decizie separată
```
