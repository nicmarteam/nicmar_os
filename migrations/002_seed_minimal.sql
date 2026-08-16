-- ============================================================
-- NicMar OS — Migration 002: Seed minimal
-- ============================================================
-- Scop: date minime necesare ca vertical slice-urile (Mission,
-- FollowUp, Partner) sa functioneze pe PostgreSQL real.
-- Sursa: 04-KPI-REG-001.md (cei 13 KPI), cele 3 reguli deja
-- implementate in cod (rule_engine.py), un utilizator de test.
-- Nu se inventeaza KPI, reguli sau utilizatori suplimentari.
-- ============================================================

-- ------------------------------------------------------------
-- 1. Cei 13 KPI oficiali, exact din 04-KPI-REG-001.md
-- ------------------------------------------------------------
INSERT INTO kpis (metric_code, name, status) VALUES
    ('DIS', 'Daily Impact Score', 'PROPOSED'),
    ('CRH', 'Customer Relationship Health', 'PROPOSED'),
    ('PDI', 'Partner Development Index', 'PROPOSED'),
    ('PIP', 'Partner Integration Progress', 'PROPOSED'),
    ('OAS', 'Onboarding Activation Success', 'PROPOSED'),
    ('ERI', 'Experience Reuse Index', 'PROPOSED'),
    ('LRI', 'Leadership Readiness Index', 'PROPOSED'),
    ('MEI', 'Mentoring Effectiveness Index', 'PROPOSED'),
    ('TDI', 'Team Development Index', 'PROPOSED'),
    ('AMS', 'Autonomy Maturity Score', 'PROPOSED'),
    ('PES', 'Presentation Effectiveness Score', 'PROPOSED'),
    ('ORE', 'Objection Resolution Effectiveness', 'PROPOSED'),
    ('OPI', 'Overall Performance Index', 'PROPOSED');

-- ------------------------------------------------------------
-- 2. Cele 3 reguli folosite efectiv de vertical slice-urile
--    implementate (RuleEngine — rule_engine.py). Doar acestea 3,
--    nu toate exemplele ilustrative din 03-rule-model-001.md.
-- ------------------------------------------------------------
INSERT INTO rules (rule_code, rule_version, logic_definition, is_active) VALUES
    (
        'RULE-MISSION-DAILY-001',
        '1.0.0',
        '{"description": "owner_id are < 1 misiune activa azi -> MISSION_READY, altfel MISSION_BLOCKED", "implemented_in": "src/engines/rule/rule_engine.py:evaluate_mission_readiness"}'::jsonb,
        TRUE
    ),
    (
        'RULE-FOLLOWUP-DUPLICATE-001',
        '1.0.0',
        '{"description": "conversation_id fara follow_up PENDING -> FOLLOWUP_READY, altfel FOLLOWUP_DUPLICATE", "implemented_in": "src/engines/rule/rule_engine.py:evaluate_followup_readiness"}'::jsonb,
        TRUE
    ),
    (
        'RULE-PARTNER-DIAGNOSTIC-001',
        '1.0.0',
        '{"description": "partner_id fara diagnostic azi -> PARTNER_READY, altfel PARTNER_ALREADY_DIAGNOSED (asumptie explicita, v. Partner Contract 1.2)", "implemented_in": "src/engines/rule/rule_engine.py:evaluate_partner_diagnostic_readiness"}'::jsonb,
        TRUE
    );

-- ------------------------------------------------------------
-- 3. Utilizator de test — un singur lider, pentru testare manuala
--    pe PostgreSQL real (nu inlocuieste testele automate stateful,
--    care folosesc UUID-uri generate dinamic).
-- ------------------------------------------------------------
INSERT INTO users (email, full_name, role) VALUES
    ('test.lider@nicmar.local', 'Lider de Test', 'LEADER');

-- ------------------------------------------------------------
-- 4. Date minime Mission / FollowUp / Partner — NU se insereaza
--    aici. Motiv: fiecare din cele 3 vertical slice-uri isi
--    genereaza propriile date prin Engine (generate_mission,
--    create_from_trigger, generate_diagnostic), care trec prin
--    RuleEngine si validare — a insera direct in tabele ar
--    ocoli exact logica pe care am testat-o azi. Testarea pe
--    PostgreSQL real foloseste codul, nu date pre-inserate.
-- ------------------------------------------------------------
