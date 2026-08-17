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

## DECIZIA 3 — Folosirea textelor canonice / variante generate

**Status:** ⏳ NEÎNCEPUTĂ

---

## DECIZIA 4 — Regula pentru situații sensibile / excluderi de siguranță

**Status:** ⏳ NEÎNCEPUTĂ

---

## DECIZIA 5 — Cifre de venit / disclaimer obligatoriu

**Status:** ⏳ NEÎNCEPUTĂ
