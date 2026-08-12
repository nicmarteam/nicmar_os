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
**Corectură aplicată (audit 12 august 2026):** adăugată coloana `status`, absentă în draftul inițial — fără ea, motoarele ar fi trebuit să interogheze constant istoricul brut de evenimente ca să afle dacă o conversație e încă deschisă.
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    channel TEXT NOT NULL DEFAULT 'WHATSAPP',
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('INITIATED', 'ACTIVE', 'WAITING', 'RESOLVED', 'ARCHIVED')),
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
```sql
CREATE TABLE follow_ups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
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

### 5.2. `state_history`
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

### 5.3. `audit_log`
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

### 5.4. `events`
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
