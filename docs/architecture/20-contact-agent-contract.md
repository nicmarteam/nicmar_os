# CONTACT AGENT — IMPLEMENTATION CONTRACT v1

**Status:** verificat față de `08-MVP-AGENT-001.md` (Agent 1, corectură P6), `02-business-objects-5-pillars.md` (State Machine Contact), `09-MVP-DATA-001.md`/`001_initial_schema.sql` (schema reală), și codul real existent (`mission_agent.py`, `partner_agent.py`, `auth/dependencies.py`)
**Data:** 17 august 2026
**Precedent:** aceeași disciplină ca `11`/`12`/`13`/`19` (Mission/FollowUp/Partner/Priority) — contract înainte de cod, verificare explicită DECLARAT vs. EXISTĂ, TDD strict, izolare `owner_id` testată

---

## 0. Ce NU face acest agent (scop strict)

`ContactAgent` **nu creează, nu modifică, nu tranziționează** starea niciunui `Contact`. E strict un agent de **citire + prezentare + recomandare** — produce o listă prioritizată de contacte și un motiv scurt pentru fiecare, liderul alege, nimic nu se scrie automat.

Confirmat explicit în sursă (`08-MVP-AGENT-001.md`, Agent 1, corectură P6): *"Contact Agent nu modifică niciodată starea Contactului. Tranzițiile (New→Active→Engaged→Qualified) rămân declanșate exclusiv de evenimentele reale de interacțiune... nu de recomandarea Agentului."*

**Notă terminologică:** sursa (`02`) descrie state machine-ul Core cu 7 stări (`New→Managed→Archived`); schema DB reală (`001_initial_schema.sql`) implementează subsetul MVP de 4: `NEW, ACTIVE, CONVERTED, ARCHIVED`. Acest contract lucrează exclusiv cu cele 4 stări MVP existente în `contacts.status` — nu inventează logică pentru stările Core neimplementate.

---

## 1. Distincție obligatorie: architectural owner vs. implemented capability

Acest contract tratează separat, pentru fiecare motor citat în `08-MVP-AGENT-001.md`, ce **declară** arhitectura față de ce **există efectiv** ca fișier `.py` în `src/`. Confuzia dintre cele două a fost exact eroarea găsită anterior la `CustomerRelationshipEngine` (citat ca motor MVP complet, deși e doar declarat, nu implementat) — acest contract nu repetă greșeala.

| Motor citat (`08-MVP-AGENT-001.md`, Agent 1) | Rol declarat | Status verificat în cod |
|---|---|---|
| `RelationshipEngine` | State Owner real al `Contact` (`02`, linia 237), folosit **READ-ONLY** | **DECLARAT ARHITECTURAL — zero cod.** Niciun fișier `src/engines/relationship/`. Nu se scrie acest motor în v1. |
| `CustomerRelationshipEngine` | Context pentru contactele convertite în Client | **ABSENT din cod.** Motor MVP conform `06-harta-motoare-tehnice.md`, dar neimplementat — dependință absentă, nu se inventează în acest contract. |
| `PartnerRelationshipEngine` | Context pentru contactele convertite în Partner | **ABSENT din cod SUB ACEST NUME.** Codul real conține `PartnerEngine` (`src/engines/partner/partner_engine.py`), care e motorul care persistă `PDI`/`PIP` — dar nu implementează State Owner "relationship" pentru Partner, doar diagnostic + confirmare. Tratat ca dependință absentă pentru scopul acestui contract (v. secțiunea 3). |

**Consecință directă pentru v1:** `ContactAgent` **nu poate citi din niciunul din cele 3 motoare de mai sus**, pentru că niciunul nu există ca implementare reală. Singura sursă de date reală și verificată e interogare directă asupra tabelelor SQL existente (`contacts`, `clients`, `partners`, `scores`+`kpis`), exact ca tiparul `get_recent_dis_score()`/`get_recent_scores()` din `MissionAgent`/`PartnerAgent`.

---

