# Decizia 46 — Prospectare Relațională (Recomandare + Reactivare)

Status: BUSINESS TRUTH ÎNGHEȚAT, SCHEMĂ TEHNICĂ NEDECISĂ (owner, 20
august 2026). Bazat pe `scope-prospectare-recrutare.md` (scope
aprobat conceptual) și audit tehnic direct din repo. **Acest document
nu conține și nu autorizează schema DB, endpoint-uri finale sau cod.**
Schema se derivă într-un pas separat, ulterior, doar din adevărul
înghețat aici.

## 1. Confirmare scope

`Scope aprobat conceptual`: primul val Prospectare & Recrutare =
Recomandare (09) + Reactivare (10), tratate ca **un singur mecanism**
— `Prospectare Relațională` — cu două moduri: `REFERRAL` și
`REACTIVATION`.

## 2. Cele 8 adevăruri de business înghețate

1. **Nu există `PUT`/`PATCH` pentru modificarea retrospectivă a
   unui outreach.** Intervenția, odată trimisă, e imutabilă.
2. **Rezultatul nu se deduce din existența unei entități ulterioare**
   (`Conversation`/`FollowUp`/`Objection`). Absența unei entități
   ulterioare nu înseamnă nimic determinat — poate însemna oricare
   din mai multe situații diferite, nedistinse una de alta.
3. **Rezultatul observat se înregistrează explicit**, ca fapt separat
   de intervenția inițială, nu ca actualizare a ei. `Outcome` e
   **entitate business proprie** (tabelă), nu doar înregistrare de
   audit în `events` — motivat de nevoia de interogare directă
   ("care a fost ultimul rezultat", "câte HESITATION am avut"), nu
   doar de trasabilitate istorică.
4. **`NO_RESPONSE` nu este un outcome.** E absența unui outcome până
   la un moment dat — o stare implicită, nu o valoare înregistrată.
5. **Cardinalitate: `Outreach (1) → Outcome (0..1)`**, nu `(0..N)`.
   Un `Outreach` are cel mult un `Outcome` imediat. Derivat din
   formularea sursei ("**deschide** 04/06/01" — verb de rutare, nu de
   actualizare repetată).
6. **`Outcome`-ul declanșează cel mult o predare (*handoff*)** către
   entitatea de continuare potrivită (`Conversation`/`Objection`/
   `FollowUp`). Orice evoluție ulterioară aparține entității de
   continuare create, deja cu propriul ei ciclu de viață construit
   (ex. tranzițiile `FollowUp` deja existente) — **nu** se mai scrie
   înapoi pe `Outreach` sau pe `Outcome`-ul original, niciunul din
   cele două nu se modifică după predare.
7. **`REFERRAL_RECEIVED` ≠ prospect nou.** E doar faptul că persoana
   contactată a oferit o recomandare. Persoana recomandată devine
   `Contact` doar printr-un pas ulterior explicit, separat.
8. **Nu se inventează alte rezultate** în afara celor găsite explicit
   în sursă (`05-competente-37-motor1.md`, Pasul 7 al Conversațiilor
   09 și 10).

## 3. Cele trei concepte, strict separate

### 3.1. `Outreach` — ce a făcut liderul

Faptul intervenției în sine: cine a fost contactat, cu ce scop
(`REFERRAL`/`REACTIVATION`), ce mesaj a fost trimis, cu ce ton, când.
Imutabil de la creare.

### 3.2. `Outcome` — ce a observat liderul ca răspuns imediat

Înregistrare separată, distinctă de `Outreach`. Valorile, **derivate
direct din sursă**, nu inventate:

| Outcome | Sursă | Aplicabil la |
|---|---|---|
| `QUESTION_ASKED` | Pasul 7, ambele conversații | `REFERRAL` + `REACTIVATION` |
| `HESITATION` | Pasul 7, ambele conversații | `REFERRAL` + `REACTIVATION` |
| `WILL_RESPOND_LATER` | Pasul 7, ambele conversații | `REFERRAL` + `REACTIVATION` |
| `REFERRAL_RECEIVED` | Pasul 7, Conversația 09 | doar `REFERRAL` |
| `POSITIVE_RESPONSE` | Pasul 7, Conversația 10 | doar `REACTIVATION` |

Absența unui `Outcome` înregistrat = stare implicită "fără rezultat
încă", niciodată o valoare scrisă explicit.

