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
- `outcome`: `ACCEPTED`, `QUESTION_ASKED`, `HESITATION`,
  `POSTPONED`, `DECLINED`
- Toate 5 derivate din Pasul 8 al sursei; `DECLINED` **adăugat** —
  sursa nu-l enumeră explicit, dar metodologia reală îl cere
  (cascada afacere→produs→recomandare→black box presupune un "nu")

**Legătura cu `meetings`**: doar pentru `ACCEPTED`. Coloană nouă,
aditivă: `meetings.source_invitation_id` (tipar identic
`conversations.source_outreach_id` de la Decizia 46).

## 6. Puncte deschise — necesită decizia owner-ului

**A. `meetings.status` nu are `CHECK` constraint** — singura coloană
de stare din toată schema fără valori restricționate. Ce valori sunt
permise? (`SCHEDULED` e default; mai există `HELD`, `CANCELLED`,
`NO_SHOW`?) Sau rămâne liber în v1?

**B. Crearea `Meeting` la `ACCEPTED` — automată sau manuală?**
Problema: la momentul înregistrării outcome-ului, liderul poate să nu
știe încă data exactă. `meetings.scheduled_at` e `NOT NULL`. Deci:
(a) sistemul cere data odată cu outcome-ul, (b) `Meeting` se creează
separat, ulterior, (c) `ACCEPTED` doar semnalează, fără `Meeting`
automat.

**C. Generarea celor 3 variante de mesaj** — aceeași situație ca la
46A: backend-ul nu generează text. Liderul scrie, alege doar tonul?
(recomandat, consecvent cu 46A) sau altceva?

**D. `DECLINED` → ce urmează?** Metodologia cere cascada
(produs → recomandare → black box), dar niciuna nu are reprezentare în
cod azi. În v1, `DECLINED` doar se înregistrează, fără continuare
automată?

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

## 9. Ordinea de lucru

```
acest contract + răspuns la punctele §6
        ↓
schema (migrare 007)
        ↓
RED
        ↓
GREEN
        ↓
regresie completă (512 + N)
        ↓
CI + verificare independentă
```

Nu se scrie cod înainte de clarificarea celor 4 puncte deschise.
