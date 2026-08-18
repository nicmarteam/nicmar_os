# DECIZIA 27 — OBJECTION WORKBENCH — CONTRACT v1

**Status:** confirmat de owner — HTML + JavaScript vanilla, un singur fișier, fără Gradio,
fără framework, fără build tooling. Verificat direct din audit: `apps/playground/` e
arhitectural incompatibil (acces direct la engine, zero auth, `gradio` nedeclarat/neinstalat —
nu rulează în acest repo) — Workbench e o aplicație nouă, separată.

Precondiții validate: Decizia 7 (dependency wiring), Decizia 8A (`get_objection()`,
`confirm_response()` scalar), Decizia 26 (router HTTP, 285/285 PASSED pe PostgreSQL real).

## 0. Locație

```
apps/workbench/
└── index.html
```

Un singur fișier — HTML, CSS și JS inline, exact ca decizia ta.

## 1. Regulile arhitecturale (neschimbate, reconfirmate)

```
Workbench → HTTP → objections.py → ConversationAgent → ObjectionEngine → PostgreSQL
```

Workbench-ul:
- folosește `fetch()` nativ, fără librării;
- trimite `Authorization: Bearer <JWT>` pe fiecare request;
- ține JWT-ul **doar în memoria sesiunii** (variabilă JS) — **NU** `localStorage`,
  **NU** `sessionStorage`, **NU** cookie;
- **NU** are acces la DB, **NU** importă cod Python, **NU** conține logică de business,
  **NU** reproduce Safety Validation, **NU** reconstruiește `Objection`, **NU** decide
  ownership-ul — toate acestea rămân exclusiv responsabilitatea backend-ului.
- **NU construiește login** — pagina primește JWT-ul printr-un câmp de sesiune (input text,
  completat manual de lider, de ex. copiat din răspunsul `/api/v1/auth/login` apelat separat,
  ex. prin Postman/curl, sau printr-un mic formular de login care doar apelează endpoint-ul
  existent și pune rezultatul în memorie — vezi secțiunea 2.1). API-ul rămâne singura
  autoritate de autentificare/autorizare.

## 2. Structura paginii — 4 zone vizibile

### 2.1 Zona Token (permanent vizibilă, sus)

Un câmp text simplu unde liderul lipește JWT-ul, plus un buton "Salvează token" care îl pune
într-o variabilă JS (`let authToken = null;`). Alternativ (mai prietenos pentru un
non-tehnician): un mini-formular `email`/`parolă` care apelează `POST /api/v1/auth/login` și
pune `access_token` din răspuns direct în `authToken` — **fără să afișeze sau să stocheze
parola nicăieri după request**. Aleg această a doua variantă pentru MVP, ca liderul să nu
trebuiască să folosească un tool extern doar ca să obțină tokenul.

Fără token valid în memorie, orice acțiune ulterioară afișează explicit "Autentifică-te
întâi" — Workbench-ul nu presupune niciodată un token implicit.

### 2.2 Zona Analiză (Faza 1)

- Textarea: "Ce a spus prospectul?"
- Buton "Analizează"
- La click: `POST /objections/analyze`
- Afișează rezultatul:
  - dacă `needs_manual_selection === false`: categoria detectată, cu buton "Continuă cu
    această categorie"
  - dacă `needs_manual_selection === true`: apelează automat `GET /objections/categories`,
    afișează cele 13 ca listă de radio-buttons/butoane selectabile

### 2.3 Zona Pregătire (Faza 2)

- La confirmarea categoriei (din 2.2): `POST /objections/prepare` cu `objection_text`
  (păstrat din Faza 1) + `objection_category` (aleasă)
- Afișează cele 3 variante (`CALDA`/`DIRECTA`/`INTREBARE`) ca 3 carduri/opțiuni, fiecare cu
  textul complet vizibil
- Liderul alege una (radio/click) → textul ei apare într-un `<textarea>` editabil
- Butonul "Confirmă și trimite" rămâne inactiv până la o selecție

### 2.4 Zona Confirmare (Faza 3)

- La click "Confirmă și trimite": `POST /objections/confirm` cu **exact** `objection_id`
  (păstrat din răspunsul `/prepare`), `response_text` (conținutul curent al textarea-ului,
  posibil editat), `response_variant_used` (cheia variantei alese inițial — **neschimbată**
  chiar dacă textul a fost editat, la fel ca regula din `21`/`22`)
- Randare pe `validation_level`, per secțiunea 4

## 3. Payload-urile exacte — identice cu schema Pydantic din `26-objections-router-contract.md`

```javascript
// POST /api/v1/objections/analyze
{ "objection_text": "Mi se pare prea scump." }
// -> { "detected_category": "PRET" | null, "needs_manual_selection": bool }

// GET /api/v1/objections/categories
// (fara body)
// -> { "categories": ["AMANARE", "FAMILIE_SUPORT", ...] }  // 13, alfabetic

// POST /api/v1/objections/prepare
{ "objection_text": "...", "objection_category": "PRET", "conversation_id": null }
// -> { "objection_id": "uuid", "variants": { "CALDA": "...", "DIRECTA": "...", "INTREBARE": "..." } }

// POST /api/v1/objections/confirm
{ "objection_id": "uuid", "response_text": "...", "response_variant_used": "CALDA" }
// -> { "persisted": bool, "validation_level": "PASS"|"BLOCK"|"PARTIAL_VALIDATION"|"HUMAN_REVIEW", "reason": string|null }
```