**Cardinalitate finală, înghețată**: `Outreach (1) → Outcome (0..1)`,
nu `(0..N)`. Motivare, derivată din formularea sursei ("**deschide**
04", "**deschide** 06" — verb de rutare, nu de actualizare repetată):

- `0` = mesajul a fost trimis, dar liderul încă n-a înregistrat
  reacția imediată — **nu** înseamnă `NO_RESPONSE`, rămâne aceeași
  distincție deja înghețată la Punctul 4
- `1` = reacția imediată a fost înregistrată o singură dată

**Regulă centrală, înghețată**: un `Outreach` are cel mult un
`Outcome` imediat. `Outcome`-ul declanșează cel mult o predare
(*handoff*) către entitatea de continuare potrivită. **Orice evoluție
ulterioară aparține entității de continuare create (`FollowUp`,
`Conversation`, `Objection`), nu se mai scrie înapoi pe `Outreach`
sau pe `Outcome`-ul original.** Nici `Outreach`-ul, nici `Outcome`-ul
nu se modifică după predare.

### 3.3. `Continuare` — ce se întâmplă mai departe, în sistemul deja construit

Fiecare `Outcome` declanșează exact o predare, o singură dată, spre
infrastructura deja existentă — care preia de acolo propriul ei ciclu
de viață, deja construit:

```
QUESTION_ASKED       → Conversation (flux 01, existent)
HESITATION            → Objection (flux 04, existent, prin Conversation)
WILL_RESPOND_LATER     → FollowUp (flux 06, existent) — orice răspuns
                          ulterior al persoanei se urmărește prin
                          tranzițiile deja construite ale FollowUp-ului
                          (PENDING→COMPLETED/POSTPONED/RESCHEDULED),
                          nu printr-un al doilea Outcome
REFERRAL_RECEIVED       → Conversation cu persoana recomandată (flux 03)
POSITIVE_RESPONSE       → flux Invitație (07, neconstruit — gol separat, nu tratat aici)
```

Continuarea *creează* o entitate existentă (Conversation/FollowUp);
nu modifică `Outreach`-ul sau `Outcome`-ul. Responsabilitatea fiecărei
entități rămâne strict separată:

```
Outreach    = "am făcut această intervenție"
Outcome     = "aceasta a fost reacția imediată observată"
FollowUp    = "persoana a spus că revine / trebuie reluată"
Conversation = "a început conversația"
Objection   = "a apărut o ezitare"
Contact     = "avem o persoană în sistem"
Events      = istoricul tehnic al tuturor tranzițiilor
```

### 3.4. Prospect nou (cazul `REFERRAL_RECEIVED`)

Separat explicit, conform punctului 6: `REFERRAL_RECEIVED` înregistrează
doar faptul recomandării. Transformarea persoanei recomandate într-un
`Contact` real e un **pas explicit separat, ulterior**, nu automat —
folosind mecanismul deja existent (`POST /api/v1/contacts`), nu un
proces paralel nou. Rămâne de decis, la pasul de schemă, dacă acel
`Contact` nou păstrează vreo legătură vizibilă cu `Outreach`-ul care
l-a generat (ex. un câmp opțional de proveniență) — **nedecis aici**,
doar semnalat ca întrebare deschisă pentru pasul următor.

## 4. Ce rămâne explicit nedecis (deliberat, pentru pasul următor)

- Schema DB exactă (tabele, coloane, tipuri)
- Endpoint-urile API exacte
- Dacă `Contact`-ul rezultat dintr-un `REFERRAL_RECEIVED` păstrează o
  legătură vizibilă cu `Outreach`-ul de origine
- Formatul exact al legăturii `Outcome → Continuare` (ex. dacă
  `Conversation`/`FollowUp` primesc un câmp opțional de referință, sau
  legătura rămâne doar implicită prin timp/context)

Niciunul din aceste puncte nu se decide implicit prin acest document.

## 5. Explicit exclus (neschimbat față de versiunea anterioară)

- `Mission`, `Priority` — neatinse
- Niciun KPI nou
- "Biblioteca Experienței" (Pasul 8) — omis din v1
- Integrări Facebook/WhatsApp/TikTok — zero
- Fluxul `POSITIVE_RESPONSE → Invitație` (07) — outcome-ul se
  înregistrează, dar continuarea tehnică rămâne un gol separat,
  netratat în acest val

## 6. Ordinea de lucru

```
acest document — business truth înghețat (1-3), schema explicit deferată
        ↓
pas separat — derivarea schemei DB din secțiunea 3, cu confirmare proprie
        ↓
contract tehnic final
        ↓
RED
        ↓
GREEN
        ↓
PostgreSQL real
        ↓
regresie (468 + N)
        ↓
CI
        ↓
verificare independentă
```

**RED nu începe la acest document.** Următorul pas e derivarea
schemei, ca document/decizie separată, cu propria confirmare explicită.
