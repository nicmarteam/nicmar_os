# Decizia 46A — Workbench Prospectare Relațională

Status: PROPUNERE DE CONTRACT (owner, 20 august 2026). Bazat pe
Decizia 46 (backend, 494/494 PASSED) și audit direct al Workbench-ului
existent.

## 1. Obiectiv

> Liderul intră în Workbench și vede clar pe cine poate reactiva / cui
> poate cere o recomandare, apoi execută acțiunea — în 30-60 de
> secunde.

**46A nu e "soluția pentru recrutare".** E prima piesă utilizabilă din
fundația construită la Decizia 46 — face vizibil și acționabil un
mecanism care azi există doar ca API.

## 2. Scope

**Domeniu:** exclusiv `apps/workbench/index.html` +
`tests/test_workbench_structure.py`.

**Explicit exclus — zero modificare backend:**
- `OutreachEngine`, `src/api/routers/outreach.py`, `schemas.py`
- Migrarea `005`, orice tabelă
- Mission, Priority, KPI, ORE
- Celelalte panouri existente (Contact, FollowUp, Partner, Objection)

## 3. Decizie luată — varianta (a), cu precizare

**Liderul scrie mesajul. Workbench-ul îi oferă contextul și următorul
pas.**

Respins explicit: 3 variante fixe hardcodate în frontend — ar fi cod
care *mimează* inteligența pe care vrem s-o construim ulterior, real,
prin `src/llm/` (azi deconectat, confirmat prin audit).

Dar nici formular gol. **NICMAR e ajutorul din spate: arată contextul,
liderul gândește, înțelege și decide.** Concret, panoul afișează,
înainte de scrierea mesajului:

- cine este persoana (`full_name`)
- de ce apare acum în lista de acțiuni (`reason` — deja calculat de
  `ContactAgent`, zero backend nou)
- ce relație există deja (`status`, `converted_to`)
- ce s-a întâmplat ultima dată (`last_followup_at`,
  `last_followup_status`)
- dacă e recomandare sau reactivare (`purpose` ales de lider)

**Toate aceste câmpuri există deja** în `GET /api/v1/contacts`
(`ContactSummaryResponse`) — confirmat prin audit. Nu se adaugă
nimic în backend.

Generarea inteligentă de mesaj adaptat persoanei aparține unei etape
ulterioare, când există `persoană → context → canal → nevoie → limbaj
→ invitație → răspuns` — atunci `src/llm/` va avea un rol real.

## 4. Comportament

```
Login
   ↓
panel-outreach activ (independent de currentContactId, ca Mission/Priority)
   ↓
Lider alege: 🤝 Cer o recomandare | 🔄 Reactivez o relație
   ↓
Alege contactul din listă (GET /api/v1/contacts, deja existent)
   ↓
NICMAR AFIȘEAZĂ CONTEXTUL PERSOANEI:
   nume · de ce apare acum (reason) · status relație ·
   ultimul follow-up · dacă e deja partener
   ↓
Alege tonul (CALDA / RELAXATA / DIRECTA) — etichetă, nu generator
   ↓
Liderul scrie mesajul (el decide ce spune)
   ↓
"Am trimis mesajul" → POST /api/v1/outreach
   ↓
"Ce răspuns ai primit?" → 5 opțiuni
   ↓
POST /api/v1/outreach/{id}/outcome
   ↓
Dacă răspunsul conține conversation_id → mesaj clar:
   "Conversație deschisă — continuă din panoul Contact"
```

## 5. Criterii de acceptare (RED — teste structurale)

1. `test_contine_endpoint_post_outreach` — `"/api/v1/outreach"` prezent
2. `test_contine_endpoint_outreach_outcome` — pattern `/outreach/${...}/outcome`
3. `test_outreach_create_payload_campuri_exacte` — payload conține exact `contact_id`, `purpose`, `message_text`, `tone_used`; fără `owner_id`
4. `test_outcome_payload_contine_doar_outcome` — payload conține exact `outcome`
5. `test_ambele_purposes_prezente` — `REFERRAL` și `REACTIVATION` apar ca valori exacte
6. `test_toate_cele_5_outcomes_prezente` — toate 5 valorile din contractul 46
7. `test_cele_3_tonuri_prezente` — `CALDA`, `RELAXATA`, `DIRECTA`
8. `test_zona_outreach_activa_dupa_login` — `id="panel-outreach"`, `class="panel disabled"`, activat în `login()`
9. `test_conversation_id_din_outcome_afisat_liderului` — răspunsul cu `conversation_id` produce un mesaj vizibil, nu e ignorat silențios
10. `test_contextul_persoanei_afisat_inainte_de_mesaj` — codul citește explicit `reason`, `status` și `last_followup_status` pentru afișare (NICMAR arată contextul, nu doar un formular gol — §3)

Criteriul `owner_id` absent din fișier — acoperit de testul existent.

## 6. Ordinea de lucru

```
contract (acest document) + confirmare punct §3
        ↓
RED (9 teste structurale)
        ↓
GREEN (panel-outreach în index.html)
        ↓
regresie completă (494 + 9)
        ↓
CI
        ↓
verificare independentă
```
