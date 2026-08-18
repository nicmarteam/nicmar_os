# DECIZIA 36 — WORKBENCH → FOLLOWUP — CONTRACT

**Status:** confirmat de owner. Verificat direct din `followup_engine.py`, `followup_agent.py`,
`followups.py`, `schemas.py`, `12-contact-followup-vertical-slice-contract.md` — nu din memorie.

**Precondiție închisă**: Decizia 35 a stabilit definitiv că `Objection → FollowUp` **nu e
relație arhitecturală** — acest contract nu o introduce, nu o presupune.

---

## 0. Descoperire RED — un gol real în API, nu în `FollowUpEngine`

`CreateFollowUpRequest` (`schemas.py`) **nu are câmpurile `notes`/`scheduled_at`**, deși
`FollowUpEngine.create_from_trigger()` le acceptă opțional (`notes: Optional[str] = None`,
`scheduled_at: Optional[str] = None`, cu `COALESCE(%s, clock_timestamp())` în `INSERT`).
Router-ul (`followups.py`) nici nu le pasează azi.

**Decizie, folosind excepția autorizată explicit** ("cu excepția situației în care auditul RED
descoperă o problemă reală"): extindem **doar** `CreateFollowUpRequest` + pass-through în
router — **zero linie modificată în `FollowUpEngine`**, care deja suportă aceste câmpuri.
Nu e o regulă de business nouă, e conectarea unui parametru deja existent, neexpus din
neatenție.

```python
class CreateFollowUpRequest(BaseModel):
    contact_id: UUID
    conversation_id: UUID
    notes: Optional[str] = None
    scheduled_at: Optional[str] = None
```

Router: `create_from_trigger(current_user.id, body.contact_id, body.conversation_id,
notes=body.notes, scheduled_at=body.scheduled_at)`.

---

## 1. Scope — confirmat, neschimbat față de propunerea ta

Extindem **doar** `apps/workbench/index.html` + extensia minimă de la Secțiunea 0. Restul
backend-ului (`FollowUpEngine`, `PriorityEngine`, `RuleEngine`) rămâne complet neatins.

## 2. Date reutilizate din Decizia 34

```javascript
currentContactId, currentConversationId, authToken, apiFetch()
```

Zero mecanism nou de selecție Contact/Conversation.

## 3. UI nou — panel "Follow-Up", după panelul Contact/Conversație

- Câmpuri: `Notes` (opțional), `Scheduled at` (opțional, `datetime-local`) — vezi Secțiunea 0
- Buton "Creează Follow-Up" — **dezactivat** dacă `currentContactId`/`currentConversationId`
  lipsesc (regula de siguranță, Secțiunea 4)
- Listă "Follow-Up-uri în așteptare" (`GET /api/v1/followups`, doar `PENDING`, deja filtrat
  server-side) — reîncărcată după fiecare acțiune
- Fiecare item: `contact_id`/`conversation_id` (afișate ca atare — Workbench n-are încă
  numele contactului asociat unui `follow_up` fără un JOIN suplimentar, ne-construit acum),
  `scheduled_at`, `notes`, 3 butoane

## 4. Regula de siguranță — verificată structural

```javascript
if (!currentContactId || !currentConversationId) {
    // buton dezactivat / request neconstruit
}
```

Identic principiu cu dezactivarea `panel-analyze` până la conversație (Decizia 34).

## 5. Cele 3 acțiuni — fără body suplimentar, exact ca API-ul

- **Finalizează** → `POST /followups/{id}/complete`, body `{"confirmed": true}` — singurul
  care cere confirmare explicită (regulă deja existentă, `HumanConfirmationRequiredError`)
- **Amână** → `POST /followups/{id}/postpone`, fără body
- **Reprogramează** → `POST /followups/{id}/reschedule`, fără body

## 6. Ce NU se introduce — confirmat, listă din propunerea ta

`objection_id`, automatizare `Objection → FollowUp`, `FOLLOWUP_NEEDED` ca precondiție, reguli
noi de business, modificări în `FollowUpEngine`/`PriorityEngine`.

## 7. Testarea — Nivel 1 (structural) + Nivel 2 (server real)

**Nivel 1** — extensie `test_workbench_structure.py`:
- `/api/v1/followups` prezent (POST creare + GET listă, aceeași cale)
- Template literale pentru `/complete`, `/postpone`, `/reschedule` prezente
- Marcaj nou `FOLLOWUP_PAYLOAD_START/END` — conține `currentContactId`/`currentConversationId`
- Guard-ul de siguranță (Secțiunea 4) prezent ca literal verificabil
- `owner_id` — absent, regresie verificată din nou

**Nivel 2** — server HTTP real, flux echivalent (aceeași limitare documentată la Decizia 27/34):
```
register → login → creez contact → creez conversație
    → creez follow-up (notes + scheduled_at) → 201
    → GET /followups → apare în listă, status PENDING
    → complete (confirmed=true) → 200, status COMPLETED
    → GET /followups → dispare din listă (nu mai e PENDING)
```

## 8. Criteriul de acceptare final

```
Login → Workbench → selectez Contact + Conversation → creez Follow-Up
    → apare în lista PENDING → Finalizez → dispare din listă
    → verificat din DB: follow_up.status == 'COMPLETED'
```