**Interzis explicit în orice payload trimis de Workbench:** `owner_id`, `objection_category`
(la `/confirm`), `objection_text` (la `/confirm`) — identic cu regula de securitate din `26`.

## 4. Randarea celor 4 niveluri Safety — BLOCK e rezultat normal, NU eroare tehnică

| `validation_level` | `persisted` | Afișare Workbench |
|---|---|---|
| `PASS` | `true` | ✅ Mesaj succes verde: "Răspuns trimis cu succes." |
| `BLOCK` | `false` | ⚠️ Banner de avertisment (NU roșu de eroare tehnică): "Răspuns blocat de validarea de siguranță. Motiv: {reason}." + textarea rămâne editabilă + butonul "Confirmă și trimite" rămâne activ, pentru reîncercare imediată |
| `PARTIAL_VALIDATION` | `true` | ℹ️ Mesaj succes cu avertisment atașat: "Trimis, dar semnalat: {reason}." |
| `HUMAN_REVIEW` | `true` | ℹ️ Mesaj succes cu avertisment: "Trimis — recomandăm verificare suplimentară: {reason}." |

Distincție explicită de design: `BLOCK` NU se randează ca o eroare de rețea/server (nu roșu
alarmant tip "500 Internal Server Error") — e un rezultat funcțional normal al Safety
Validation, tratat vizual ca parte a fluxului, nu ca o defecțiune a Workbench-ului.

## 5. Erorile HTTP reale (spre deosebire de BLOCK, acestea SUNT probleme)

| Status | `error_code` | Afișare |
|---|---|---|
| `401` | — | "Sesiunea a expirat sau tokenul e invalid — autentifică-te din nou." Golește `authToken`, revine la Zona Token. |
| `403` | `ACCESS_DENIED` | "Nu ai acces la această obiecție." (nu ar trebui să apară în flux normal — doar dacă tokenul aparține altui lider) |
| `400` | `INVALID_CATEGORY` / `INVALID_REFERENCE` | Afișează `message` din răspuns, direct |
| `422` | — | Eroare de validare Pydantic (payload malformat) — nu ar trebui să apară dacă Workbench respectă schema; afișare generică "Eroare de format, contactează dezvoltatorul." |

## 6. Direcție vizuală minimă (nu design complet — doar principii pentru GREEN)

Interfață funcțională, curată, fără decor inutil — instrument de lucru pentru un lider în
timp real, nu pagină de marketing. Cele 3 faze clar delimitate vizual (numerotare 1/2/3 e
justificată aici — fluxul chiar e secvențial, nu un truc estetic). Culoare de avertisment
pentru `BLOCK` (galben/portocaliu), nu roșu — reface distincția din secțiunea 4.

## 7. Testarea — o limitare reală, care trebuie confirmată explicit

Repo-ul **nu are nicio infrastructură de testare JavaScript** (fără Jest, Playwright,
Selenium — verificat, `pyproject.toml` conține doar `pytest`/`httpx`, pentru Python). Un fișier
HTML+JS static, cu logică inline, nu poate fi testat cu suita `pytest` existentă în sensul
"RED echivalent unui test unitar Python".

Propun două niveluri, ca să păstrăm totuși disciplina RED→GREEN, fără să inventez o unealtă
nouă de testare fără să întreb:

**Nivel 1 — teste structurale (Python, fără dependențe noi), `tests/test_workbench_structure.py`:**
verifică STATIC conținutul fișierului `index.html` (citit ca text), nu comportamentul lui în
browser. RED = fișierul nu există încă. GREEN = fișierul există și conține:
- fiecare din cele 4 URL-uri de endpoint exacte (`/api/v1/objections/analyze`, etc.)
- fiecare din câmpurile de payload obligatorii (`objection_text`, `objection_category`,
  `objection_id`, `response_text`, `response_variant_used`)
- **absența** literelor `localStorage`/`sessionStorage`/`document.cookie` (regula de
  securitate a tokenului, verificată static)
- **absența** oricărui import Python/SQL (`psycopg`, `SELECT`, `INSERT`)
- prezența gestionării pentru toate cele 4 `validation_level`

**Nivel 2 — verificare manuală ghidată, cu PostgreSQL real:** eu pornesc `TestClient`-ul
(sau, dacă preferi, un server `uvicorn` real local), tu deschizi `index.html` în browser, faci
login, și parcurgi fluxul complet cu o obiecție reală, iar eu confirm în paralel din DB că
datele apar corect. Nu e "test automat" în sensul `pytest`, dar e verificare reală, nu doar
citire de cod.

**Nu propun introducerea Playwright/Selenium acum** — ar fi o dependență nouă, netriviala,
pentru un MVP intern cu un singur fișier. Dacă Workbench-ul crește, automatizarea testării
browser-ului devine o decizie separată, cu propriul audit.

Confirmi acest plan de testare (Nivel 1 + Nivel 2), sau preferi altă abordare?
