# MVP-DATA-001 — MVP Data Model & PostgreSQL Persistence Layer

**Identificator:** `MVP-DATA-001`
**Business Domain:** NicMar OS / MVP Core
**Nivel:** Data Architecture & Persistence
**Versiune:** 1.1 (corectată, 12 august 2026)
**Status:** 🔒 VALIDAT — cele 3 corecturi de audit aplicate
**SSOT Sursă:** `MVP-CORE-001`, `06-harta-motoare-tehnice.md`, `04-KPI-REG-001.md`, `03-rule-model-001.md`
**Metodologie:** MVP Vertical Slice / Deterministic Persistence & Audit

---

## 1. Scopul documentului

`MVP-DATA-001` definește schema fizică a bazei de date PostgreSQL pentru prima versiune funcțională a NicMar OS. Documentul stabilește: structura tabelelor pentru cele 9 Business Objects canonice, tabelele de suport pentru evenimente, istoric de stări și audit, constrângerile de integritate referențială (Foreign Keys) și ownership (`owner_id`), tipurile de date și indexurile necesare pentru performanță și rularea deterministă a motoarelor (v. `06-harta-motoare-tehnice.md`).

**Principiul fundamental:**
> Niciun motor, agent sau componentă MVP nu poate persista date în afara structurilor definite în acest document. Modelul de date este singura sursă de adevăr fizic pentru starea sistemului.

---

## 2. Decizie de audit — reducerea stărilor la subsetul MVP (confirmat 12 august 2026)

**Stările entităților Contact, Partner și Client sunt reduse la subsetul operațional MVP**, eliminând stările intermediare pre-Lider, pentru a menține simplitatea primului vertical slice.

| Business Object | State machine complet (Core, `02-business-objects-5-pillars.md`) | Subset MVP (acest document) |
|---|---|---|
| Contact | New → Active → Engaged → Qualified → Converted → Managed → Archived (7 stări) | `NEW, ACTIVE, CONVERTED, ARCHIVED` (4) |
| Partner | Activated → Onboarding → Active → Developing → Autonomous → Leader → Mentor → Archived (8 stări) | `ACTIVATED, ACTIVE, ARCHIVED` (3) |
| Client | Converted → Active → Loyal → AtRisk → Churned → Reactivated → Archived (7 stări) | `CONVERTED, ACTIVE, ARCHIVED` (3) |
| Mission | Generated → Assigned → InProgress → Completed → Skipped → Expired → Archived (7 stări) | `GENERATED, ASSIGNED, IN_PROGRESS, COMPLETED` (4) |
| Conversation | Initiated → Active → Waiting → FollowUpNeeded → Resolved → Closed → Archived (7 stări) | `INITIATED, ACTIVE, WAITING, FOLLOWUP_NEEDED, RESOLVED, ARCHIVED` (6) |

**Notă audit P4 (12 august 2026):** Mission și Conversation au fost adăugate în acest tabel după verificare explicită de dependențe funcționale (Engine/Event/KPI), nu doar prin analogie cu Contact/Partner/Client. Pentru Mission, cele 3 stări excluse (`Skipped`, `Expired`, `Archived`) sunt gestionate exclusiv de motoare din afara celor 6 MVP (`ContinuityEngine`, `RelationshipEngine`) — excludere confirmată sigură. Pentru Conversation, `FollowUpNeeded` a fost inițial exclusă tăcut, dar verificarea a arătat o ruptură funcțională reală (`FollowUpEngine` + `MissionEngine`, ambele MVP, depind de tranziția spre această stare) — motiv pentru care a fost recuperată; doar `Closed` rămâne exclusă, fiind legată exclusiv de `RelationshipEngine` (neconfirmat în MVP).

**Motiv arhitectural:** în prima versiune funcțională, stările intermediare sunt gestionate prin activitatea motoarelor, interacțiuni și misiuni, fără să complice mașina de stări a bazei de date. Stările complete din Core rămân valabile pentru fazele post-MVP, când motoarele corespunzătoare (`PartnerOnboardingEngine`, `PartnerIntegrationEngine`, `LeadershipDevelopmentEngine` etc., v. `07-motoare-post-mvp.md`) intră în scope.

---

## 3. Convenții de proiectare PostgreSQL

