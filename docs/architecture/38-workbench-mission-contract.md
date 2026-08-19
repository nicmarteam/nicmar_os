# Decizia 38 — Mission Workbench

Status: APPROVED (owner, 19 august 2026)

## 1. Context

Backend-ul Mission e complet și testat: 6 endpoint-uri,
`MissionEngine`/`MissionAgent`, ownership verificat server-side
(`Security Isolation Audit`, 12 august 2026). Dar `apps/workbench/index.html`
nu conține niciun cod Mission — verificat explicit prin căutare
(`grep -n "mission\|Mission\|MISSION"`), zero rezultate înainte de
această decizie.

Spre deosebire de Partner (Decizia 37), Mission **nu depinde de
`currentContactId`**: coloanele `contact_id`/`partner_id`/`client_id`/
`scheduled_at` există în tabela `missions` (`ON DELETE SET NULL`,
opționale), dar nu sunt citite/scrise nicăieri în `MissionEngine`,
`MissionAgent`, router sau schemas — verificat explicit, zero
rezultate. Sunt `DECLARAT ARHITECTURAL`, nu `EXISTĂ` funcțional.
Mission e legată strict de `owner_id`.

## 2. Scope

**Domeniu:** exclusiv `apps/workbench/index.html` + `tests/test_workbench_structure.py`.

**Explicit exclus — niciun cod backend nu se modifică:**
- `MissionEngine`, `MissionAgent`, `src/api/routers/missions.py`
- `src/api/schemas.py` (Mission*, PresentMissionResponse, DisScoreResponse)
- Niciun endpoint nou, nicio schimbare de payload/response

## 3. Plasament — panou la nivel de lider, nu de contact

Panoul Mission e activ imediat după autentificare, **independent de
`currentContactId`** — nu așteaptă selecția unui contact, spre
deosebire de Partner/FollowUp/Objection. Devine `disabled` doar
înainte de login, la fel ca `panel-contact`, dar se activează direct
în `login()`, nu în `selectContact()`.

Separare conceptuală (confirmată de audit, nu presupusă):
```
CONTACT   → relația cu oamenii  → Conversation → Objection → FollowUp → Partner
MISSION   → execuția liderului  → ce fac azi → execut → completez → DIS
```

## 4. Cele 6 endpoint-uri — metode exacte (verificate din router, nu presupuse)

| Endpoint | Metodă | Body | Response |
|---|---|---|---|
| `/api/v1/missions` | POST | `{title}` | `{id, owner_id, title, status}` |
| `/api/v1/missions/{id}/assign` | POST | — | `MissionResponse` |
| `/api/v1/missions/{id}/present` | **GET** | — | `{text}` |
| `/api/v1/missions/{id}/start` | POST | `{confirmed}` | `MissionResponse` |
| `/api/v1/missions/{id}/complete` | POST | — | `MissionResponse` |
| `/api/v1/missions/dis-score` | GET | — | `{dis_score}` |

**Atenție explicită:** `/present` e `GET`, nu `POST` — diferit de
tiparul Objection/Partner. `CreateMissionRequest` conține **doar**
`title` (fără `description`, deși engine-ul îl acceptă intern ca
parametru opțional — router-ul nu-l expune, deci Workbench-ul nu-l
trimite).

## 5. Mașina de stări — sursă de adevăr pentru UI

```
GENERATED → ASSIGNED → IN_PROGRESS → COMPLETED
```

Din `_ALLOWED_TRANSITIONS` (`mission_engine.py`): drum unic, fără
sărituri, fără întoarcere. `COMPLETED` e stare finală.

**Regula UI (butoane condiționate strict de `status`-ul curent):**

| Stare curentă | Acțiuni disponibile |
|---|---|
| *(nicio misiune azi)* | Generează misiune |
| `GENERATED` | Assign, Present |
| `ASSIGNED` | Present, Start (+ confirmare) |
| `IN_PROGRESS` | Complete |
| `COMPLETED` | — (afișează DIS-ul cel mai recent) |

„Misiunea de azi" — formulare păstrată intenționat în UI, pentru că
reflectă direct regula de unicitate din backend
(`RULE-MISSION-DAILY-001`, verificată prin `MissionNotReadyError` →
`409 ALREADY_EXISTS` dacă owner_id are deja o misiune activă azi).

