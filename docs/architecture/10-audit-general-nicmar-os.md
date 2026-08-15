# AUDIT GENERAL NicMar OS — Document de Referință

**Status:** OFICIAL — reconstruit integral din surse, verificat linie cu linie în repo
**Data:** 12 august 2026
**Metodologie:** Repo → sursă → verificare → matrice → verdict → concluzie (nu conversație → memorie → rezumat)
**Înlocuiește:** orice audit general anterior bazat pe rezumat din conversație — acelea rămân draft de orientare, nu SSOT

---

## 1. Scopul proiectului

NicMar OS e sistemul de operare AI pentru liderii Metodei NicMar — un partener digital care observă relațiile, prioritizează, pregătește acțiunea, propune, iar liderul confirmă. Principiul central, confirmat din `docs/living-vision/00_Manifest_NicMar.md` și `01_Caracter_NicMar_OS.md`: **omul înaintea tehnologiei**, testat prin întrebarea *"Dacă nu îl ajută pe om, nu îl construim."*

Bucla operațională: **observă → analizează → prioritizează → pregătește → propune → omul confirmă → sistemul înregistrează → KPI se actualizează → următoarea acțiune devine mai bună.**

---

## 2. Business Objects — 9, verificate

```sql
users, contacts, clients, partners, conversations, missions, follow_ups, objections, meetings
```
Verificat: `09-MVP-DATA-001.md`, 9 tabele canonice + 7 de suport = 16 total (v. secțiunea 5).

---

## 3. State Machines — verificate, cu subseturi MVP explicite

| Business Object | Stări Core | Subset MVP |
|---|---|---|
| Contact | 7 (New→Managed→Archived) | 4 (`NEW, ACTIVE, CONVERTED, ARCHIVED`) |
| Partner | 8 (Activated→Mentor→Archived) | 3 (`ACTIVATED, ACTIVE, ARCHIVED`) |
| Client | 7 (Converted→Reactivated→Archived) | 3 (`CONVERTED, ACTIVE, ARCHIVED`) |
| Mission | 7 (Generated→Skipped/Expired→Archived) | 4 (`GENERATED, ASSIGNED, IN_PROGRESS, COMPLETED`) |
| Conversation | 7 (Initiated→Closed→Archived) | 6 (`INITIATED, ACTIVE, WAITING, FOLLOWUP_NEEDED, RESOLVED, ARCHIVED`) |
| Meeting, Objection, FollowUp | — fără State Machine dedicată în Core (obiecte operaționale secundare) | — |

`MissionReassigned` — clarificat ca operațiune laterală (schimbă `owner_id`/`partner_id`), nu tranziție de stare.

---

## 4. Motoare — 18 confirmate în Core, 6 în MVP

**MVP (verificat, `06-harta-motoare-tehnice.md`):**
```
MissionEngine, FollowUpEngine, CustomerRelationshipEngine,
PartnerRelationshipEngine, RuleEngine, ObjectionEngine
```

**Corecție importantă:** `RelationshipEngine` — Primary Engine real pentru Contact și Conversation în Core — **nu e printre cele 6**. Rămâne capacitate READ-ONLY, folosită de Contact Agent (Decizia P6), nu motor complet.

**`PriorityEngine`** — dependință funcțională reală (Partner Agent, FollowUpEngine, MissionGenerated), dar rămâne post-MVP ca motor complet; acoperit prin "Priority capability" la nivel de Agent (Decizia P11), aplicată explicit doar la Partner Agent — Mission Agent nu are încă aceeași notă (observație deschisă, nu gaură).

**Clasificate, excluse din MVP:** `ContinuityEngine` (contradicție `02`/`05`, investigat), `NotificationEngine` (infrastructură transversală), `AuditEngine` (redundant cu `audit_log`).

**12 motoare rămase, documentate pregătitor:** `07-motoare-post-mvp.md`.

---

## 5. Date — 16 tabele, v1.3

