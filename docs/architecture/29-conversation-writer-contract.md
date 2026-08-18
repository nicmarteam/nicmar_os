# DECIZIA 29 — `ConversationEngine` ("Conversation Writer") — CONTRACT v1

**Status:** verificat direct din schema (`contacts`, `conversations`, `events`) și din pattern-urile
existente (`FollowUpEngine.create_from_trigger`, `PartnerEngine._verify_ownership`) — nu din
memorie. **Nu se conectează la niciun canal (WhatsApp/Messenger/Facebook)** — asta rămâne
decizie separată, ulterioară, explicit amânată.

**Atenție la nume:** `ConversationEngine` (acest contract) e complet diferit de
`ConversationAgent` (existent, `22-...md`) — al doilea orchestrează fluxul `Objection`, n-are
nicio legătură cu tabela `conversations`. Coincidența de nume e reală și trebuie păstrată în
minte la implementare — nu le confundăm, nu le unificăm.

---

## 1. Cine creează conversația

**Sistemul, printr-o singură metodă**: `ConversationEngine.get_or_create_conversation()`.
Nu liderul manual, nu clientul HTTP direct — orice apelant (viitor webhook de canal, sau orice
alt cod) trece prin această metodă, niciodată prin `INSERT` direct.

`contact_id` **obligatoriu** — verificat din schema reală: `conversations.contact_id UUID NOT
NULL REFERENCES contacts(id)`. Nu există conversație fără contact asociat.

## 2. Când se creează rândul — evenimentul exact

**În acest contract, nu există încă niciun eveniment real care declanșează crearea** — pentru
că niciun canal nu e conectat. Metoda există, testată complet, dar **neapelată de nimic în
producție** — identic cu situația `PriorityEngine v1`, care există fără router. Viitorul
webhook de canal va apela `get_or_create_conversation()` la primul mesaj primit; asta rămâne
decizia componentei 5, nu a acesteia.

**Dacă conversația există deja** (pentru același `contact_id`, status încă deschis):
`get_or_create_conversation()` **returnează conversația existentă**, fără `INSERT` nou.

**Prevenirea duplicatelor — verificat explicit, fără presupunere:** schema `conversations`
**nu are constrângere `UNIQUE`** pe `(owner_id, contact_id)` — am verificat direct în
`001_initial_schema.sql`. PostgreSQL nu împiedică singur duplicate. Deci logica de idempotency
trebuie să fie explicit `SELECT` înainte de `INSERT`, în cod, la fel ca la
`FollowUpEngine.create_from_trigger()` (verificare `RuleEngine` înainte de scriere).

## 3. Relația `contacts → conversations`

- Cheia reală: `conversations.contact_id → contacts.id` (FK, verificat)
- `owner_id`: prezent și în `contacts`, și în `conversations` — **denormalizat intenționat**
  (verificat din schemă), nu derivat doar prin `contact_id`
