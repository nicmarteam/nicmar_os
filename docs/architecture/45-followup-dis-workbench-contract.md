# Decizia 45 — FollowUp DIS → Workbench

Status: APPROVED (owner, 19 august 2026)

## 1. Context

Auditul direct din cod (traseu complet producer → persistență →
API → schema → UI → teste) confirmă: backend-ul pentru DIS-FollowUp e
complet și funcțional — `FollowUpEngine._record_dis_score()`,
`FollowUpAgent.get_recent_dis_score()`, `GET /api/v1/followups/dis-score`,
schema `DisScoreResponse` (reutilizată identic de la Mission). **Zero
gap tehnic pe acest traseu.**

Singurul gap real e strict API→UI: Workbench-ul nu apelează deloc
acest endpoint, deși e testat și funcțional. Spre deosebire de ORE
(Decizia 44, blocată prin lipsă de definiție), DIS are deja un
placeholder aprobat explicit (Decizia 38, pentru Mission) — extinderea
la FollowUp reutilizează exact același placeholder deja acceptat,
pentru o a doua sursă a aceluiași KPI, deja corect izolată prin
`entity_type`. Nu se inventează nimic nou.

Auditul a mai descoperit două goluri minore, incluse acum:
- Testul structural existent (`test_contine_endpoint_dis_score`)
  verifică doar `/api/v1/missions/dis-score`, nu și pe cel de FollowUp
- Nu există test HTTP dedicat de izolare owner pentru
  `GET /followups/dis-score` (izolarea e garantată de filtrul SQL,
  dar netestată explicit la acest nivel, spre deosebire de toate
  celelalte endpoint-uri mutante din proiect)

## 2. Scope

**Domeniu:**
- `apps/workbench/index.html` — afișare nouă, zonă Performance
- `tests/test_workbench_structure.py` — test structural nou
- `tests/test_followup_api.py` — test de izolare owner nou

**Explicit exclus — niciun cod deja validat nu se modifică:**
- Formula DIS, `FollowUpEngine`, `FollowUpAgent`
- Tabela `scores`, schema `DisScoreResponse`
- Endpoint-ul `GET /api/v1/followups/dis-score` (folosit ca atare)
- DIS Mission — panoul existent rămâne neatins
- ORE — neatins, rămâne `BLOCKED BY DEFINITION`

## 3. Plasament — zona Performance, DIS Mission și DIS FollowUp alăturate

```
PERFORMANCE
┌───────────────────────┐  ┌─────────────────────────┐
│ DIS — Misiuni          │  │ DIS — Follow-up-uri     │
│ Valoare operațională   │  │ Valoare operațională    │
│ curentă                │  │ curentă                 │
│        1.0             │  │         1.0             │
└───────────────────────┘  └─────────────────────────┘
```

Motiv (verbatim din decizia aprobată): utilizatorul trebuie să
înțeleagă imediat că vede **două surse ale aceluiași KPI**, nu doi
KPI diferiți. Etichetele — `DIS — Misiuni` / `DIS — Follow-up-uri` —
și formularea discretă `Valoare operațională curentă` evită
prezentarea lui `1.0` ca scor sofisticat deja calculat.

Panoul existent `mission-dis-box` (buton "Vezi DIS-ul tău cel mai
recent") se extinde/reorganizează în această zonă comună — fără să
schimbe comportamentul lui, doar plasarea vizuală alături de noul
panou FollowUp.

## 4. Apel API — payload și consumer

```js
// GET fără body, identic structural cu loadDisScore() existent
const result = await apiFetch("/api/v1/followups/dis-score", { method: "GET" });
```

Consumă `DisScoreResponse{dis_score: Optional[float]}` — identic cu
Mission, niciun câmp nou.

## 5. Criterii de acceptare (RED)

1. `test_contine_endpoint_followups_dis_score` — `"/api/v1/followups/dis-score"` prezent ca string literal în `index.html`
2. `test_dis_followup_afisat_separat_de_dis_mission` — eticheta `"DIS — Follow-up-uri"` prezentă și distinctă de `"DIS — Misiuni"` (ambele string-uri exacte, verificabile separat)
3. `test_dis_followup_foloseste_method_get` — apelul către `/api/v1/followups/dis-score` folosește explicit `method: "GET"` (verificare extrasă din bloc, nu doar prezența URL-ului — tipar identic cu testul `/present` de la Mission)
4. `test_owner_a_vede_exclusiv_dis_score_propriu` — **HTTP + PostgreSQL real**: liderul A creează un follow-up (DIS scris), liderul B apelează `GET /followups/dis-score`, primește `None` (nu vede DIS-ul lui A)
5. `test_owner_b_vede_exclusiv_dis_score_propriu` — companion invers, închide golul de izolare identificat la audit

Criteriul `owner_id` absent din fișier rămâne acoperit de testul deja
existent — regresie, nu test nou.

## 6. Ordinea de lucru

```
contract (acest document)
   ↓
RED — 5 teste, toate eșuând din lipsă de implementare
   ↓
GREEN — cod minim în index.html, care satisface exact aceste teste
   ↓
regresie completă (463 + 5, toate PASS)
   ↓
45 CLOSED
```

Nu se scrie cod de implementare înainte de RED. Formula DIS, producer-ul
FollowUp, DIS Mission și ORE rămân complet neatinse pe tot parcursul.
