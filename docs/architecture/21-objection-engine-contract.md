# OBJECTION ENGINE — IMPLEMENTATION CONTRACT v1

**Status:** verificat față de cele 5 decizii confirmate în `21-objection-engine-decizii-preliminare.md` (17 august 2026), `08-MVP-AGENT-001.md`, `06-harta-motoare-tehnice.md` (Decizia 2, MVP), `02-business-objects-5-pillars.md`, `05-competente-37-motor1.md` (flux `04_Raspuns_La_O_Obiectie`), schema DB (`001_initial_schema.sql` + `004_objection_response_columns.sql`).
**Precedent:** aceeași disciplină ca `11`/`12`/`13`/`19`/`20` — verificare explicită DECLARAT vs. EXISTĂ, TDD strict, izolare `owner_id` testată, fără cod înainte de contract.

---

## 0. Ce e `ObjectionEngine` v1 — scop strict (Decizia 1)

`ObjectionEngine` primește textul liber al unei obiecții, îl clasifică (dacă se poate, determinist) într-una din categoriile eligibile, oferă 3 variante de răspuns din Biblioteca Experienței, acceptă editarea liderului, validează textul final pentru siguranță, și persistă rezultatul.

**Nu pretinde acces la** `RelationshipEngine`, `Motorul Identității`, `CustomerRelationshipEngine`, `PartnerRelationshipEngine` — toate absente din cod, confirmat. Arhitectura țintă (`Objection → Relationship + Identity + Customer/Partner context → răspuns`) rămâne pentru o versiune ulterioară.

**v1 executabil:** `Objection → Biblioteca Experienței → răspuns`

---

## 1. Fluxul complet, capăt la capăt

```
1. Input: text liber al obiecției (objection_text)
2. Clasificare deterministă (clasifier.py, deja implementat, 17/17 teste GREEN)
   → categorie din cele 6 eligibile, SAU None (fără potrivire)
3. Dacă None: liderul alege manual categoria din cele 13 din Bibliotecă
4. Motorul oferă 3 variante (Caldă / Directă / Întrebare) din
   biblioteca-experientei-variante-v1.md, pentru categoria stabilită
5. Liderul alege o variantă și, opțional, o editează
6. Safety Validation (Decizia 4 + Decizia 5) rulează pe response_text final
   → PASS: continuă la pasul 7
   → BLOCK: respins, liderul trebuie să editeze din nou
   → PARTIAL VALIDATION / HUMAN REVIEW: semnalat, dar nu blocat
7. Persistare: response_text + response_variant_used (varianta de ORIGINE,
   neschimbată de editare) în tabela objections
```

---

## 2. Clasificare (Decizia 2)

### 2.1 Cele 6 categorii eligibile pentru clasificare automată
`PRET`, `TIMP`, `INCREDERE_STRUCTURA`, `FAMILIE_SUPORT`, `AMANARE`, `FRICA_TEHNOLOGIE` — deja implementate în `src/engines/objection/classifier.py`, verificate GREEN (17 teste unitare, cuvinte-cheie exclusiv din citate reale confirmate în audit).

### 2.2 Restul categoriilor (7)
`FRICA_ESEC`, `FRICA_VORBIT`, `NU_CUNOSC_OAMENI`, `VULNERABILITATE_IZOLARE`, `IMAGINE_SOCIALA`, `NU_VREAU_VANZARE`, `PIATA_SATURATA` — rămân în Bibliotecă, disponibile prin **selecție manuală** de către lider, nu prin clasificare automată (acoperire insuficientă de sursă, confirmat prin audit).

### 2.3 `VULNERABILITATE_IZOLARE` — gate suplimentar
Nu se declanșează automat, nici măcar dacă liderul o selectează direct fără o confirmare explicită suplimentară ("ești sigur/ă că vrei să folosești acest răspuns acum?") — v. `biblioteca-experientei-v1-CONSOLIDAT.md`, secțiunea 3.

### 2.4 `NEINCREDERE_PRODUS` — eliminată permanent
Nu există, nu poate fi selectată, nu poate fi returnată de niciun mecanism — eliminată din lista oficială (Decizia 2), nesusținută de nicio sursă reală.

---

## 3. Biblioteca Experienței — sursa de conținut (Decizia 1, Decizia 3)

Sursă: `biblioteca-experientei-variante-v1.md` — 39 de texte (3 variante × 13 categorii), verificate ca fiind curate (fără cifre de venit, fără tipare excluse). **Nu** tabela `objections` — aceea stochează doar instanțe de obiecții, nu conținut de bibliotecă.

