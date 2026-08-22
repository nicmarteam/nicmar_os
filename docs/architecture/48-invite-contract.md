# Decizia 48 — INVITE (Invitația)

Status: PROPUNERE DE CONTRACT (owner, 22 august 2026).
Surse: `05-competente-37-motor1.md`, Conversația 07
(`07_Invitatie_La_Cafea_Sau_Zoom`) + metodologia reală
(`source-1.0-metodologie.md`, §3).

**Nu autorizează implementare.** Business truth + design, cu punctele
deschise marcate explicit.

## 1. De ce INVITE, și de ce acum

Auditul lanțului de recrutare a arătat un **gol structural la mijloc**:

```
AM OAMENI          🟢 (Decizia 47)
AM CONVERSAȚII     🟢 (Deciziile 46/46A)
AM INTERES         🟡 parțial
AM INVITAȚII       🔴  ← GOL CRITIC
AM PREZENTĂRI      🔴
AM DECIZII         🟡
AM PARTENERI       🟢
```

Consecința concretă: orice sistem de orchestrare (Next Best Action)
construit înainte de INVITE **nu ar putea observa niciodată** trecerea
de la conversație la invitație — ar rămâne blocat la *"începe
conversații"*, indiferent câte ar face liderul.

**INVITE nu e "următoarea funcție CRM". E veriga care închide lanțul.**

## 2. Distincția centrală — invitație ≠ întâlnire

`meetings` există deja în schemă (`contact_id`, `partner_id`, `title`,
`scheduled_at`, `status`), niciodată folosită. E infrastructură bună
**pentru întâlnire**, dar o invitație și o întâlnire nu sunt același
lucru:

```
INVITAȚIE (fapt: am invitat)
   │
   ├── ACCEPTED    → MEETING programat
   ├── QUESTION    → Conversation (există)
   ├── HESITATION  → Objection (există)
   ├── POSTPONED   → FollowUp (există)
   └── DECLINED    → FollowUp / închidere
```

O invitație poate exista fără să producă vreodată o întâlnire. O
întâlnire e doar **una din cele 5 continuări posibile**.

## 3. Ce spune sursa — Conversația 07, 9 pași

| Pas | Ce face liderul | Opțiuni exacte din sursă |
|---|---|---|
| 1 | Primire | *"Invitația este mereu despre o conversație, iar evenimentul este doar cadrul"* |
| 2 | Alege persoana | Scriu numele / Aleg din lista mea / Încă mă gândesc |
| 3 | **Alege cadrul** | ☕ Cafea · 💻 Zoom · 📞 Apel · 🎥 Live · ✨ Altceva |
| 4 | **Motivul invitației** | O idee nouă · O oportunitate · O experiență · O conversație plăcută · Altceva |
| 5 | Construiește mesajul | 3 variante: Caldă / Relaxată / Directă |
| 6 | Verifică | *"Citește cu voce tare. Îți seamănă?"* |
| 7 | Trimite | Buton: **"Am trimis invitația"** — auto-declarat |
| 8 | **Revine cu răspunsul** | Da → Prezentare · Cere detalii → Conversation · Ezită → Objection · Mai târziu → FollowUp |
| 9 | Biblioteca Experienței | ⚠️ omis din v1 — `ExperienceLibraryEngine` nu există |

## 4. Structura propusă — reutilizare maximă

Tiparul e **aproape identic cu Decizia 46** (Outreach → Outcome →
Continuare), deja construit și validat:

| Concept | Decizia 46 (Outreach) | Decizia 48 (Invite) |
|---|---|---|
| Faptul | `outreach_attempts` | `invitations` |
| Reacția | `outreach_outcomes` (0..1, UNIQUE) | `invitation_outcomes` (0..1, UNIQUE) |
| Continuarea | Conversation / FollowUp / Objection | idem **+ Meeting** |
| Imutabilitate | fără PUT/PATCH | idem |
| Auto-declarat | "Am trimis mesajul" | "Am trimis invitația" |

**Nu se inventează un tipar nou** — se aplică unul deja validat prin
494 de teste.

## 5. Ce trebuie persistat

**`invitations`** (faptul invitației, imutabil):
- `owner_id`, `contact_id` (ținta — mereu un `Contact`, ca la 46)
- `frame` — cadrul propus: `CAFEA`, `ZOOM`, `APEL`, `LIVE`, `ALTCEVA`
- `purpose` — motivul: `IDEE_NOUA`, `OPORTUNITATE`, `EXPERIENTA`,
  `CONVERSATIE_PLACUTA`, `ALTCEVA`
- `message_text`, `tone_used` (`CALDA`/`RELAXATA`/`DIRECTA` — același
  set ca la 46)
- `sent_at`

**`invitation_outcomes`** (reacția, 0..1 per invitație, `UNIQUE`):
- `outcome`: `ACCEPTED`, `POSTPONED`, `QUESTION_ASKED`,
  `OBJECTION`, `DECLINED`