1. **Identificatori:** toate tabelele utilizează `UUID` v4 ca cheie primară (`id`), generat nativ (`gen_random_uuid()`).
2. **Timestamps:** toate tabelele critice conțin cel puțin `created_at` și `updated_at` de tip `TIMESTAMPTZ` (fus orar UTC implicit).
3. **Multi-tenancy / Ownership:** entitățile operaționale aparțin unui utilizator prin coloana obligatorie `owner_id` (referință către `users`).
4. **Stări canonice:** câmpurile de status utilizează `TEXT` cu constrângeri `CHECK`, mapate pe subsetul MVP al mașinilor de stare (v. secțiunea 2).

---

## 4. Schema tabelelor de bază (9 Business Objects)

### 4.1. `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'LEADER',
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);
```

### 4.2. `contacts`
```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    status TEXT NOT NULL CHECK (status IN ('NEW', 'ACTIVE', 'CONVERTED', 'ARCHIVED')),
    source TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_contacts_owner_status ON contacts(owner_id, status);
```

### 4.3. `clients`
```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID UNIQUE NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('CONVERTED', 'ACTIVE', 'ARCHIVED')),
    client_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_clients_owner_status ON clients(owner_id, status);
```

### 4.4. `partners`
```sql
CREATE TABLE partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID UNIQUE NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('ACTIVATED', 'ACTIVE', 'ARCHIVED')),
    partner_level TEXT DEFAULT 'BRONZE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_partners_owner_status ON partners(owner_id, status);
```

### 4.5. `conversations`
**Corectură aplicată (audit P4, 12 august 2026):** `FOLLOWUP_NEEDED` recuperat în schema de stări — exclus inițial fără să fie declarat explicit, dar verificarea a arătat o ruptură funcțională reală: `FollowUpTriggered` (evenimentul care declanșează crearea automată a unui Follow-up) depinde de tranziția `Waiting → FollowUpNeeded`, iar motoarele care reacționează la el (`FollowUpEngine`, `MissionEngine`) sunt ambele confirmate în cele 6 motoare MVP. `Closed` rămâne exclus — motorul care-l gestionează (`RelationshipEngine`, generic) nu e confirmat în cele 6 MVP, iar evenimentul asociat nu influențează niciun KPI direct.
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    channel TEXT NOT NULL DEFAULT 'WHATSAPP',
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('INITIATED', 'ACTIVE', 'WAITING', 'FOLLOWUP_NEEDED', 'RESOLVED', 'ARCHIVED')),
    summary TEXT,
    raw_payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_conversations_contact ON conversations(contact_id, created_at DESC);
```

### 4.6. `missions`
```sql
CREATE TABLE missions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL CHECK (status IN ('GENERATED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED')),
    scheduled_at TIMESTAMPTZ,
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    partner_id UUID REFERENCES partners(id) ON DELETE SET NULL,
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_missions_owner_status ON missions(owner_id, status, scheduled_at);
```

### 4.7. `follow_ups`
**Corectură aplicată (audit G3, 12 august 2026):** `status` primește `CHECK` constraint explicit — câmpul era complet nevalidat (`TEXT` liber). `FollowUp` nu are State Machine dedicată în Core (obiect operațional secundar, ca `Meeting`/`Objection`), dar spre deosebire de `Meeting`, `FollowUpEngine` și `FollowUp Agent` sunt deja MVP activ și folosesc acest tabel — motiv suficient pentru corectare acum, nu FOLLOW-UP. Valorile derivate strict din dovezi (`08-MVP-AGENT-001.md` + `05-competente-37-motor1.md`, Competența `06_Follow_Up`): `PENDING` (așteaptă acțiunea), `COMPLETED` (confirmat de lider ca realizat), `POSTPONED` (lider a ales "mai târziu"), `RESCHEDULED` (reprogramat pentru alt moment).
```sql
CREATE TABLE follow_ups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'COMPLETED', 'POSTPONED', 'RESCHEDULED')),
    scheduled_at TIMESTAMPTZ NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_followups_scheduled ON follow_ups(owner_id, scheduled_at, status);
```

### 4.8. `objections`
```sql
CREATE TABLE objections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    objection_category TEXT NOT NULL,
    objection_text TEXT NOT NULL,
    resolution_status TEXT NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);
```
**Notă:** acest tabel alimentează KPI `ORE` (v. `04-KPI-REG-001.md`, KPI-012) prin `ObjectionEngine`.