Cele 3 variante per categorie: **`CALDA`** (înțelegătoare), **`DIRECTA`** (scurtă, la obiect), **`INTREBARE`** (deschide dialogul cu o întrebare).

---

## 4. Persistare — schema DB (Decizia 3)

```sql
-- Existent (001_initial_schema.sql):
objections(id, owner_id, conversation_id, objection_category, objection_text,
           resolution_status, created_at, updated_at)

-- Adăugat (004_objection_response_columns.sql, executat, verificat pe PostgreSQL real):
objections.response_text          TEXT  -- text final trimis (editat sau nu)
objections.response_variant_used  TEXT  -- 'CALDA' | 'DIRECTA' | 'INTREBARE', origine, NU se schimbă la editare
```

Ambele coloane `NULLABLE` — o obiecție poate exista fără răspuns încă trimis.

**Regulă strictă:** `response_variant_used` reflectă mereu varianta de la care s-a PORNIT, indiferent de câte modificări a făcut liderul asupra `response_text`. Nu există valoare `'EDITATA'` — ar pierde informația de origine, necesară pentru analiza ulterioară ("variantele CALDA generează mai multe continuări?"), posibilă sursă pentru `ORE`.

---

## 5. Safety Validation (Decizia 4 + Decizia 5)

### 5.1 Model pe 3 niveluri
- **BLOCK** — răspunsul nu poate fi persistat/trimis, punct.
- **PARTIAL VALIDATION** — semnalat, dar nu blocat (acoperire parțială, cunoscută ca atare).
- **HUMAN REVIEW** — semnalat pentru verificare umană explicită, nu blocat automat.

### 5.2 Mecanisme, per categorie de risc

| Excludere | Nivel | Mecanism v1 |
|---|---|---|
| Promisiuni nerealiste/garantare rezultate | BLOCK | Cuvinte-cheie: "garantat", "sigur", "100%" |
| Presiune financiară | BLOCK | Cuvinte-cheie: "trebuie să investești acum", "prețul crește" |
| "Trebuie să decizi acum" | BLOCK | Cuvinte-cheie: "acum sau niciodată", "doar azi", "ultima șansă" |
| Exploatarea vulnerabilităților | BLOCK | Listă derivată din audit real (`biblioteca-experientei-v1-CONSOLIDAT.md`, secțiunea 4) |
| **Cifre de venit fără disclaimer (Decizia 5)** | **BLOCK** | Detectare (valoare numerică + monedă + context financiar) → necesită prezența exactă a disclaimer-ului |
| Presiune/manipulare emoțională generală | PARTIAL VALIDATION | Aceeași listă combinată — nu detectează manipulare subtilă neprevăzută |
| Afirmații false/neverificabile | PARTIAL VALIDATION | Listă de afirmații cunoscute problematice din audit — nu verificare generală de adevăr |
| Ascunderea informațiilor | PARTIAL VALIDATION | Doar pe `INCREDERE_STRUCTURA`: răspunsul trebuie să conțină confirmare directă ("da" + termen MLM/companie) |
| Devierea de la răspunsul onest | PARTIAL VALIDATION | Extins acolo unde există exemplu concret din audit |
| Inventarea de testimoniale/dovezi | HUMAN REVIEW | Marcaje suspecte ("studii arată", "conform...") → semnalare |
| Ocolirea refuzului explicit al prospectului | HUMAN REVIEW | Pe `objection_text` curent (refuz clar) vs. markeri de insistență în răspuns — fără istoric de conversație |

**Declarație explicită de limitare (obligatorie în orice comunicare despre acest sistem):** *"Sistemul nu revendică detectarea deterministă a riscurilor care necesită înțelegere semantică, verificarea adevărului factual sau context conversațional istoric. Orice limitare identificată rămâne explicit documentată și nu este prezentată ca protecție completă."*

### 5.3 Regula specifică Decizia 5 (disclaimer venituri)

**Detectare:** valoare numerică + monedă (`lei`/`RON`/`euro`/`EUR`) + context financiar (`venit`/`câștig`/`câștiguri`/`lunar`/`pe lună`/`an`/`pe an`).
**Disclaimer obligatoriu:** *"Rezultatele variază de la persoană la persoană și nu sunt garantate."*
**Mesaj la BLOCK:** *"Textul conține o afirmație privind venituri fără disclaimerul obligatoriu."*
**Regulă Human-in-the-loop:** motorul **NU adaugă automat** disclaimerul — liderul îl scrie el însuși. Motorul doar verifică prezența lui.

