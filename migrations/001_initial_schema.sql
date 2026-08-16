-- ============================================================
-- NicMar OS — Migration 001: Initial Schema
-- ============================================================
-- Sursa: docs/architecture/09-MVP-DATA-001.md (v1.3, 16 tabele)
-- Generat: extras verbatim din document, fara nicio coloana,
-- tabel sau relatie adaugata/modificata.
-- Ordine: respecta dependintele FK (fiecare tabel doar dupa cele
-- pe care le referentiaza).
-- ============================================================

-- Extensia necesara pentru gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ------------------------------------------------------------
-- Tabel: users
-- ------------------------------------------------------------
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'LEADER',
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- ------------------------------------------------------------
-- Tabel: contacts
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: clients
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: partners
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: conversations
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: missions
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: follow_ups
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: objections
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: meetings
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: rules
-- ------------------------------------------------------------
CREATE TABLE rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code TEXT UNIQUE NOT NULL,
    rule_version TEXT NOT NULL DEFAULT '1.0.0',
    logic_definition JSONB NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- ------------------------------------------------------------
-- Tabel: rule_evaluations
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: kpis
-- ------------------------------------------------------------
CREATE TABLE kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    entity_type TEXT,
    status TEXT NOT NULL DEFAULT 'PROPOSED',
    calculation_rule_id UUID REFERENCES rules(id) ON DELETE SET NULL,
    context_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- ------------------------------------------------------------
-- Tabel: scores
-- ------------------------------------------------------------
CREATE TABLE scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id UUID NOT NULL REFERENCES kpis(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    score_value NUMERIC NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    engine_source TEXT,
    context_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_scores_kpi ON scores(kpi_id);
CREATE INDEX idx_scores_entity ON scores(entity_type, entity_id);
CREATE INDEX idx_scores_calculated_at ON scores(calculated_at DESC);

-- ------------------------------------------------------------
-- Tabel: state_history
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: audit_log
-- ------------------------------------------------------------
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

-- ------------------------------------------------------------
-- Tabel: events
-- ------------------------------------------------------------
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name TEXT NOT NULL,
    target_object TEXT NOT NULL,
    target_object_id UUID NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_events_name_time ON events(event_name, created_at DESC);
