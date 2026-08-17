# Decizii preliminare — Contract 21 (`ObjectionEngine`)

**Status:** jurnal de decizii, NU e Contract 21. Contractul se scrie abia după ce toate cele 5 decizii sunt închise.
**Metodă:** pentru fiecare decizie — sursă → fapt verificat → ce lipsește → decizia owner-ului → consemnare.

---

## DECIZIA 1 — Scope-ul `ObjectionEngine` v1 — ✅ CONFIRMATĂ (17 august 2026)

### Sursă
`02-business-objects-5-pillars.md` (Event Catalog Conversation), `06-harta-motoare-tehnice.md` (secțiunea `ObjectionEngine`, Decizia 2), `04-KPI-REG-001.md`.

### Fapt verificat
1. `Objection` nu e Business Object independent — generat automat dintr-o tranziție `Conversation.Resolved`, via `WF-OBJECTION-CREATE-001`.
2. Inputuri declarate oficial pentru `ObjectionEngine`: tipul preocupării, istoricul relației, `Motorul Identității`, `CustomerRelationshipEngine`, `PartnerRelationshipEngine`.
3. Toate cele 4 dependințe (`RelationshipEngine`, `Motorul Identității`, `CustomerRelationshipEngine`, `PartnerRelationshipEngine`) — **absente din cod**.
4. `ObjectionEngine` e motor MVP oficial confirmat (Decizia 2, `06`).
5. Tabela `objections` din DB stochează **instanțe** de obiecții ridicate (owner_id, conversation_id, objection_category, objection_text, resolution_status) — **nu conține conținut de bibliotecă/răspunsuri**. Nedemonstrat că e sursă de conținut.

### Decizia owner-ului (formulare confirmată)

> **ObjectionEngine v1 va procesa obiecția și va selecta/construi răspunsul folosind exclusiv informațiile disponibile în Biblioteca Experienței și contextul direct al obiecției.**
>
> În v1, motorul nu va pretinde că are acces la istoricul relației, Motorul Identității, CustomerRelationshipEngine sau PartnerRelationshipEngine, deoarece aceste dependințe nu sunt implementate. Aceste dependințe rămân parte din arhitectura țintă și pot extinde motorul într-o versiune ulterioară.

**Arhitectura țintă** (post-v1): `Objection → Relationship + Identity + Customer/Partner context → răspuns`
**v1 executabil** (confirmat acum): `Objection → Biblioteca Experienței → răspuns`

**Notă reținută explicit:** tabela `objections` NU e sursa principală de conținut pentru v1 — sursa e `biblioteca-experientei-v1-CONSOLIDAT.md` (sau succesorul ei validat). Rămâne de stabilit (Decizia 2) mecanismul exact prin care motorul citește/potrivește conținutul din Bibliotecă.

---

## DECIZIA 2 — Mecanismul de potrivire obiecție ↔ categorie din Bibliotecă — ✅ CONFIRMATĂ (17 august 2026)

### Sursă
`05-competente-37-motor1.md` (flux `04_Raspuns_La_O_Obiectie`), audit de acoperire pe toate cele ~24 fișiere sursă (inclusiv `Recrutare_si_Obiectii_NicMar.md`, omis inițial din verificare, corectat).

### Fapt verificat
1. UX-ul sursă cere detecție automată din text liber ("Analizează obiecția").
2. Confirmă exact 3 variante de răspuns + opțiune "Construim una împreună".
3. Acoperirea reală de formulări/sinonime per categorie e **inegală** — verificată explicit prin extragere de citate reale din surse, nu presupusă.

### Audit de acoperire (rezultat, cu dovadă din surse)

| Categorie | Acoperire | Verdict pentru v1 |
|---|---|---|
| `PRET` | ✅ bună | Eligibilă clasificare automată |
| `TIMP` | ✅ bună | Eligibilă clasificare automată |
| `INCREDERE_STRUCTURA` | ✅ foarte bună | Eligibilă clasificare automată |
| `FAMILIE_SUPORT` | ✅ bună | Eligibilă clasificare automată |
| `AMANARE` | ✅ bună | Eligibilă clasificare automată |
| `FRICA_TEHNOLOGIE` | ✅ bună | Eligibilă clasificare automată |
| `FRICA_ESEC` | 🟡 limitată | Rămâne în Bibliotecă, NU eligibilă automat în v1 |
| `FRICA_VORBIT` | 🟡 limitată | Rămâne în Bibliotecă, NU eligibilă automat în v1 |
| `NU_CUNOSC_OAMENI` | 🟡 limitată | Rămâne în Bibliotecă, NU eligibilă automat în v1 |
| `VULNERABILITATE_IZOLARE` | 🟡 alt tip de sursă (context, nu obiecție-citat) | Tratată separat — nu e obiecție standard |
| `IMAGINE_SOCIALA` | 🔴 insuficientă | Rămâne în Bibliotecă, NU eligibilă automat |
| `NU_VREAU_VANZARE` | 🔴 insuficientă | Rămâne în Bibliotecă, NU eligibilă automat |
| `PIATA_SATURATA` | 🔴 insuficientă | Rămâne în Bibliotecă, NU eligibilă automat |
| `NEINCREDERE_PRODUS` | 🔴 **neconfirmată din nicio sursă** | **SCOASĂ din lista oficială de categorii** — a fost inferată de mine, nu extrasă din material real |

