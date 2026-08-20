# Decizia 46 — Prospectare Relațională (Recomandare + Reactivare)

Status: PROPUNERE DE CONTRACT (owner, 20 august 2026). Bazat pe
`scope-prospectare-recrutare.md` (scope aprobat conceptual) și audit
tehnic direct din repo. **Schema DB nu e decisă încă** — secțiunea 3
(adevărul de business) precede secțiunea 4 (schema derivată), în
această ordine, nu invers.

## 1. Confirmare scope

`Scope aprobat conceptual`: primul val Prospectare & Recrutare =
Recomandare (09) + Reactivare (10), tratate ca **un singur mecanism**
— `Prospectare Relațională` — cu două moduri, nu două proiecte
separate: `REFERRAL` și `REACTIVATION`.

> Obiectivul nu este „să avem două conversații noi". Obiectivul este
> să oferim liderului două mecanisme simple și repetabile prin care
> să creeze conversații noi din relațiile pe care le are deja.

## 2. Principiul de unificare

Un singur motor (`RelationalOutreachEngine`, nume provizoriu), un
singur endpoint de creare, o singură schemă de răspuns — parametrizate
prin `purpose: REFERRAL | REACTIVATION`. Diferența dintre 09 și 10,
verificată din specificațiile complete, e doar de conținut (întrebări
de context ușor diferite, ton generat diferit), nu de mecanică.
Reduce cod duplicat, contracte duplicate, teste duplicate, UI duplicat
— exact cerința explicită.

## 3. Adevărul de business ce trebuie persistat

Înainte de orice câmp de schemă, răspuns explicit la fiecare întrebare
pusă:

| Întrebare | Răspuns |
|---|---|
| **Cine e ținta?** | Întotdeauna un `Contact` — dacă liderul scrie un nume nou (nu din listă), sistemul creează întâi un `Contact` (reutilizează `ContactEngine.create_contact()` existent), apoi continuă. Nu se inventează un concept paralel de "persoană țintă" — ținta e mereu `contact_id` |
| **Ce tip de acțiune?** | `purpose`: `REFERRAL` sau `REACTIVATION` — enum, obligatoriu |
| **Ce mesaj a fost ales?** | Textul final al mesajului (după eventuale editări ale liderului) + tonul ales (`CALDA`/`RELAXATA`/`DIRECTA` — **set distinct** de variantele Objection, `CALDA`/`DIRECTA`/`INTREBARE`; nu se confundă cele două seturi) |
| **Când a fost trimis?** | Timestamp, confirmat explicit de lider prin butonul "Am trimis mesajul" — **auto-raportat, nu verificat de sistem** (aceeași natură declarativă ca `FollowUp.COMPLETED`, semnalată onest, nu ascunsă) |
| **Ce rezultat a avut?** | **Nu se persistă ca un câmp separat, actualizabil.** Propunere: rezultatul se deduce din faptul că un `Conversation`/`FollowUp`/`Objection` ulterior *referențiază* această intervenție (`source_outreach_id`, opțional, pe endpoint-urile deja existente). Motiv: sistemul nu are, azi, niciun `PUT`/`PATCH` — introducerea unui câmp mutabil doar pentru asta ar fi prima excepție de la acest tipar, nefundamentată. Legarea prin referință la crearea următoarei entități e consecventă cu restul arhitecturii |
| **Care e următorul pas?** | Identic cu răspunsul de mai sus — nu e un câmp separat, e efectul observat (ce s-a creat după) |

**Punct explicit de confirmat cu dvs.**: propunerea de a NU introduce
mutabilitate (fără `PUT`/`PATCH` nou) și de a deduce rezultatul prin
referință e o decizie de design, nu un fapt din audit — vă rog
confirmare explicită înainte de a îngheța, exact disciplina aplicată
la fiecare pas de azi.

## 4. Schema derivată (propunere, nu decizie)

Doar după secțiunea 3 — un singur tabel nou:

