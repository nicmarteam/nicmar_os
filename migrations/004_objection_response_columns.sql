-- ============================================================
-- NicMar OS — Migration 004: Objection Response Columns
-- ============================================================
-- Adaugă coloanele necesare pentru persistarea răspunsului
-- liderului la o obiecție (Decizia 3, ObjectionEngine v1,
-- confirmată de owner 17 august 2026 — v.
-- 21-objection-engine-decizii-preliminare.md).
--
-- DECIZIE DE DESIGN (explicită, nu implicită):
-- response_variant_used păstrează varianta de ORIGINE a
-- răspunsului (CALDA / DIRECTA / INTREBARE), nu e suprascrisă
-- dacă liderul editează textul.
--
-- Motiv: separă explicit "ce a spus prospectul" (objection_text,
-- existent) de "ce a trimis efectiv liderul" (response_text, nou)
-- de "de unde a pornit răspunsul" (response_variant_used, nou).
-- Editarea de către lider modifică DOAR response_text —
-- response_variant_used rămâne varianta aleasă inițial, ca să
-- rămână posibilă analiza ulterioară de tipul "răspunsurile
-- pornite din varianta CALDA au generat mai multe continuări ale
-- conversației?" — informație care poate alimenta KPI ORE, fără
-- să se piardă originea răspunsului editat.
--
-- Ambele coloane sunt NULLABLE: o obiecție poate exista fără
-- răspuns încă trimis (resolution_status = 'OPEN'), la fel cum
-- password_hash e NULLABLE în 003 pentru utilizatori fără login
-- real — pattern deja stabilit în acest proiect.
-- ============================================================

ALTER TABLE objections
    ADD COLUMN response_text TEXT,
    ADD COLUMN response_variant_used TEXT;