### Decizia owner-ului (confirmată, în 2 niveluri)

**Nivel 1 — Mecanism general:** clasificare deterministă pe cuvinte/expresii-cheie (Opțiunea A), NU selecție manuală uniformă, NU LLM în v1 — consistent cu Decizia 1.

**Nivel 2 — Eligibilitate:** clasificarea automată se aplică **doar** celor 6 categorii cu acoperire bună (`PRET`, `TIMP`, `INCREDERE_STRUCTURA`, `FAMILIE_SUPORT`, `AMANARE`, `FRICA_TEHNOLOGIE`). Restul (7 categorii + `VULNERABILITATE_IZOLARE` tratată separat) rămân documentate în Bibliotecă, dar **nu sunt ținte ale clasificării automate în v1** — nu se inventează acoperire care nu există în sursă.

**Regulă generală reținută:** numărul de categorii oficiale nu e fixat dinainte — rezultă din ce sursele pot susține demonstrabil, nu din câte au fost propuse inițial în document.

**Consecință tehnică pentru `objections.objection_category`:** `CHECK` constraint-ul, dacă se introduce, ar trebui să acopere toate cele 13 categorii rămase (14 minus `NEINCREDERE_PRODUS`), dar doar 6 sunt "clasificabile automat" — diferența trebuie reflectată explicit în contract (ex. un flag sau o listă separată `AUTO_CLASSIFIABLE_CATEGORIES`).

---

## DECIZIA 3 — Folosirea textelor canonice / variante generate — ✅ CONFIRMATĂ (17 august 2026)

### Sursă
`05-competente-37-motor1.md`, pașii 4 ("Construirea") și 5 ("Autenticitatea") din fluxul `04_Raspuns_La_O_Obiectie`.

### Fapt verificat
1. Sursa numește explicit 3 stiluri distincte: **Caldă și înțelegătoare**, **Scurtă și directă**, **Bazată pe o întrebare de deschidere**.
2. Pasul 5 cere explicit editare de către lider înainte de trimitere ("Hai să schimbăm câteva cuvinte").
3. Tabela `objections` nu avea niciun câmp pentru a stoca răspunsul trimis — doar `objection_text` (ce a spus prospectul).

### Decizia owner-ului (confirmată)
1. **3 variante distincte (caldă/directă/întrebare) pentru toate cele 13 categorii** din Bibliotecă (nu doar cele 6 eligibile automat) — 39 de texte în total.
2. **Motorul acceptă și persistă text editat de lider** — extinde scope-ul `ObjectionEngine` de la strict READ-ONLY (ca `ContactAgent`) la READ+WRITE limitat.
3. **Separare explicită de roluri, în schema DB:** `response_variant_used` păstrează varianta de ORIGINE (`CALDA`/`DIRECTA`/`INTREBARE`), nu e suprascrisă la editare — doar `response_text` se schimbă. Motiv: permite analiză ulterioară ("variantele CALDA generează mai multe continuări?"), posibilă sursă pentru `ORE`.

### Migrație executată (schimbare de arhitectură, aprobată explicit înainte de execuție)
```sql
-- migrations/004_objection_response_columns.sql
ALTER TABLE objections
    ADD COLUMN response_text TEXT,
    ADD COLUMN response_variant_used TEXT;
```
Verificat: mecanismul real de migrare din repo (fără ORM, SQL brut aplicat secvențial via `psql -f`, convenție `NNN_descriere.sql`, pas explicit adăugat în CI). Rulată pe PostgreSQL local, confirmată structural. Regresie completă: **179/179, 0 failed**.

### Conținut livrat
Cele 39 de texte (3 variante × 13 categorii) — `biblioteca-experientei-variante-v1.md`, scrise respectând toate excluderile de siguranță deja stabilite (secțiunea 4, `biblioteca-experientei-v1-CONSOLIDAT.md`). `VULNERABILITATE_IZOLARE` include nota de uz restricționat direct în text.

---

## DECIZIA 4 — Regula pentru situații sensibile / excluderi de siguranță — ✅ CONFIRMATĂ (17 august 2026)

### Sursă
Cele 10 excluderi propuse de owner + auditul de conținut deja făcut (`biblioteca-experientei-v1-CONSOLIDAT.md`, secțiunea 4 — exploatare vulnerabilitate; `Pașii_de_bază_afacerii.docx` — evitare răspuns direct).