- **Verificare ownership obligatorie, dincolo de FK**: FK-ul garantează doar că `contact_id`
  există undeva — **nu** garantează că aparține owner-ului care face cererea. Exact
  vulnerabilitatea documentată în `PartnerEngine._verify_ownership()` ("Security Isolation
  Audit, 12 august 2026") — fără verificare explicită, un lider ar putea crea o conversație
  legată de contactul altui lider, doar cunoscându-i `contact_id`. Reproduc același pattern:
  `SELECT 1 FROM contacts WHERE id = %s AND owner_id = %s` înainte de orice scriere.
- Un contact **poate avea mai multe conversații** — confirmat din index-ul real,
  `idx_conversations_contact ON conversations(contact_id, created_at DESC)`, proiectat exact
  pentru interogarea "ultima conversație a acestui contact". Idempotency-ul de la punctul 2 se
  aplică doar conversațiilor **deschise** (status ∈ `INITIATED`/`ACTIVE`/`WAITING`/
  `FOLLOWUP_NEEDED`) — o conversație `RESOLVED`/`ARCHIVED` nu blochează crearea uneia noi.

## 4. Ce reprezintă o conversație

- **Container**, nu jurnal de mesaje — conversația e "sesiunea" cu un contact, pe un canal.
- **Nu există azi o tabelă `messages`** — verificat, singurele tabele din schemă sunt cele 16
  existente (`users`...`events`), fără niciuna dedicată mesajelor individuale. Introducerea
  unei asemenea tabele **e explicit în afara scopului acestui contract**.
- **Diferența față de `objection`**: o `objection` e deja legată de `conversation_id`
  (`objections.conversation_id`, opțional, verificat) — o obiecție e un eveniment **în
  interiorul** unei conversații, nu o conversație în sine. `ConversationEngine` nu creează
  obiecții, `ObjectionEngine` nu creează conversații — fiecare rămâne pe propriul domeniu.

## 5. Ce face `ConversationEngine`

Exclusiv: `SELECT` (verificare ownership + verificare idempotency) → `INSERT` condiționat →
`RETURNING` → `Conversation` dataclass. Nimic altceva.

## 6. Ce NU face — arhitectura explicită

```
Channel (viitor) → ConversationEngine → DB
                              ↑
        ConversationAgent → Objection (existent, neschimbat)
```

**NU:**
- `ConversationEngine → WhatsApp/Facebook` — nicio livrare, nicio integrare externă
- `ConversationEngine → ObjectionEngine` — nu clasifică, nu creează obiecții
- `ConversationEngine → Safety Validation` — zero validare de conținut
- `ConversationEngine` nu alege răspunsuri, nu interpretează mesaje — doar persistă
  existența/starea unei conversații

## 7. Idempotency

```python
def get_or_create_conversation(
    self, owner_id: UUID, contact_id: UUID, channel: str = "WHATSAPP",
) -> Conversation:
```

Ordine internă:
1. Verifică ownership (`contact_id` aparține `owner_id`) → altfel `ConversationAccessDeniedError`
2. `SELECT` conversație existentă, `WHERE owner_id=%s AND contact_id=%s AND status IN
   ('INITIATED','ACTIVE','WAITING','FOLLOWUP_NEEDED') ORDER BY created_at DESC LIMIT 1`
3. Dacă găsită → **returnează direct, fără scriere**
4. Dacă nu → `INSERT ... RETURNING`, `status='INITIATED'` implicit

**Limitare cunoscută, nu ascunsă:** acest `SELECT`-apoi-`INSERT` are aceeași fereastră de
cursă (race condition) teoretică ca și `FollowUpEngine.create_from_trigger()` — două request-uri
simultane, pentru același contact, ar putea ambele trece de verificare înainte ca vreunul să
scrie. Nu introduc o soluție nouă (ex. `SELECT FOR UPDATE`, `INSERT ... ON CONFLICT`) fără s-o
discutăm — repo-ul nu rezolvă asta nicăieri altundeva, deci rămân consecvent, dar semnalez
explicit limitarea aici, nu o ascund.

## 8. Securitate

- `owner_id` — exclusiv parametru din apelant (viitor: JWT/context intern), **niciodată** din
  payload extern necontrolat. Acest contract nu expune încă niciun endpoint HTTP — deci nu
  există azi "payload de client" propriu-zis; regula rămâne valabilă pentru orice viitor
  apelant.
- Acces filtrat prin ownership — verificat la pasul 1, cu `ConversationAccessDeniedError`
  (mesaj identic pentru "nu există" și "aparține altcuiva" — previne enumerare, la fel ca
  `ObjectionNotFoundError`/`PartnerAccessDeniedError`).

## 9. Testarea — RED → GREEN → PostgreSQL real, obligatoriu User A/User B + duplicate

1. Contract (acest document)
2. RED: teste unitare (mock) pentru `get_or_create_conversation()`
3. GREEN: implementare `src/engines/conversation/conversation_engine.py`
4. PostgreSQL real:
   - creare reușită, câmpuri corecte
   - apel al doilea, același contact → **aceeași conversație**, nu una nouă (idempotency)
   - **User A creează contact + conversație; User B încearcă
     `get_or_create_conversation(contact_id_A, owner_B)` → `ConversationAccessDeniedError`**
   - `contact_id` inexistent → `ConversationAccessDeniedError`
5. Regresie completă

---

## Ce rămâne explicit NEDECIS (viitoare decizii separate)

- Componenta 5: cine apelează `get_or_create_conversation()` (webhook de canal)
- Tabelă `messages`/jurnal de mesaje individuale
- Soluție pentru fereastra de cursă la creare concurentă
- Orice endpoint HTTP peste `ConversationEngine`
