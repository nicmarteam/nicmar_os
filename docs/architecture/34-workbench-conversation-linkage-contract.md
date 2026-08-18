# DECIZIA 34 — WORKBENCH CONVERSATION LINKAGE — CONTRACT

**Status:** confirmat de owner — UI integration strictă peste backend-ul Deciziei 33
(398/398 GREEN, verificat pe server HTTP real). Verificat direct din `apps/workbench/index.html`
și `tests/test_workbench_structure.py` — nu din memorie.

**Descoperire confirmată din audit**: `index.html` trimite azi `conversation_id: null`,
hardcodat (linia 463), și nu apelează niciodată `/api/v1/contacts` sau
`/api/v1/conversations`. Backend-ul e complet, UI-ul e izolat de el.

---

## 1. Scope strict — ce se schimbă și ce NU

**Se schimbă**: doar `apps/workbench/index.html`. Zero cod Python, zero endpoint nou, zero
schimbare de contract API (Decizia 33 rămâne exact cum e).

**NU construim acum**: follow-up automat, WhatsApp, Mission UI, Partner UI, istoric conversații,
editare contact, CRM complet.

**O completare minimă, necesară pentru testabilitate reală, dincolo de lista explicită**:
un formular minim "Contact nou" (doar `full_name`), pentru că altfel un lider nou-înregistrat,
cu zero contacte, n-ar putea parcurge fluxul deloc — criteriul de acceptare cere "contactele
apar → selectez Contact A", ceea ce presupune fie contacte pre-existente (nerealist pentru un
cont nou), fie un mecanism minim de a crea unul. Nu e "Contact editing" (modificare a unui
contact existent) — e strict creare, un singur câmp, deja acoperit de `POST /api/v1/contacts`
existent (Decizia 31).

## 2. Structura nouă a paginii

### 2.1 Zonă nouă — "Contact & Conversație" (între Login și Faza 1)

- La login reușit: apelează automat `GET /api/v1/contacts`, afișează lista ca butoane
  selectabile (nume + status), la fel stilistic ca lista de categorii existentă
- Sub listă: formular minim "Contact nou" — un `<input>` (`full_name`) + buton — apelează
  `POST /api/v1/contacts`, apoi reîncarcă lista
- La selectarea unui contact: apelează `POST /api/v1/conversations` cu `contact_id`, primește
  `conversation_id`, îl reține în stare (`currentConversationId`)
- **Faza 1 (Analiză) rămâne dezactivată** până la existența unui `currentConversationId` —
  la fel cum Faza 1 era dezactivată până la login, acum e dezactivată până la conversație

### 2.2 Faza 1-3 — neschimbate structural

Doar `prepareOptions()` se modifică: `conversation_id: null` → `conversation_id:
currentConversationId`.

## 3. Stare JS nouă (variabile, memorie runtime, nimic persistat)

```javascript
let currentContactId = null;
let currentConversationId = null;
```

## 4. Convenție de testabilitate nouă — marcaj `PREPARE_PAYLOAD`

Identic cu `CONFIRM_PAYLOAD_START/END` (Decizia 27): construcția payload-ului pentru
`/objections/prepare` se delimitează explicit:

```javascript
// PREPARE_PAYLOAD_START
const preparePayload = {
  objection_text: currentObjectionText,
  objection_category: currentCategory,
  conversation_id: currentConversationId,
};
// PREPARE_PAYLOAD_END
```

Testul structural verifică STRICT, în interiorul acestui bloc: `"null"` (ca valoare literală
pentru `conversation_id`) **absent**, `"currentConversationId"` **prezent**.

## 5. Endpoint-uri noi folosite (deja existente, din Decizia 33 — zero cod backend nou)

```
GET  /api/v1/contacts       — listă contacte
POST /api/v1/contacts       — creare contact minimă (doar full_name)
POST /api/v1/conversations  — creare/obținere conversație pentru un contact
```

## 6. Testarea — Nivel 1 (structural) + Nivel 2 (server real)

**Nivel 1 — teste noi în `test_workbench_structure.py`:**
- conține `/api/v1/contacts`, `/api/v1/conversations` ca string-uri literale la apeluri
  `apiFetch`
- blocul `PREPARE_PAYLOAD_START/END` există; conține `currentConversationId`; NU conține
  `"conversation_id: null"` (verificare literal, nu doar cuvântul `null` oriunde în fișier —
  `null` apare legitim în alte verificări JS, ex. `=== null`)
- `owner_id` — rămâne absent din tot fișierul (regresie, verificată din nou)

**Nivel 2 — server HTTP real, flux vizual echivalent** (aceeași limitare documentată la
Decizia 27: fără browser real conectat, simulăm exact payload-urile pe care JS-ul le trimite):

```
register → login (simulat)
    ↓
GET /contacts → listă goală
    ↓
POST /contacts {full_name} → contact nou
    ↓
GET /contacts → contactul apare
    ↓
selectez contactul → POST /conversations {contact_id} → conversation_id primit
    ↓
scriu obiecția → POST /objections/prepare {conversation_id: <cel real>}
    ↓
verificare DB: objection.conversation_id == conversation_id
```

Testul negativ (Leader B) **nu se repetă** — deja demonstrat la Decizia 33, la nivel de API;
această decizie verifică doar că UI-ul chiar folosește mecanismul corect, nu re-testează
securitatea backend-ului.

## 7. Criteriul de acceptare final

```
Login → Workbench → contactele apar → selectez Contact A → se creează Conversation A
    → Workbench reține conversation_id → scriu obiecția → prepare → conversation_id = A
    → verificat din DB: objection.conversation_id == conversation.id
```

După acest criteriu confirmat, harta devine:

```
Register → Login → Contacts → Conversation → Workbench → Objection   TOATE VERZI, UI INCLUS
```
