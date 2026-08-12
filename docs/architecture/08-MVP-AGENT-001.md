# MVP-AGENT-001 — Arhitectura celor 4 Agenți MVP

**Status:** DRAFT VALIDAT — cele 4 puncte deschise confirmate de owner (v. secțiunea 4)
**Depinde de:** `06-harta-motoare-tehnice.md` (6 motoare MVP), `04-KPI-REG-001.md` (13 KPI)
**Notă de proveniență:** Conceptul de "Agent" nu are sursă primară confirmată în `02-business-objects-5-pillars.md` sau `05-competente-37-motor1.md` — provine din auditul de execuție (conversație). Contractul Human-in-the-loop, în schimb, **este confirmat masiv în sursa primară** (49 de puncte de confirmare explicită în cele 37 de competențe, sub principiul numit chiar în document "Legea Primului Pas" / "Legea Însoțirii").

---

## 1. Principiul fundamental — Human-in-the-loop (confirmat din sursă)

Documentul de 37 de competențe arată un tipar consecvent, repetat de 49 de ori: platforma **nu acționează niciodată autonom**. Propune (de obicei 2-3 variante), așteaptă un click explicit de confirmare, abia apoi trece la pasul următor. Exemplu direct din sursă (Competența 12): *"Am fixat direcția pentru prima săptămână, iar primul tău pas de astăzi este clar. Nu uita: mergem pas cu pas. Eu sunt aici la fiecare pas."*

**Regulă pentru toți cei 4 agenți:** niciun agent nu trimite mesaje, nu programează acțiuni și nu ia decizii în locul liderului/partenerului. Fiecare agent produce o **recomandare** + variante, omul confirmă, abia apoi acțiunea se înregistrează ca eveniment în sistem.

---

## 2. Cei 4 agenți

### Agent 1 — Contact Agent
- **Întrebare:** *"Pe cine merită să contactez astăzi?"*
- **Motoare sursă:** `CustomerRelationshipEngine`, `PartnerRelationshipEngine`
- **Input:** stare Contact/Client/Partner, ultima interacțiune, istoric, engagement, follow-up-uri restante, etapa relației
- **KPI relevanți:** CRH, PDI, PIP
- **Output:** listă prioritizată de contacte + motiv scurt pentru fiecare ("de ce azi, de ce el/ea")
- **Human-in-the-loop:** liderul vede lista, alege pe cine contactează, nimic nu se trimite automat

### Agent 2 — Conversation Agent (scope redus, confirmat Decizia 3)
- **Întrebare:** *"Ce îi spun?"*
- **Motoare sursă:** `ObjectionEngine` **(exclusiv)** — fără `PresentationEngine` (rămas post-MVP)
- **Input:** tipul preocupării/obiecției, istoricul conversației, etapa relației
- **KPI relevanți:** ORE
- **Output:** răspuns concret la o obiecție ridicată — **nu** generează prezentări sintetice de la zero (limitare explicită, Decizia 3)
- **Human-in-the-loop:** propune 2-3 variante de răspuns (aliniat cu tiparul din sursă — Competența 01: exact 3 variante: caldă, directă, bazată pe întrebare), liderul alege sau ajustează
- **Sursă de voce recomandată** (neconfirmată încă în arhitectură, decizie de-a ta): `Avatar_360.md` + `Limbajul_Avatarului.md`

### Agent 3 — FollowUp Agent
- **Întrebare:** *"Pe cine trebuie să urmăresc astăzi și ce fac?"*
- **Motor sursă:** `FollowUpEngine`
- **Input:** FollowUp-uri programate, timp scurs de la ultima interacțiune, Relationship Priority Score (RPS — metric confirmat în sursă, Competența FollowUp)
- **KPI relevanți:** DIS, RPS
- **Output:** listă de follow-up-uri de azi, ordonate după prioritate
- **Human-in-the-loop:** liderul confirmă fiecare follow-up înainte să fie marcat ca "realizat"

### Agent 4 — Mission Agent
- **Întrebare:** *"Care este următoarea acțiune concretă?"*
- **Motor sursă:** `MissionEngine`
- **Input:** Misiunea Zilei, progresul curent, disponibilitatea de timp
- **KPI relevanți:** DIS
- **Output:** un singur pas concret, executabil azi (aliniat cu "Legea Primului Pas" din sursă — un singur pas, nu o listă lungă)
- **Human-in-the-loop:** buton unic de confirmare ("Sunt gata, încep"), aliniat exact cu tiparul din Competența 12

---

## 3. Stratul comun — RuleEngine

Toți cei 4 agenți trec prin `RuleEngine` (v. Decizia 1, `06-harta-motoare-tehnice.md`) înainte de a produce recomandarea finală, conform fluxului deja stabilit în auditul de execuție:

```
Event → Engine → Rule → Data → Agent → Human → Action
```

`RuleEngine` decide *dacă* și *cum* se declanșează un agent (ex: praguri, condiții), agentul produce conținutul recomandării, omul confirmă, acțiunea devine eveniment.

---

## 4. Decizii confirmate (12 august 2026)

1. **Sursa de voce pentru Conversation Agent — confirmată.** `Avatar_360.md` + `Limbajul_Avatarului.md` devin sursa oficială de ton pentru toate răspunsurile generate de Conversation Agent. Această legătură nu are (încă) corespondent explicit în `05-competente-37-motor1.md`, dar e acum decizie validată de owner, nu presupunere.

2. **Ordinea de construcție — confirmată.** Contact Agent → Conversation Agent → FollowUp Agent → Mission Agent, ca prim vertical slice complet funcțional, conform planului din auditul de execuție inițial.

3. **Numărul de agenți — 4 pentru MVP, explicit provizoriu.** Owner-ul confirmă: *"acum 4 agenți, dar vor fi mult mai mulți agenți"*. Cei 4 nu sunt o limită arhitecturală, ci punctul de plecare al vertical slice-ului MVP. Extinderea ulterioară e așteptată, nu excepțională — probabil unul per motor din cele 13 rămase post-MVP (`07-motoare-post-mvp.md`), pe măsură ce fiecare motor intră în scope.

---

## 5. Hartă orientativă pentru extindere viitoare (neconfirmată, doar pregătitoare)

Pe măsură ce motoarele din `07-motoare-post-mvp.md` intră în scope, fiecare pare să aibă un agent-pereche natural — **listă informativă, nu decizie**:

| Motor post-MVP | Agent-pereche probabil |
|---|---|
| PresentationEngine | Presentation Agent |
| ObjectionEngine *(deja MVP)* | *(deja acoperit de Conversation Agent)* |
| PartnerOnboardingEngine | Onboarding Agent |
| PartnerIntegrationEngine | Integration Agent |
| MentorGuidanceEngine | Mentor Agent |
| TeamCoordinationEngine | Team Agent |
| LeadershipDevelopmentEngine | Leadership Agent |
| HabitEngine | Habit Agent |
| DailyRhythmEngine | Rhythm Agent |
| PriorityEngine | Priority Agent |
| ResilienceEngine | Resilience Agent |
| ExperienceLibraryEngine | Experience Agent |
| PerformanceEvaluationEngine / AutonomyEngine | Performance/Autonomy Agent (probabil orchestrator, nu agent operațional) |

Aceasta e doar o observație structurală, de păstrat pentru referință — fiecare intrare trebuie tratată cu același rigoare (verificare surse, decizie explicită) ca cei 4 agenți actuali, nu implementată automat pe baza acestui tabel.

---
*Document DRAFT. Necesită confirmare pe cele 3 puncte deschise înainte de trecerea la implementare.*