## 2. Sursele de date reale, verificate în schema DB (`001_initial_schema.sql`)

### 2.1 Tabel `contacts` — câmpuri reale
```sql
id UUID PK
owner_id UUID NOT NULL REFERENCES users(id)
full_name TEXT NOT NULL
phone TEXT
email TEXT
status TEXT NOT NULL CHECK (status IN ('NEW', 'ACTIVE', 'CONVERTED', 'ARCHIVED'))
source TEXT
metadata JSONB
created_at, updated_at TIMESTAMPTZ
```
Index existent: `idx_contacts_owner_status ON contacts(owner_id, status)` — folosit direct de interogarea principală a agentului.

### 2.2 Tabele derivate, pentru context Client/Partner
```sql
clients(id, owner_id, contact_id UNIQUE, status, client_data, ...)
partners(id, owner_id, contact_id UNIQUE, status, partner_level, ...)
```
Un `Contact` cu `status='CONVERTED'` poate avea un rând corespondent în `clients` SAU `partners` (relație 1-la-1 via `contact_id UNIQUE`). Acest contract **citește** ambele tabele prin JOIN opțional pe `contact_id`, fără să presupună care din cele două există.

### 2.3 `follow_ups` — pentru "ultima interacțiune" / "follow-up-uri restante"
```sql
follow_ups(id, owner_id, contact_id, conversation_id, status, scheduled_at, notes, ...)
```
Câmp real folosit: `contact_id`, `status`, `scheduled_at`. Statusurile reale: `PENDING, COMPLETED, POSTPONED, RESCHEDULED` (verificat, identic cu `19-priority-engine-contract.md` secțiunea 5).

### 2.4 `scores` + `kpis` — pentru CRH/PDI/PIP
```sql
scores(id, kpi_id FK kpis, entity_type, entity_id, score_value, calculated_at, ...)
kpis(id, metric_code UNIQUE, name, status, ...)
```
**Stare reală verificată** (`migrations/002_seed_minimal.sql`): toți cei 13 KPI, inclusiv `CRH`, `PDI`, `PIP`, sunt seed-uiți cu `status='PROPOSED'`. `CRH` **nu are nicio scriere reală în `scores` nicăieri în cod** (grep confirmat, zero producători). `PDI`/`PIP` **au scriere reală**, dar doar din `PartnerEngine.confirm_and_complete()` (`partner_engine.py:207-220`), cu valoare fixă `1.0`, fără formulă — identic cu tiparul deja documentat în `17-kpi-dependency-map.md`.

---

## 3. Ce citește `ContactAgent` v1 — exhaustiv

| Sursă | Ce citește | Metodă |
|---|---|---|
| `contacts` | listă contacte ale `owner_id`, cu `status` | `SELECT ... WHERE owner_id = %s`, index `idx_contacts_owner_status` |
| `clients` / `partners` | dacă un contact convertit are rând corespondent (context, nu recalculare) | `LEFT JOIN` opțional pe `contact_id` |
| `follow_ups` | cel mai recent follow-up per contact (dată, status) — pentru "ultima interacțiune" | `SELECT ... WHERE contact_id = %s ORDER BY scheduled_at DESC LIMIT 1`, per contact |
| `scores` + `kpis` | scor `PDI`/`PIP` cel mai recent **per Partener individual** (`entity_id = partners.id`), DOAR pentru contactele convertite în Partner | `WHERE p.id = ANY(partner_ids) AND p.owner_id = %s` — v. corectură secțiunea 3.1 |

### 3.1 Corectură de granularitate (confirmată 17 august 2026, audit tehnic)

**Bug identificat, nu simplificare de scop:** o primă implementare (GREEN inițial) citea PDI/PIP agregat per `owner_id` — cel mai recent scor al **oricărui** Partener al liderului, aplicat identic tuturor Contactelor convertite în Partener ale acelui owner. Verificat direct în `partner_engine.py:229`: `scores.entity_id` e populat cu `partner_id` exact — granularitatea per-Partener **există deja în schema DB**, doar interogarea inițială nu o folosea.