### Verificare de precedent
`RuleEngine` existent — verificat, **nu e o potrivire**: evaluează reguli structurale de creare de entități (Mission/FollowUp/Partner), nu validare de conținut text. Nu se reutilizează.

### Decizia owner-ului (verdict final)

> **ObjectionEngine v1 utilizează mecanisme tehnice distincte pentru cele 10 categorii de excluderi de siguranță. Nivelul de acoperire este diferențiat între BLOCK, PARTIAL VALIDATION și HUMAN REVIEW. Sistemul nu revendică detectarea deterministă a riscurilor care necesită înțelegere semantică, verificarea adevărului factual sau context conversațional istoric. Orice limitare identificată rămâne explicit documentată și nu este prezentată ca protecție completă.**

### Mecanisme confirmate, per categorie de excludere

| Excludere | Nivel | Mecanism |
|---|---|---|
| Promisiuni nerealiste/garantare rezultate | **BLOCK** | Listă cuvinte-cheie interzise ("garantat", "sigur", "100%") |
| Presiune financiară | **BLOCK** | Listă cuvinte-cheie ("trebuie să investești acum", "prețul crește") |
| "Trebuie să decizi acum" | **BLOCK** | Listă cuvinte-cheie ("acum sau niciodată", "doar azi", "ultima șansă") |
| Exploatarea vulnerabilităților | **BLOCK** | Listă derivată din auditul real (secțiunea 4, Bibliotecă) |
| Presiune/manipulare emoțională generală | **PARTIAL VALIDATION** | Aceeași listă combinată — prinde tipare cunoscute, nu manipulare subtilă neprevăzută |
| Afirmații false/neverificabile | **PARTIAL VALIDATION** | Listă de afirmații cunoscute problematice din audit — nu verificare generală de adevăr |
| Ascunderea informațiilor | **PARTIAL VALIDATION** | Doar pe `INCREDERE_STRUCTURA`: răspunsul trebuie să conțină confirmare directă |
| Devierea de la răspunsul onest | **PARTIAL VALIDATION** | Același mecanism, extins unde există exemplu concret din audit |
| Inventarea de testimoniale/dovezi | **HUMAN REVIEW** | Marcaje suspecte ("studii arată", "conform...") → semnalare, nu blocaj automat |
| Ocolirea refuzului explicit al prospectului | **HUMAN REVIEW** | Verificare pe `objection_text` curent (refuz clar) vs. markeri de insistență în răspuns — fără istoric de conversație |

**Comportament confirmat:** `BLOCK` → răspunsul nu poate fi persistat/trimis. `PARTIAL VALIDATION` și `HUMAN REVIEW` → nu blochează, doar semnalează pentru verificare umană înainte de trimitere.

---

## DECIZIA 5 — Cifre de venit / disclaimer obligatoriu — ✅ CONFIRMATĂ (17 august 2026)

### Sursă
`Planul_de_20_minute.docx`, `Planul_de_5_minute_bun.docx` — cifre de venit fără disclaimer. Cele 39 de texte canonice verificate: **curate, zero cifre de venit** — regula operează exclusiv pe `response_text` (text final, posibil editat de lider), nu necesită modificarea Bibliotecii.

### Regula (formulare finală, precizată de owner)

Dacă `response_text` conține **o afirmație identificabilă privind venituri sau rezultate financiare** (nu orice cifră — ex. "Programul durează 15 zile" nu se califică), sistemul verifică disclaimerul obligatoriu:

> „Rezultatele variază de la persoană la persoană și nu sunt garantate."

**Detectare v1:** combinație de (valoare numerică) + (monedă: lei/RON/euro/EUR) + (context financiar: venit/câștig/câștiguri/lunar/pe lună/an/pe an).

**Nivel:** `BLOCK` — nu se poate persista fără disclaimer.

**Flux:** Editare lider → Safety Validation → detectare afirmație financiară → verificare disclaimer → PASS/BLOCK. Mesaj la blocare: *"Textul conține o afirmație privind venituri fără disclaimerul obligatoriu."*

**Regulă Human-in-the-loop explicită:** sistemul **nu adaugă automat** disclaimerul — liderul trebuie să-l scrie el însuși. Păstrează clar ce a fost efectiv scris și trimis de lider.

---

## Toate cele 5 decizii — ÎNCHISE (17 august 2026)

| Decizie | Status |
|---|---|
| 1 — Scope v1 | ✅ |
| 2 — Clasificare | ✅ |
| 3 — Bibliotecă + persistare | ✅ |
| 4 — Safety exclusions | ✅ |
| 5 — Income disclaimer | ✅ |

**Următorul pas:** `21-objection-engine-contract.md` — contractul tehnic final, consolidând toate cele 5 decizii.