---

## 6. Ce NU face `ObjectionEngine` v1

- Nu generează text liber (fără LLM în v1, confirmat Decizia 1)
- Nu are acces la istoricul relației, identitate, context client/partener
- Nu verifică adevărul afirmațiilor dincolo de o listă cunoscută
- Nu urmărește istoricul conversației dincolo de `objection_text` curent
- Nu adaugă automat disclaimere — doar le verifică
- Nu declanșează nicio tranziție de stare pe `Conversation` (acel Business Object rămâne în afara scope-ului, legat de `ConversationAgent`, neconstruit încă)

---

## 7. Criterii de acceptare și teste obligatorii

### 7.1 Clasificare (deja acoperit)
- [x] 17/17 teste GREEN pe `classifier.py` — cele 6 categorii eligibile, text neconcludent → `None`, insensibil la majuscule, `NEINCREDERE_PRODUS` niciodată returnată.

### 7.2 Bibliotecă + selecție variante
- [ ] Pentru fiecare din cele 13 categorii, motorul poate returna exact 3 variante (`CALDA`/`DIRECTA`/`INTREBARE`)
- [ ] Categorie inexistentă (ex. `NEINCREDERE_PRODUS`) → eroare explicită, nu excepție ascunsă
- [ ] `VULNERABILITATE_IZOLARE` necesită confirmare suplimentară explicită înainte de a fi oferită

### 7.3 Persistare
- [ ] `response_text` se salvează corect, editat sau nu
- [ ] `response_variant_used` rămâne varianta de ORIGINE, chiar dacă `response_text` e editat ulterior
- [ ] Izolare `owner_id` — un lider nu poate persista/citi obiecțiile altui lider

### 7.4 Safety Validation — BLOCK
- [ ] Text cu "garantat"/"sigur"/"100%" → BLOCK
- [ ] Text cu presiune financiară → BLOCK
- [ ] Text cu urgență artificială → BLOCK
- [ ] Text cu tipare de exploatare a vulnerabilității (din audit) → BLOCK
- [ ] Text cu cifră de venit FĂRĂ disclaimer → BLOCK
- [ ] Text cu cifră de venit CU disclaimer exact → PASS
- [ ] Text cu cifră ce NU e financiară (ex. "Programul durează 15 zile") → PASS, fără fals-pozitiv

### 7.5 Safety Validation — PARTIAL VALIDATION / HUMAN REVIEW
- [ ] Aceste niveluri semnalează, dar NU blochează persistarea
- [ ] `INCREDERE_STRUCTURA` fără confirmare directă → semnalat (PARTIAL VALIDATION)
- [ ] Marcaje de testimonial suspect → semnalat (HUMAN REVIEW)

### 7.6 PostgreSQL real
- [ ] Toate cele de mai sus, repetate pe PostgreSQL real (tiparul `TestContactAgentOnRealPostgres`)

### 7.7 Regresie completă
- [ ] Toate testele existente (179, confirmate azi) rămân verzi

---

## 8. Lista exactă a lucrurilor care rămân pentru o versiune ulterioară

1. **`RelationshipEngine`, `Motorul Identității`, `CustomerRelationshipEngine`, `PartnerRelationshipEngine`** — toate declarate arhitectural, neimplementate
2. **LLM pentru generare/clasificare** — infrastructură existentă (`ProviderFactory`, `UnifiedLLMService`), neconectată, exclusă explicit din v1
3. **Cele 7 categorii fără clasificare automată** — rămân doar cu selecție manuală, până la material sursă suficient
4. **Verificare generală de adevăr** — imposibilă determinist, ar necesita LLM sau proces uman
5. **Istoric de conversație pentru "ocolirea refuzului"** — necesită `ConversationAgent`, neconstruit
6. **`Biblioteca Întrebărilor`** — concept menționat în `05`, distinct de Biblioteca Experienței, neconstruit
7. **Opțiunea "Construim una împreună"** din UX-ul sursă — necesită fie LLM, fie un flux de completare ghidată, neconstruit în v1

---
*Contract consolidat din cele 5 decizii confirmate progresiv (17 august 2026), fiecare cu sursă, fapt verificat, și decizie explicită a owner-ului — nicio secțiune nu reprezintă presupunere tehnică nedeclarată.*
