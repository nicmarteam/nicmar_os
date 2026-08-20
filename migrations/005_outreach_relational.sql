-- Migrare 005 — Prospectare Relaționala (Decizia 46)
-- Sursă: docs/architecture/46-prospectare-relationala-contract.md

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

CREATE INDEX idx_outreach_owner_sent ON outreach_attempts(owner_id, sent_at DESC);
CREATE INDEX idx_outreach_owner_contact ON outreach_attempts(owner_id, contact_id);

CREATE TABLE outreach_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    outreach_id UUID NOT NULL UNIQUE REFERENCES outreach_attempts(id) ON DELETE CASCADE,
    outcome TEXT NOT NULL CHECK (
        outcome IN ('QUESTION_ASKED', 'HESITATION', 'WILL_RESPOND_LATER',
                    'REFERRAL_RECEIVED', 'POSITIVE_RESPONSE')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_outreach_outcomes_owner_type ON outreach_outcomes(owner_id, outcome);

ALTER TABLE conversations ADD COLUMN source_outreach_id UUID
    REFERENCES outreach_attempts(id) ON DELETE SET NULL;