## 6. Payload-uri exacte

```js
// MISSION_CREATE_PAYLOAD
{ title: <text> }

// MISSION_START_PAYLOAD
{ confirmed: true }

// assign, complete — fără body
// present, dis-score — GET, fără body
```

## 7. Reguli de securitate și onestitate față de lider

- **`owner_id` nu apare niciodată** în niciun payload trimis de
  Workbench — identic cu regula deja aplicată la Objection/FollowUp/
  Partner (`test_owner_id_nu_apare_niciunde_in_fisier`, regresie,
  nu test nou). Identitatea vine exclusiv din `Authorization: Bearer`.
- **`DIS-score` e agregat pe owner, nu pe misiunea curentă** —
  confirmat din cod (`MissionAgent.get_recent_dis_score`,
  `JOIN missions m ON... WHERE m.owner_id = %s ORDER BY calculated_at
  DESC LIMIT 1` — cel mai recent DIS din toate misiunile). UI-ul
  afișează explicit eticheta **„DIS-ul tău cel mai recent"**,
  niciodată „DIS-ul acestei misiuni" — identică ca justificare cu
  eticheta scorurilor Partner (contract 37, secțiunea 6).
- **Confirmarea umană pentru Start** e obligatorie — `confirmed: true`
  trimis explicit doar după bifarea unui checkbox, identic cu tiparul
  de la Partner Send.

## 8. Coduri de eroare de gestionat explicit în UI

| Acțiune | Cod | error_code | Mesaj UI |
|---|---|---|---|
| Create | 409 | `ALREADY_EXISTS` | Ai deja o misiune activă azi |
| Assign/Present/Start/Complete | 403 | `ACCESS_DENIED` | Sesiune invalidă pentru această misiune |
| Assign/Start/Complete | 400 | `INVALID_TRANSITION` | Această acțiune nu e posibilă în starea curentă |
| Start | 400 | `CONFIRMATION_REQUIRED` | Bifează confirmarea înainte de a începe |

## 9. Criterii de acceptare (RED — teste structurale)

Urmând convenția deja stabilită (căutare de string/regex pe HTML,
markeri `_PAYLOAD_START`/`_END`, `panel disabled id="panel-..."`):

1. `test_contine_endpoint_post_missions` — `"/api/v1/missions"` prezent
2. `test_contine_endpoint_mission_assign` — template `/missions/${...}/assign`
3. `test_contine_endpoint_mission_present` — template `/missions/${...}/present`, verificat ca GET (nu POST) în apelul `apiFetch`
4. `test_contine_endpoint_mission_start` — template `/missions/${...}/start`
5. `test_contine_endpoint_mission_complete` — template `/missions/${...}/complete`
6. `test_contine_endpoint_dis_score` — `"/api/v1/missions/dis-score"` prezent
7. `test_mission_create_payload_contine_doar_title` — payload creare conține exact `title`, fără `description`/`owner_id`
8. `test_mission_start_payload_contine_doar_confirmed` — payload Start conține exact `confirmed`, fără `owner_id`
9. `test_zona_mission_activa_dupa_login_nu_dupa_contact` — panoul are `id="panel-mission"`, activat în funcția `login()`, nu în `selectContact()`
10. `test_butoane_mission_conditionate_de_status` — cele 4 stări (`GENERATED`, `ASSIGNED`, `IN_PROGRESS`, `COMPLETED`) apar ca valori verificate explicit în cod (`===` sau `switch`), nu doar ca text
11. `test_eticheta_dis_nu_mentioneaza_misiunea_curenta` — eticheta conține „cele mai recente" sau „DIS-ul tău", nu „DIS-ul acestei misiuni"
12. `test_owner_id_nu_apare_niciunde_in_fisier` — regresie, testul deja existent trebuie să rămână verde

## 10. Ordinea de lucru (identică cu 37)

```
contract (acest document)
   ↓
RED — teste structurale, toate eșuând din lipsă de cod
   ↓
GREEN — cod minim în index.html care satisface exact aceste teste
   ↓
regresie completă (428 + N teste noi, toate PASS)
   ↓
38 CLOSED
```

Nu se scrie cod UI înainte de RED.
