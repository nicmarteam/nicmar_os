# PRIORITY ENGINE — IMPLEMENTATION CONTRACT v1

**Status:** verificat față de `18-priority-engine-spec-v1.md` (specificația de decizie, complet închisă) și față de codul real existent
**Data:** 12 august 2026 (continuare, aceeași sesiune)
**Precedent:** aceeași disciplină ca `11`/`12`/`13` (Mission/FollowUp/Partner) — contract înainte de cod, 3 verificări, test de integrare stateful, PostgreSQL real

---

## 0. Ce NU face acest motor (scop strict)

`PriorityEngine` **nu creează, nu modifică, nu finalizează** nimic — e strict **read-only**, citește din `missions`/`follow_ups`/`contacts`, calculează, returnează o listă ordonată. Nicio scriere în DB, cu o singură excepție posibilă (persistarea opțională a rezultatului — v. secțiunea 8, marcată explicit ca decizie separată, nu implicită).

---

## 1. Inputuri

```python
build_priority_list(owner_id: UUID) -> List[PrioritizedActivity]
```

Un singur parametru obligatoriu: `owner_id`. Toate datele necesare (Mission/FollowUp active, `contacts.status`, `scheduled_at`) sunt citite intern, filtrate strict per `owner_id` — aceeași disciplină de izolare aplicată azi la toate motoarele (bug-urile #1-4 găsite și corectate).

---

## 2. Output

```python
@dataclass(frozen=True)
class PrioritizedActivity:
    entity_type: str        # "mission" | "followup"
    entity_id: UUID
    title: str               # missions.title / follow_ups.notes sau identificator descriptiv
    impact: float
    urgency: float
    vechime_seconds: float   # ACUM - created_at, în secunde (unitate brută, nu rotunjită)
    priority_key: tuple      # (impact, urgency, vechime_seconds) — folosit direct pentru sortare
```

**Partner exclus din output-ul v1** — verificat în `18`: Partner nu are concept de "activitate deschisă, în așteptare" comparabil cu Mission/FollowUp (diagnosticul + trimiterea sunt same-day, nu persistă ca "PENDING" în timp). `PriorityEngine v1` produce lista doar din Mission + FollowUp active.

---

## 3. Valorile admise — verbatim din `18`

### Impact
```
Mission              → 1.0 (fix)
FollowUp + ARCHIVED  → 1.0
FollowUp + NEW       → 1.5
FollowUp + ACTIVE    → 2.0
FollowUp + CONVERTED → 1.0
```

### Urgență
```
Mission              → 1.0 (fix — missions.scheduled_at mereu NULL, verificat în cod)
FollowUp, din scheduled_at vs. ACUM:
    ≥3 zile viitor    → 1.00
    +1-2 zile         → 1.33
    ziua curentă      → 1.67
    trecut (orice)    → 2.00
```

### Vechime
```
Toate tipurile: ACUM - created_at (secunde)
```

---

## 4. Regula de sortare — `PriorityKey`

```python
sorted(activities, key=lambda a: a.priority_key, reverse=True)
```

Tuplu `(impact, urgency, vechime_seconds)` — sortare Python nativă pe tuplu face exact ordinea lexicografică cerută (`Impact` decide primul, `Urgență` desparte la egalitate de Impact, `Vechime` desparte la egalitate de Impact ȘI Urgență) — **fără cod suplimentar de comparație**, comportament nativ al limbajului.

---

## 5. Comportament pentru activități neterminate vs. terminate

`build_priority_list` interoghează **strict** activități în stări ne-terminale:
```
missions:   status IN ('GENERATED', 'ASSIGNED', 'IN_PROGRESS')
follow_ups: status = 'PENDING'
```
O activitate `COMPLETED`/`POSTPONED`/`RESCHEDULED` **nu apare niciodată** în output — motor de prioritizare, nu de istoric (istoricul rămâne acoperit de `Timp`, componenta separată, pentru `DIS`).

---

## 6. Comportament pentru date lipsă

| Caz | Comportament |
|---|---|
| `Mission` fără `contact_id` (mereu, azi) | Impact = `1.0`, fără eroare — comportament normal, nu excepție |
| `Mission` fără `scheduled_at` (mereu, azi) | Urgență = `1.0`, fără eroare — comportament normal |
| `FollowUp` fără `contact_id` | **Imposibil** — `contact_id` e `NOT NULL` în schemă, nu se gestionează acest caz |
| `owner_id` fără nicio activitate activă | Returnează listă goală `[]`, nu eroare |

---

## 7. Filtrul de Încărcare — separat de scoring

```python
apply_workload_filter(sorted_activities: List[PrioritizedActivity]) -> List[PrioritizedActivity]
```

Aplicat **după** sortare, niciodată în interiorul calculului `PriorityKey`.

### Regulă exactă, fără formulă inventată
```
Planul Zilei = până la 5 activități prioritare (primele din lista deja sortată),
               cu obiectivul operațional de 3-5 atunci când există suficiente activități eligibile.
```

**Comportament, caz cu caz, verificat — nu dedus dintr-o formulă:**
- 5+ activități disponibile → afișăm exact **5** (plafon dur)
- 4 disponibile → afișăm **4**
- 3 disponibile → afișăm **3**
- 1-2 disponibile → afișăm **cele disponibile** (1 sau 2)
- 0 disponibile → **listă goală**

Implementare: `sorted_activities[:5]` — atât. **Niciun `min`/`max` artificial, niciun plafon minim forțat** — sursa spune "3-5 acțiuni esențiale", nu "minimum 3, chiar dacă nu există"; a forța un minim de 3 când owner-ul are doar 1 activitate eligibilă ar însemna să inventăm activități care nu există.

---

## 8. Persistare — explicit NU în v1

`PriorityEngine v1` **nu scrie rezultatul nicăieri** — e calculat la cerere (ex: la fiecare afișare de Dashboard), nu persistat în `scores`/tabel nou. Motiv: rezultatul depinde de `ACUM` (Vechime, Urgență) — persistarea ar produce date stale imediat. Dacă se dorește caching, rămâne decizie separată, ulterioară.

---

## 9. Invariante care trebuie să rămână adevărate (verificate prin teste)

1. Niciun `Mission` cu Impact `1.0` nu apare vreodată înaintea unui `FollowUp` cu Impact `2.0`, indiferent de Urgență/Vechime
2. La Impact egal, Urgență mai mare decide — testat cu Impact identic, Urgență diferită
3. La Impact ȘI Urgență egale, Vechime mai mare decide
4. Rezultatul conține **exclusiv** activități ale `owner_id`-ului cerut — test de izolare cu 2 lideri, ca la toate motoarele de azi
5. Rezultatul **nu conține niciodată** activități `COMPLETED`/`POSTPONED`/`RESCHEDULED`
6. Filtrul de Încărcare nu schimbă ordinea, doar trunchiază

---

## 10. Structura de fișiere

```
src/engines/priority/
├── __init__.py
└── priority_engine.py
```

Fără agent dedicat în v1 — consumat direct de API-ul viitor sau de un `PriorityAgent` ulterior, nu construit acum (scop strict, conform regulii "nu construim infrastructură inutilă" aplicată toată sesiunea).

---

## 11. Teste obligatorii înainte de cod finalizat

- [ ] Impact: toate 5 cazuri (Mission, FollowUp × 4 status contact)
- [ ] Urgență: toate 5 cazuri (Mission, FollowUp × 4 praguri temporale)
- [ ] Vechime: calcul corect, pe date reale (nu mock de timp — folosește timestamp real din DB)
- [ ] Sortare: cele 3 invariante din secțiunea 9 (Impact domină, Urgență tiebreaker, Vechime tiebreaker final)
- [ ] Izolare: 2 lideri, fiecare vede strict propriile activități
- [ ] Excludere terminale: activități `COMPLETED` nu apar
- [ ] Filtru Încărcare: trunchiere corectă la 3-5, fără reordonare
- [ ] PostgreSQL real: test de integrare stateful, ca la Mission/FollowUp/Partner
- [ ] Regresie completă: cele 115+ teste existente rămân verzi

---
*Contract verificat față de `18` (specificație de decizie) și codul real (`missions`/`follow_ups`/`contacts` schema, `MissionEngine`/`FollowUpEngine` pattern). Zero decizii de business deschise — Partner exclus (confirmat), Planul Zilei fără formulă inventată (confirmat, `sorted_activities[:5]`). Executabil conceptual complet.*