```sql
CREATE TABLE outreach_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    purpose TEXT NOT NULL CHECK (purpose IN ('REFERRAL', 'REACTIVATION')),
    message_text TEXT NOT NULL,
    tone_used TEXT NOT NULL CHECK (tone_used IN ('CALDA', 'RELAXATA', 'DIRECTA')),
    sent_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);
```

Plus **un singur câmp adăugat**, opțional, la 2 endpoint-uri deja
existente (nu se creează endpoint-uri noi pentru ele):

```python
# CreateConversationRequest (extindere aditivă)
class CreateConversationRequest(BaseModel):
    contact_id: UUID
    source_outreach_id: Optional[UUID] = None   # NOU

# CreateFollowUpRequest (extindere aditivă)
class CreateFollowUpRequest(BaseModel):
    contact_id: UUID
    conversation_id: UUID
    notes: Optional[str] = None
    scheduled_at: Optional[str] = None
    source_outreach_id: Optional[UUID] = None   # NOU
```

Zero migrare pe `objections` — legătura cu fluxul de obiecție se
poate deduce indirect prin `conversation_id`, deja existent.

## 5. Endpoint-uri propuse

| Endpoint | Metodă | Scop |
|---|---|---|
| `/api/v1/outreach` | POST | Creează intervenția (rezolvă/creează `Contact`, generează cele 3 variante server-side, persistă alegerea finală) |
| `/api/v1/outreach` | GET | Listă recentă, pentru vizibilitate în Workbench |

Fără endpoint separat de "marchează rezultat" — conform deciziei de
design din secțiunea 3.

## 6. Evenimente

Tipar identic cu cele 6 engine-uri existente:

```python
self._emit_event("OutreachSent", outreach.id, {
    "owner_id": str(owner_id),
    "purpose": purpose,
})
```

## 7. Flux E2E

```
Lider alege REFERRAL sau REACTIVATION
        ↓
Alege contact existent SAU introduce nume nou → Contact creat/reutilizat
        ↓
Sistem generează 3 variante (server-side, tipar similar library.py de la Objection)
        ↓
Lider alege/editează, confirmă "Am trimis" → POST /outreach
        ↓
[OutreachSent emis]
        ↓
Lider revine cu rezultat →
        ├── Continuă conversația → POST /conversations (+ source_outreach_id)
        ├── Are ezitare → flux Objection existent (prin Conversation)
        └── Revine mai târziu → POST /followups (+ source_outreach_id)
```

## 8. Explicit exclus din acest contract

- `Mission`, `Priority` — neatinse, nicio legătură implicită creată
- Niciun KPI nou — nicio măsură de "eficiență prospectare" nu se
  inventează aici; dacă va fi nevoie vreodată, trece prin propriul
  proces de tip 44A
- "Biblioteca Experienței" (pasul 8 din ambele specificații) — omis
  din v1, `ExperienceLibraryEngine` nu există, nu se construiește aici
- Integrări Facebook/WhatsApp/TikTok — zero, confirmat deja la
  Decizia 4 din `06-harta-motoare-tehnice.md`
- Workbench — panou nou, dar fără alte modificări la panourile
  existente în afara celor 2 câmpuri opționale de mai sus

## 9. Ownership

Tipar identic, fără excepție: `owner_id` din JWT, `contact_id`
verificat că aparține owner-ului (același model ca la `create_partner`,
`create_from_trigger`).

## 10. Criterii de acceptare (RED, propunere pentru pasul următor)

Nu se scriu acum — urmează după confirmarea acestui contract, cu
aceeași disciplină (unitare + PostgreSQL real + izolare owner HTTP,
minim 2 lideri).

## 11. Ordinea de lucru

```
acest contract (propunere)
        ↓
CONFIRMARE EXPLICITĂ (inclusiv punctul deschis din secțiunea 3)
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

Nu se scrie cod înainte de confirmarea explicită a acestui document.
