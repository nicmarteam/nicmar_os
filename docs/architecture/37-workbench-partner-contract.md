# Decizia 37 — Partner Workbench

Status: APPROVED (owner, 19 august 2026)

## 1. Context

Backend-ul Partner e complet și testat (Decizia 32): 4 endpoint-uri,
`PartnerEngine`/`PartnerAgent`, ownership verificat server-side. Dar
`apps/workbench/index.html` nu conține niciun cod Partner — verificat
explicit prin căutare (`grep -n "Partner"`), zero rezultate înainte de
această decizie. Liderul nu poate azi să creeze un partener, să
solicite un diagnostic, sau să vadă scoruri, din Workbench.

Decizia 37A (închisă, CI verde, 416/416) a expus `partner_id` în
`GET /api/v1/contacts`, eliminând blocajul care ar fi împiedicat acest
contract.

## 2. Scope

**Domeniu:** exclusiv `apps/workbench/index.html` (HTML/CSS/JS,
fișier unic, fără build step) + `tests/test_workbench_structure.py`.

**Explicit exclus — niciun cod backend nu se modifică:**
- `PartnerEngine`, `PartnerAgent`, `src/api/routers/partners.py`
- `src/api/schemas.py` (Partner*)
- Niciun endpoint nou, nicio schimbare de payload/response față de
  contractul deja implementat (16-partner-api-contract.md,
  32-partner-create-contract.md)

## 3. Sursă de adevăr pentru `partner_id` (regulă centrală)

`currentPartnerId` **nu e o sursă independentă persistentă**. Pentru
un contact deja convertit, sursa de adevăr este exclusiv
`contact.partner_id`, citit din `GET /api/v1/contacts` (Decizia 37A).

O variabilă runtime (`currentPartnerId`) există doar ca stare
tranzitorie de execuție curentă — populată fie din
`contact.partner_id` (contact deja convertit), fie din
`response.id` după `POST /partners` (creare nouă în aceeași sesiune).
Nu se citește din `localStorage`/`sessionStorage`/cookie — identic cu
regula deja aplicată la `currentContactId`/`currentConversationId`
(test existent: `test_nu_foloseste_local_storage`).

## 4. Flux condiționat pe `converted_to`

```
selectContact(contactId)
      │
      ├── (deja există, neschimbat) POST /conversations
      │
      └── NOU: citește converted_to + partner_id din obiectul
          contact deja primit de la loadContacts()
              │
              ├── converted_to !== "partner"
              │       → afișează zona „Creează partener”
              │       → ascunde Diagnostic/Send/Scores
              │
              └── converted_to === "partner"
                      → currentPartnerId = contact.partner_id
                      → ascunde „Creează partener”
                      → afișează Diagnostic/Send/Scores
```

După `POST /partners` reușit: `currentPartnerId = response.id`,
tranziție imediată către starea "partener creat" (Diagnostic/Send/
Scores), fără reîncărcare de pagină și fără al doilea apel către
`GET /contacts` doar pentru a re-obține `partner_id`-ul pe care
răspunsul de creare îl oferă deja.

## 5. Payload-uri exacte (identice cu backend-ul existent, nu se inventează câmpuri noi)

```js
// PARTNER_CREATE_PAYLOAD
{ contact_id: currentContactId }

// PARTNER_DIAGNOSTIC_PAYLOAD
{ diagnostic_type: <una din cele 4> }

// PARTNER_SEND_PAYLOAD
{ confirmed: true }

// GET /api/v1/partners/scores — fără body
```

**`diagnostic_type` — exact 4 valori fixe, hardcodate în UI ca
listă**, identice cu `VALID_DIAGNOSTIC_TYPES` din
`src/engines/partner/partner_engine.py`:
`ENCOURAGEMENT`, `CLARITY`, `APPRECIATION`, `NEXT_STEP`.
Nu se generează dinamic, nu există alt endpoint care le expune.

## 6. Reguli de securitate și onestitate față de lider (fixate de contract)

- **`owner_id` nu apare niciodată** în niciun payload trimis de
  Workbench — identic cu regula deja aplicată și testată
  (`test_owner_id_nu_apare_niciunde_in_fisier`). Identitatea vine
  exclusiv din headerul `Authorization: Bearer <token>`.