- Primele 4 derivate din Pasul 8 al sursei; `DECLINED` **adăugat
  explicit** — sursa nu-l enumeră, dar metodologia reală îl cere
  (un "nu" trebuie să poată fi înregistrat)

**Legătura cu `meetings`**: doar pentru `ACCEPTED`. Coloană nouă,
aditivă: `meetings.source_invitation_id` (tipar identic
`conversations.source_outreach_id` de la Decizia 46).

## 6. Cele 4 decizii — ÎNGHEȚATE

### Principiul central, înghețat

> **INVITE este evenimentul de business. MEETING este consecința
> programată a unei invitații acceptate.**

Separația permite, mai târziu (Recruitment State), numărarea distinctă:
câte invitații s-au făcut · câte au fost acceptate · câte au devenit
întâlniri · câte întâlniri s-au finalizat · câte au produs o decizie.

### A. `meetings.status` — valori standardizate

```
SCHEDULED · COMPLETED · CANCELLED · RESCHEDULED
```

**Regulă strictă**: `meetings.status` **nu reprezintă răspunsul la
invitație**. Sunt două lucruri diferite, pe două niveluri:

```
INVITE outcome  →  ACCEPTED / POSTPONED / QUESTION / OBJECTION / DECLINED
                          ↓ (doar ACCEPTED, și doar cu dată stabilită)
MEETING status  →  SCHEDULED / COMPLETED / CANCELLED / RESCHEDULED
```

Necesită `CHECK` constraint adăugat pe `meetings.status` (azi lipsește
— singura coloană de stare din schemă fără restricție).

### B. `ACCEPTED` → Meeting: NU automat

`ACCEPTED` înregistrează **acceptarea invitației**, atât. `Meeting` se
creează **doar când există efectiv o dată/oră programată**:

```
ACCEPTED  →  "Da, vreau"  →  se stabilește ziua/ora  →  MEETING (SCHEDULED)
```

Rezolvă elegant problema `scheduled_at NOT NULL` și e mai aproape de
realitate: omul poate spune *"da, sigur, hai să vorbim"*, iar
programarea efectivă vine ulterior.

### C. Mesajul — liderul scrie, sistemul dă structura

Model identic cu 46A. **INVITE v1 nu e generator AI de texte.**

Workbench-ul oferă: persoana · context · motivul invitației · tipul
întâlnirii (cafea / Zoom / apel / live) · câmp liber pentru mesaj.

Cele 3 tonuri (`CALDA`/`RELAXATA`/`DIRECTA`) rămân **opțiuni de
ghidare și etichetare**, nu texte generate automat.

### D. `DECLINED` — doar se înregistrează în v1

Fără declanșare automată de: produs · recomandare · Black Box · altă
cascadă.

Motiv: metodologia spune că relația continuă **în funcție de context**;
automatizarea acestor ramificații ar introduce comportament
necontractat.

```
DECLINED  →  înregistrat  →  contactul rămâne în sistem
```

Ulterior, FollowUp / Recomandare / Reactivare (Decizia 46, deja
construită) pot decide ce urmează — manual, la alegerea liderului.

### Fluxul complet, înghețat

```
OUTREACH / CONVERSATION
          ↓
       INVITE
          ↓
 ┌────────┼──────────┬───────────┬──────────┐
 ↓        ↓          ↓           ↓          ↓
ACCEPTED POSTPONED QUESTION   OBJECTION  DECLINED
 ↓        ↓          ↓           ↓          ↓
Meeting  Follow-up Conversation Objection  înregistrare
(după                                       (fără
programare)                                 continuare automată)
```

## 7. Explicit exclus din v1

- Biblioteca Experienței (Pasul 9) — motor inexistent
- `PresentationEngine` (Pasul 8, ramura "Da") — exclus din MVP;
  `ACCEPTED` duce la `Meeting`, nu la prezentare structurată
- Generare automată de text (LLM) — `src/llm/` deconectat
- Cascada completă produs/recomandare/black box — decizie separată
- Workbench — decizie 48A, ulterioară

## 8. Criteriul de succes

> Un lider care are o conversație cu un prospect poate face o
> invitație reală, iar sistemul poate observa ce s-a întâmplat cu
> acea invitație și poate transmite persoana către următoarea verigă.

Concret: după 48, starea **AM INVITAȚII** devine 🟢 observabilă, iar
lanțul de recrutare nu mai are gol la mijloc.

## 9. Status și ordinea de lucru

**Toate cele 4 puncte deschise sunt înghețate (§6). Contractul e
complet — RED poate începe.**

```
contract 48 ✅ COMPLET
        ↓
schema (migrare 007: invitations, invitation_outcomes,
        meetings.status CHECK, meetings.source_invitation_id)
        ↓
RED
        ↓
GREEN
        ↓
regresie completă (512 + N)
        ↓
CI + verificare independentă
        ↓
48A — Workbench INVITE (decizie separată)
```