**Corectat:** `ContactAgent` citește PDI/PIP filtrat pe `partner_id`-ul specific al fiecărui Contact convertit, nu pe `owner_id` agregat. Fiecare Contact convertit în Partener primește scorul propriului Partener, niciodată al altuia.

**Motiv pentru care nu a fost tratat ca "limitare acceptabilă v1":** spre deosebire de alte simplificări din acest contract (ex. Partner exclus din `PriorityEngine`, unde datele pentru a face altfel nu există), aici datele corecte există deja în `scores.entity_id`. A le ignora ar fi însemnat livrarea unui rezultat cunoscut-incorect, nu doar incomplet.

**`CRH` explicit exclus din citire în v1** — motiv verificat, nu presupus: zero producători în cod (secțiunea 2.4). A citi un KPI care nu e scris niciodată ar întoarce mereu `None`/listă goală — comportament corect tehnic, dar contractul îl semnalează explicit ca "citire fără sursă", nu ca omisiune tăcută.

---

## 4. Ce NU poate face `ContactAgent` v1 (limite explicite)

- **Nu scrie niciodată** în `contacts`, `clients`, `partners`, `scores`, `follow_ups` — read-only strict, aceeași regulă ca `MissionAgent`/`PartnerAgent`.
- **Nu calculează CRH, PDI sau PIP** — le citește dacă există (PDI/PIP), le omite dacă nu (CRH).
- **Nu declanșează tranziții de stare** (`NEW→ACTIVE→CONVERTED→ARCHIVED`) — acestea rămân, conform `02`, declanșate exclusiv de evenimente reale de interacțiune, niciun engine care le implementează nu există încă în cod.
- **Nu prioritizează global** (nu e `PriorityEngine`) — ordinea listei în v1 e o sortare simplă, explicită mai jos (secțiunea 5), nu un scor compozit.
- **Nu include Conversation** — motiv, secțiunea 6.

---

## 5. Output v1 — listă prioritizată, regulă explicită, fără formulă inventată

```python
@dataclass(frozen=True)
class ContactSummary:
    contact_id: UUID
    full_name: str
    status: str                          # NEW | ACTIVE | CONVERTED | ARCHIVED
    last_followup_at: Optional[datetime] # None daca nu exista follow-up
    last_followup_status: Optional[str]
    converted_to: Optional[str]          # "client" | "partner" | None
    pdi: Optional[float]                 # doar daca converted_to == "partner"
    pip: Optional[float]                 # doar daca converted_to == "partner"
    reason: str                          # motiv scurt, derivat din grupul de prioritate
```

### 5.1 `reason` — CONFIRMAT explicit de owner (17 august 2026), corectură a inconsistenței interne a contractului

Descoperire de audit: secțiunea 0 a acestui contract promitea deja "un motiv scurt pentru fiecare" (aliniat cu `08-MVP-AGENT-001.md`), dar `ContactSummary` inițial nu avea acest câmp — inconsistență internă, nu doar diferență față de `08`. Corectată aici.

**`reason` nu calculează nimic nou și nu modifică `PriorityKey`/sortarea** — e strict explicația textuală a grupului deja calculat de `_priority_group()`. Regula CONFIRMATĂ:

```
Grup 0 (FollowUp scadent)              → "Follow-up scadent"
Grup 1 (fără niciun FollowUp)          → "Fără follow-up programat"
Grup 2 (restul), sub-caz FollowUp
    PENDING dar programat în viitor    → "Fără follow-up scadent"
Grup 2 (restul), orice alt caz
    (COMPLETED/POSTPONED/RESCHEDULED)  → "Prioritate după actualizare"
```

Notă de interpretare, semnalată explicit: regula confirmată de owner distinge textual 4 cazuri, deși `PriorityKey` are doar 3 grupuri numerice (0/1/2) — grupul 2 ("restul") se împarte în două formulări diferite după caz, fără să schimbe poziția în sortare. Motivul practic al distincției: „fără follow-up scadent" (există un FollowUp viitor programat) e o informație diferită pentru lider față de „prioritate după actualizare" (nu există niciun FollowUp activ relevant).