### 4.9. `meetings`
```sql
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    partner_id UUID REFERENCES partners(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    scheduled_at TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'SCHEDULED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_meetings_schedule ON meetings(owner_id, scheduled_at);
```

---

## 5. Tabele de suport și audit (infrastructură deterministă)

### 5.1. `rules` (pentru `ENG-RULE-001` / `RuleEngine`)
```sql
CREATE TABLE rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code TEXT UNIQUE NOT NULL,
    rule_version TEXT NOT NULL DEFAULT '1.0.0',
    logic_definition JSONB NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);
```

### 5.2. `rule_evaluations` (adăugat — audit P3, 12 august 2026)
**Decizie de audit:** obligatoriu în MVP, nu conceptual/post-MVP. `RULE-MODEL-001` (secțiunea 21-23) definește persistența evaluărilor ca cerință fermă, necondiționată de scope MVP (documentul nu face nicio distincție MVP/full-architecture). `RuleEngine` e deja motor activ în MVP (Decizia 1); fără acest tabel, se pierde trasabilitatea versiunii regulii care a produs fiecare decizie — informație pe care `audit_log` (tabel generic, pentru toate motoarele) nu o poate substitui.

**Schema preluată exact din `RULE-MODEL-001`, secțiunea 21 (Rule Evaluation Persistence)**, fără modificări:
```sql
CREATE TABLE rule_evaluations (
    evaluation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID NOT NULL REFERENCES rules(id) ON DELETE CASCADE,
    rule_code TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    target_object_type TEXT NOT NULL,
    target_object_id UUID NOT NULL,
    trigger_event TEXT,
    result TEXT NOT NULL,
    outcome_code TEXT,
    score NUMERIC,
    context_payload JSONB DEFAULT '{}'::jsonb,
    result_payload JSONB DEFAULT '{}'::jsonb,
    correlation_id UUID,
    actor_id UUID,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_rule_evaluations_rule ON rule_evaluations(rule_code, rule_version);
CREATE INDEX idx_rule_evaluations_target ON rule_evaluations(target_object_type, target_object_id);
```

**Relația cu `audit_log` (clarificare, nu suprapunere):** `rule_evaluations` e istoricul specializat al evaluărilor de reguli (cu versiune, scor, obiect țintă exact) — `audit_log` rămâne audit generic, cross-engine, pentru execuții și decizii la nivel de motor, nu de regulă individuală. Fluxul confirmat: `rules → rule_evaluations → events → audit_log`.

### 5.3. `state_history`
```sql
CREATE TABLE state_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    previous_state TEXT,
    new_state TEXT NOT NULL,
    triggered_by_event TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_state_history_entity ON state_history(entity_type, entity_id);
```

### 5.4. `audit_log`
**Corectură aplicată (audit 12 august 2026):** referință redenumită din `RuleEvaluationEngine` (nume rezidual, neactualizat) în `RuleEngine`, aliniat cu Decizia 1 din `06-harta-motoare-tehnice.md`.
```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engine_id TEXT NOT NULL,
    rule_code TEXT,
    decision_outcome TEXT,
    reason_code TEXT,
    payload_snapshot JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_audit_engine ON audit_log(engine_id, created_at DESC);
```
*(Înregistrează execuțiile critice ale motoarelor și deciziile luate de `RuleEngine`.)*

### 5.5. `events`
```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name TEXT NOT NULL,
    target_object TEXT NOT NULL,
    target_object_id UUID NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_events_name_time ON events(event_name, created_at DESC);
```

---

## 6. Status final

**Document:** `MVP-DATA-001`
**Versiune:** 1.1
**Status:** 🔒 VALIDAT — toate cele 3 corecturi de audit aplicate (reducere stări documentată explicit, `RuleEngine` corectat, `conversations.status` adăugat)
**Rol:** schema de persistență PostgreSQL pentru MVP Core și Motoare, aliniată cu `06-harta-motoare-tehnice.md` și `04-KPI-REG-001.md`.

---
*Document canonic. Coroborează cu `06-harta-motoare-tehnice.md` (motoare), `04-KPI-REG-001.md` (KPI), `08-MVP-AGENT-001.md` (agenți).*
