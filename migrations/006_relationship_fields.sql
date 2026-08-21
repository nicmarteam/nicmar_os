-- Migrare 006 — Construirea Listei de Relații (Decizia 47, Competența 18)
-- Sursă: docs/architecture/47-lista-relatii-contract.md
--
-- Toate coloanele NULLABLE — contactele existente rămân valide, zero
-- breaking change. NU se creează entitatea Relationship: o persoană =
-- un Contact, un singur traseu (contract 47, §2).

ALTER TABLE contacts ADD COLUMN relationship_category TEXT
    CHECK (relationship_category IN (
        'FAMILIE', 'PRIETENI', 'COLEGI', 'VECINI',
        'FOSTI_COLEGI', 'CUNOSTINTE', 'ALTA'
    ));

ALTER TABLE contacts ADD COLUMN relationship_level TEXT
    CHECK (relationship_level IN (
        'FOARTE_APROPIATA', 'BUNA', 'OCAZIONALA', 'DE_RELUAT'
    ));

-- Aproximare declarată de lider, NU timestamp — exact cum cere sursa
-- (Ecranul 5: "Astăzi / Săptămâna aceasta / ... / Nu îmi amintesc").
ALTER TABLE contacts ADD COLUMN last_contact_approx TEXT
    CHECK (last_contact_approx IN (
        'ASTAZI', 'SAPTAMANA_ACEASTA', 'LUNA_ACEASTA',
        'MAI_DEMULT', 'NU_IMI_AMINTESC'
    ));

ALTER TABLE contacts ADD COLUMN significant_context TEXT;

ALTER TABLE contacts ADD COLUMN perceived_interest TEXT
    CHECK (perceived_interest IN (
        'FOARTE_DESCHISA', 'PROBABIL', 'NU_STIU_INCA'
    ));
