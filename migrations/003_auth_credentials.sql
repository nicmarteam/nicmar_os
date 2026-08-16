-- ============================================================
-- NicMar OS — Migration 003: Auth Credentials
-- ============================================================
-- Adaugă minim necesar pentru autentificare email+parolă.
--
-- DECIZIE DE DESIGN (explicită, nu implicită):
-- password_hash este NULLABLE, nu NOT NULL.
--
-- Motiv: 002_seed_minimal.sql și toate cele 107 teste existente
-- (Mission/FollowUp/Partner, unitare + integrare + API) creează
-- utilizatori prin INSERT INTO users fără password_hash — sunt
-- folosiți direct ca owner_id în teste de Engine/Agent, nu prin
-- login real. NOT NULL ar rupe retroactiv toată suita validată
-- până acum. Un utilizator cu password_hash NULL nu se poate
-- autentifica prin /auth/login (verificat explicit în cod, nu
-- doar presupus) — dar rămâne valid ca owner_id pentru restul
-- sistemului, exact ca până acum.
-- ============================================================

ALTER TABLE users ADD COLUMN password_hash TEXT;