- Zona Partner e complet **inactivă/ascunsă** fără `currentContactId`
  selectat — nicio acțiune Partner nu e posibilă înaintea selectării
  unui contact (guard identic cu cel de la FollowUp,
  `test_are_guard_pentru_contact_si_conversation_la_creare_followup`).
- **Mesajul returnat de `/diagnostic` conține `[STUB]`** — Workbench-ul
  îl afișează ca atare, cuvânt cu cuvânt, plus o notă vizibilă lângă
  el (ex: "Mesaj generat automat — text fix, nu e generat de AI încă").
  Nu se ascunde, nu se reformulează pentru a părea un mesaj final.
- **Scorurile din `GET /partners/scores` sunt agregate pe owner, nu
  pe partenerul selectat** (limitare confirmată din cod,
  `PartnerAgent.get_recent_scores`, JOIN pe `owner_id` +
  `ORDER BY calculated_at DESC` + cel mai recent per metrică). UI-ul
  afișează explicit eticheta **"Scorurile tale cele mai recente"**,
  niciodată "Scorul lui {nume partener}" — ar induce în eroare
  liderul, dat fiind că API-ul nu poate azi filtra per-partener.

## 7. Coduri de eroare de gestionat explicit în UI (din teste HTTP existente)

| Acțiune | Cod | error_code | Mesaj UI |
|---|---|---|---|
| Create | 409 | `ALREADY_EXISTS` | Contactul e deja convertit — reîncarcă lista |
| Create/Diagnostic/Send | 403 | `ACCESS_DENIED` | Sesiune invalidă pentru acest partener |
| Diagnostic | 409 | `ALREADY_EXISTS` | Diagnostic deja generat azi pentru acest partener |
| Send | 400 | `CONFIRMATION_REQUIRED` | Bifează confirmarea înainte de trimitere |

Identic cu tiparul deja folosit la Objection (`renderConfirmResult`,
banner `error`/`block`/`info`) — reutilizăm `apiFetch()` existent,
care deja aruncă `Error` cu `.status`/`.errorCode` populate.

## 8. Criterii de acceptare (RED — teste structurale în `test_workbench_structure.py`)

Urmând exact convenția testelor existente (căutare de string/regex pe
conținutul HTML, nu execuție de browser):

1. `test_contine_endpoint_post_partners` — `"/api/v1/partners"` prezent ca string literal
2. `test_contine_endpoint_partner_diagnostic` — pattern pentru `/partners/${...}/diagnostic`
3. `test_contine_endpoint_partner_send` — pattern pentru `/partners/${...}/send`
4. `test_contine_endpoint_partner_scores` — `"/api/v1/partners/scores"` prezent
5. `test_partner_create_payload_contine_doar_contact_id` — payload-ul de creare conține exact `contact_id`, nimic altceva
6. `test_diagnostic_payload_contine_doar_diagnostic_type`
7. `test_send_payload_contine_doar_confirmed`
8. `test_cele_patru_diagnostic_types_prezente` — toate 4 valorile exacte (`ENCOURAGEMENT`, `CLARITY`, `APPRECIATION`, `NEXT_STEP`) apar ca string-uri în fișier
9. `test_partner_id_nu_e_citit_din_local_storage` — extensie a testului deja existent de `localStorage`, aplicat explicit și zonei noi
10. `test_owner_id_nu_apare_niciunde_in_fisier` — testul existent rămâne valabil, verificat că trece și după adăugarea codului Partner (regresie, nu test nou)
11. `test_zona_partner_ascunsa_fara_contact_selectat` — panoul Partner are clasa `disabled` implicit în markup, identic cu `panel-analyze`/`panel-followup`
12. `test_mesaj_stub_afisat_ca_atare` — textul `[STUB]` sau echivalentul apare tratat explicit în cod (nu filtrat/ascuns printr-un `.replace()`)
13. `test_eticheta_scoruri_nu_mentioneaza_partener_specific` — stringul folosit pentru afișarea scorurilor conține „cele mai recente" sau echivalent, nu „scorul acestui partener"

## 9. Ordinea de lucru (identică cu 37A)

```
contract (acest document)
   ↓
RED — teste structurale, toate eșuând din lipsă de cod
   ↓
GREEN — cod minim în index.html care satisface exact aceste teste
   ↓
regresie completă (416 + N teste noi, toate PASS)
   ↓
37 CLOSED
```

Nu se scrie cod UI înainte de RED.