**Regula de sortare v1 — CONFIRMATĂ explicit de owner (17 august 2026), nu doar propusă:**
```
1. FollowUp scadent (status='PENDING' AND scheduled_at <= ACUM) → prioritate maximă
2. Contact fără niciun FollowUp (zero rânduri în follow_ups pentru acel contact_id) → nivelul următor
3. Restul → sortat după updated_at DESC
```
Regulă declarată explicit ca decizie de business logic, nu fapt extras din `08-MVP-AGENT-001.md` (care cere doar "listă prioritizată + motiv", fără algoritm). Confirmată de owner după audit — nu se mai tratează ca presupunere de implementare.

Precizări suplimentare confirmate în aceeași decizie:
- **`ARCHIVED` exclus explicit din output** — un contact arhivat nu justifică o recomandare de contactare azi.
- **`CONVERTED` rămâne disponibil** în lista operațională, conform regulii de mai sus (nu primește tratament special de excludere) — dar **fără scor KPI artificial**: `pdi`/`pip` se populează doar dacă există deja o scriere reală în `scores` (v. secțiunea 2.4/3), niciodată calculate sau aproximate de agent.
- Toate cele 3 grupuri rămân filtrate strict la `owner_id`-ul din `current_user` (secțiunea 7) — regula de sortare se aplică DUPĂ filtrare, niciodată înainte.

---

## 6. Conversation — exclus explicit din v1

**Motiv verificat, nu presupus:** tabela `conversations` există în DB (`001_initial_schema.sql`), dar **nu există niciun engine sau agent Conversation în cod** (`src/engines/conversation/`, `src/agents/conversation/` — ambele absente, grep confirmat). `08-MVP-AGENT-001.md` descrie un "Conversation Agent" separat (Agent 2, motor sursă `ObjectionEngine`), dar acesta e la fel de neimplementat ca și Contact Agent — nu e o dependință disponibilă pentru acest contract.

`ContactAgent` v1 **nu citește din `conversations`** și **nu afișează contextul conversațional** — doar `follow_ups`, care au propriul `contact_id` direct (nu necesită join prin `conversations` pentru acest v1).

---

## 7. Autentificare și izolare — tipar existent, reutilizat identic

```python
current_user: CurrentUser = Depends(get_current_user)  # src/auth/dependencies.py
```

`owner_id` **nu vine niciodată din request body/query** — vine exclusiv din `current_user.id`, extras din JWT validat. Identic cu tiparul din `routers/partners.py`/`routers/missions.py`. Fiecare interogare SQL din `ContactAgent` filtrează explicit `WHERE owner_id = %s` (sau `WHERE p.owner_id = %s` prin JOIN, pentru tabelele derivate) — aceeași disciplină care a prins bug-ul real de izolare la `PartnerAgent.get_recent_scores()` (comentariu explicit în cod, `partner_agent.py:83-85`).

---

## 8. Structura de fișiere

```
src/agents/contact/
├── __init__.py
└── contact_agent.py       (NOU)
```

Fără engine dedicat (`ContactEngine`) în v1 — motiv: agentul nu scrie nimic, deci nu are nevoie de un State Owner propriu. Toate interogările sunt SELECT direct via `src.data.db.get_connection()`, tipar identic cu `MissionAgent.get_recent_dis_score()` și `PartnerAgent.get_recent_scores()`. Dacă apare nevoia de scriere (ex. marcarea unei recomandări ca "văzută"), decizia de a introduce un `ContactEngine` rămâne FOLLOW-UP explicit, nu implicit.

---

## 9. Criterii de acceptare și teste obligatorii înainte de cod finalizat

