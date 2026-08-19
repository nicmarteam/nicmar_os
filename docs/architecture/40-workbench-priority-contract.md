# Decizia 40 — Priority Workbench

Status: APPROVED (owner, 19 august 2026)

## 1. Context

`GET /api/v1/priority` există complet, testat (447/447 PASSED, confirmat
independent la închiderea Deciziei 39): fără body, fără parametri,
`current_user.id` din JWT, returnează `List[PrioritizedActivityResponse]`
— maximum 5 elemente, deja sortate de `PriorityEngine`, câmpuri
`entity_type`, `entity_id`, `title`, `impact`, `urgency`,
`vechime_seconds`. Zero cod Priority în `apps/workbench/index.html` —
verificat, Decizia 39 nu a atins Workbench-ul.

Acest contract expune exclusiv acel endpoint deja câștigat — nu se
adaugă nicio logică de calcul, nicio acțiune nouă, niciun apel către
`PriorityEngine` din afara router-ului deja existent.

## 2. Scope

**Domeniu:** exclusiv `apps/workbench/index.html` + `tests/test_workbench_structure.py`.

**Explicit exclus — niciun cod backend nu se modifică:**
- `src/engines/priority/priority_engine.py`
- `src/api/routers/priority.py`, `dependencies.py`, `schemas.py`, `main.py`
- Niciun endpoint nou, nicio schimbare de payload/response

**Explicit exclus din UI — fără butoane de acțiune:**
Priority e panou de citire/execuție a priorității, nu de acțiune.
Liderul vede ordinea, dar acționează din panourile deja existente
(Mission, FollowUp). Nicio duplicare a logicii de tranziție de stare.

## 3. Plasament — imediat după Mission, aceeași zonă de execuție

```
Login → Mission → Priority → Contact → Conversation → Objection → FollowUp → Partner
```

Priority e activ imediat după autentificare, **independent de
`currentContactId`** — identic ca principiu cu Mission (Decizia 38):
activat direct în `login()`, nu condiționat de selecția unui contact.

Motivație (verbatim din decizia aprobată): Mission arată misiunea și
progresul ei; Priority devine stratul de ordonare a acțiunilor peste
Mission și FollowUp — ambele aparțin execuției liderului, nu relației
cu un contact anume.

## 4. Comportament exact

```
login()
   ↓
setPanelEnabled("panel-priority", true)
   ↓
loadPriority()
   ↓
GET /api/v1/priority   (fără body, fără parametri)
   ↓
render: maximum 5 activități, ÎN ORDINEA primită de la backend
   (Workbench-ul NU resortează, NU filtrează — afișează exact ce
   primește, PriorityEngine e sursa unică de adevăr pentru ordine)
```

Pentru fiecare activitate afișată, exact aceste câmpuri:
- `entity_type` — vizibil (`"mission"` sau `"followup"`)
- `title`
- `impact`
- `urgency`
- `vechime_seconds`
- `entity_id` — păstrat (nu neapărat vizibil ca text), pentru
  identificare/testabilitate viitoare — atribuit ca `data-entity-id`
  pe elementul DOM corespunzător, fără a fi folosit acum pentru nicio
  acțiune

**Listă goală:** mesaj clar, text exact:
`"Nu ai activități prioritare acum."`

## 5. Apel API — payload și metodă

```js
// fără PAYLOAD_START/END — GET fără body, nimic de restricționat strict
const activities = await apiFetch("/api/v1/priority", { method: "GET" });
```

Niciun alt apel către `/api/v1/priority/...` (fără sub-resurse, fără
acțiuni) — regulă verificată explicit prin test (secțiunea 6,
criteriul 7), ca gardă împotriva scope creep-ului către acțiuni.

## 6. Criterii de acceptare (RED — teste structurale)

Urmând convenția deja stabilită la 37/38 (căutare string/regex pe
HTML, `panel disabled id="panel-..."`, verificare explicită a metodei
HTTP la fel ca testul `/present` de la Decizia 38):

1. `test_contine_endpoint_get_priority` — `"/api/v1/priority"` prezent ca string literal
2. `test_priority_foloseste_method_get` — apelul `apiFetch` pentru `/api/v1/priority` folosește explicit `method: "GET"` (extragere bloc opțiuni, nu doar prezența URL-ului)
3. `test_zona_priority_activa_dupa_login` — `id="panel-priority"`, `class="panel disabled"`, activat direct în `login()` (regex pe corpul funcției, identic tipar cu testul Mission de la Decizia 38)
4. `test_afiseaza_campurile_activitate` — codul referențiază explicit `entity_type`, `title`, `impact`, `urgency`, `vechime_seconds` pe obiectul activitate (proprietăți citite, nu doar text decorativ)
5. `test_entity_id_pastrat_ca_atribut` — `data-entity-id` prezent în cod, atașat activității randate
6. `test_mesaj_lista_goala_exact` — textul exact `"Nu ai activități prioritare acum."` prezent
7. `test_fara_subresurse_priority` — nu apare niciun pattern `/api/v1/priority/` (cu slash final urmat de altceva) — gardă împotriva adăugării de acțiuni neautorizate de acest contract

Criteriul `owner_id` absent din fișier rămâne acoperit de testul deja
existent, regresie, nu test nou.

## 7. Ordinea de lucru

```
contract (acest document)
   ↓
RED — 7 teste structurale, toate eșuând din lipsă de cod
   ↓
GREEN — cod minim în index.html care satisface exact aceste teste
   ↓
regresie completă (447 + N teste noi, toate PASS)
   ↓
40 CLOSED
```

Nu se scrie cod UI înainte de RED. După 40, urmează Decizia 41 —
audit final end-to-end pe întregul traseu: Contact → Conversation →
Objection → FollowUp → Partner → Mission → Priority.
