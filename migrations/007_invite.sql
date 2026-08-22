-- Migrare 007 — INVITE (Decizia 48)
-- Sursă: docs/architecture/48-invite-contract.md
--
-- Principiu central (§6): INVITE este evenimentul de business.
-- MEETING este consecința programată a unei invitații acceptate.
-- Cele două stări sunt pe niveluri diferite și nu se confundă.

-- ------------------------------------------------------------------
-- INVITATIONS — faptul invitației, imutabil de la creare
-- ------------------------------------------------------------------
CREATE TABLE invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    frame TEXT NOT NULL CHECK (frame IN (
        'CAFEA', 'ZOOM', 'APEL', 'LIVE', 'ALTCEVA'
    )),
    purpose TEXT NOT NULL CHECK (purpose IN (
        'IDEE_NOUA', 'OPORTUNITATE', 'EXPERIENTA',
        'CONVERSATIE_PLACUTA', 'ALTCEVA'
    )),
    message_text TEXT NOT NULL,
    tone_used TEXT NOT NULL CHECK (tone_used IN ('CALDA', 'RELAXATA', 'DIRECTA')),
    sent_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_invitations_owner_sent ON invitations(owner_id, sent_at DESC);
CREATE INDEX idx_invitations_owner_contact ON invitations(owner_id, contact_id);

-- ------------------------------------------------------------------
-- INVITATION_OUTCOMES — reacția imediată, 0..1 per invitație.
-- UNIQUE garantează cardinalitatea la nivel de DB (tipar identic
-- outreach_outcomes, Decizia 46).
-- ------------------------------------------------------------------
CREATE TABLE invitation_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invitation_id UUID NOT NULL UNIQUE REFERENCES invitations(id) ON DELETE CASCADE,
    outcome TEXT NOT NULL CHECK (outcome IN (
        'ACCEPTED', 'POSTPONED', 'QUESTION_ASKED', 'OBJECTION', 'DECLINED'
    )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX idx_invitation_outcomes_owner_type
    ON invitation_outcomes(owner_id, outcome);

-- ------------------------------------------------------------------
-- MEETINGS — două modificări:
-- 1. CHECK pe status (azi lipsește — singura coloană de stare din
--    schemă fără restricție), Decizia 48 §6.A
-- 2. Legătura de proveniență către invitația acceptată.
--    ON DELETE SET NULL, nu CASCADE: ștergerea unei invitații nu
--    trebuie să șteargă o întâlnire reală (motivat identic cu
--    conversations.source_outreach_id, Decizia 46).
-- ------------------------------------------------------------------
ALTER TABLE meetings ADD CONSTRAINT meetings_status_check
    CHECK (status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED', 'RESCHEDULED'));

ALTER TABLE meetings ADD COLUMN source_invitation_id UUID
    REFERENCES invitations(id) ON DELETE SET NULL;