- [x] `list_prioritized_contacts(owner_id)` returnează doar contacte ale `owner_id`-ului cerut — test de izolare cu 2 lideri (tiparul `test_security_isolation.py`) — verificat mock + PostgreSQL real
- [x] Contacte `ARCHIVED` nu apar niciodată în output — verificat mock + PostgreSQL real
- [x] Regula de sortare (secțiunea 5): follow-up scadent înaintea celor fără follow-up, înaintea restului — testat cu date explicite pentru toate cele 3 grupuri, mock + PostgreSQL real
- [x] Contact fără niciun `follow_up` → `last_followup_at=None`, fără eroare
- [x] Contact `CONVERTED` cu rând în `clients` → `converted_to="client"`, `pdi`/`pip`=`None`
- [x] Contact `CONVERTED` cu rând în `partners` → `converted_to="partner"`, `pdi`/`pip` populate **per Partener individual** (corectură secțiunea 3.1) dacă există în `scores`, altfel `None`
- [x] Contact `CONVERTED` fără rând nici în `clients`, nici în `partners` (caz de date inconsistente) → `converted_to=None`, fără crash — verificat mock + PostgreSQL real (17 august 2026); comportament corect prin logica SQL `CASE` existentă, nu a fost nevoie de cod nou
- [x] `owner_id` fără niciun contact → listă goală `[]`, nu eroare
- [x] Niciun apel SQL nu scrie — verificat prin test care confirmă `INSERT`/`UPDATE`/`DELETE` absente din toate interogările
- [x] PostgreSQL real: test de integrare stateful, `TestContactAgentOnRealPostgres` în `test_real_postgres.py` (6 teste, toate GREEN)
- [x] Regresie completă: **162/162** teste ale întregului repo rămân verzi (confirmat local, PostgreSQL 16, 17 august 2026 — actualizat după adăugarea `reason` și a testului pentru `CONVERTED` fără `clients`/`partners`; număr inițial 115+ reflecta starea dinaintea adăugării ContactAgent)

---

## 10. Lista exactă a lucrurilor care rămân pentru o versiune ulterioară

1. **`RelationshipEngine` real** — implementare completă ca State Owner pentru `Contact`/`Conversation`, cu tranziții de stare reale (`NEW→ACTIVE→CONVERTED→ARCHIVED` declanșate de evenimente)
2. **`CustomerRelationshipEngine`** — motor MVP declarat, neimplementat
3. **`PartnerRelationshipEngine`** — clarificare necesară: relația cu `PartnerEngine` existent (redenumire? motor separat? unificare?) — decizie arhitecturală, nu tehnică, necesită confirmare explicită înainte de cod
4. **`CRH`** — formulă complet nedefinită (`KPI-MODEL-001`, nescris încă), zero producători în cod
5. **Conversation Agent** — motor sursă `ObjectionEngine`, neimplementat
6. **Scor de prioritate compozit real** pentru Contact — echivalentul `PriorityEngine`, dar pentru Contact (`PriorityEngine` v1 existent acoperă doar Mission+FollowUp, exclude explicit Contact/Partner ca input)
7. **Acțiune de "marcare ca văzut/procesat"** pentru o recomandare a agentului — ar necesita `ContactEngine` sau extensie de scriere, out of scope v1 (agent strict read-only)
8. **Actualizarea `10-audit-general-nicmar-os.md`** — documentul afirmă în secțiunea 10 "Zero implementare" pentru `engines/`/`agents/`, fals la data acestui contract (Mission/FollowUp/Partner/Priority au cod real complet); necesită regenerare, nu e în scope-ul acestui contract, dar e semnalat aici ca să nu fie folosit ca sursă de adevăr pentru "ce există în cod"

---
*Contract verificat direct din `nicmar_os-main` (arhivă repo, 17 august 2026) — fiecare afirmație din secțiunile 1-4 clasificată explicit EXISTĂ/PLACEHOLDER/ABSENT/DECLARAT ARHITECTURAL, verificată prin `grep` și citire directă de fișier, nu din memorie sau prin analogie cu alte contracte.*