**9 Business Objects** + **7 tabele de suport**: `rules`, `rule_evaluations`, `kpis`, `scores`, `state_history`, `audit_log`, `events`.

FK-uri cheie: `scores.kpi_id → kpis.id`, `kpis.calculation_rule_id → rules.id`.

**Corecții aplicate azi:** `conversations.status` cu `FOLLOWUP_NEEDED` recuperat; `follow_ups.status` cu `CHECK` complet (`PENDING, COMPLETED, POSTPONED, RESCHEDULED`); `kpis`+`scores` adăugate (rezolvă G4 — persistența transversală a KPI).

---

## 6. Agenți — 5, verificați

| # | Agent | Motor sursă | KPI |
|---|---|---|---|
| 1 | Contact Agent | `RelationshipEngine` (READ-ONLY) + `CustomerRelationshipEngine`/`PartnerRelationshipEngine` (context) | CRH, PDI, PIP |
| 2 | Conversation Agent | `ObjectionEngine` (scope redus, fără `PresentationEngine`) | ORE |
| 3 | FollowUp Agent | `FollowUpEngine` | DIS, (RPS — scor operațional, nu KPI) |
| 4 | Mission Agent | `MissionEngine` | DIS |
| 5 | Partner Agent | `PartnerRelationshipEngine` + Priority capability | PDI, PIP |

Toți respectă Human-in-the-loop — confirmat din sursă (49 de puncte explicite în `05`, "Legea Primului Pas"). Partner Agent are dublu HITL (direcție emoțională + confirmare mesaj).

---

## 7. KPI — 13 oficiali, verificați complet

```
DIS, CRH, PDI, PIP, OAS, ERI, LRI, MEI, TDI, AMS, PES, ORE, OPI
```
12 operaționali + `OPI` (strategic, compozit). `RPS` — reclasificat explicit ca **scor operațional** (ordonează o listă acum), nu KPI (măsoară performanța în timp) — regulă arhitecturală nouă, utilă pentru orice metrică viitoare.

---

## 8. Micro-lanțuri verificate cap-coadă

| Lanț | Rezultat | Găuri descoperite |
|---|---|---|
| Contact → FollowUp | ✅ complet | G1 (contradicție internă `02`), G2 (RPS), G3 (`follow_ups` schema) — toate închise |
| Partner | ✅ complet | G4 (persistență KPI lipsă) — închis, rezolvat transversal pentru toți cei 13 |
| Mission | ✅ complet | doar observație de consecvență (`PriorityEngine` la Mission Agent) |

---

## 9. FOLLOW-UP rămas (nedecis, nu ignorat)

1. **Meeting** — fără proprietar tehnic (motor/agent), decizie explicită de scop redus
2. **`PriorityEngine`** complet — post-MVP
3. **Consecvență Mission Agent** — dacă primește aceeași notă de "Priority capability" ca Partner Agent
4. **KPI-MODEL-001** — formulele exacte (praguri, ponderi) încă nedefinite pentru toți cei 13

---

## 10. Ce nu există încă — cod

**Zero implementare.** `src/` conține doar `runtime/` (observabilitate AI, sesiuni, timeline) și `llm/` — nimic din `engines/`, `agents/`, `rules/` nu are cod. Tot ce e în acest document e specificație verificată, nu software funcțional.

---

## 11. Poziția reală

Arhitectura MVP e coerentă, verificată transversal din surse primare, nu din memorie: Business Objects, State Machines, Events, 6 Engines, 5 Agents, 13 KPI, 16 tabele — toate cu trasabilitate confirmată. Următoarea etapă majoră: transformarea acestei specificații în cod executabil, prin vertical slices, testate dincolo de happy path (timeout, date lipsă, refuz uman, retry).

---
*Document canonic. Reconstruit integral din `docs/architecture/00-09`, verificat prin comenzi directe în repo, nu din rezumat conversațional.*
