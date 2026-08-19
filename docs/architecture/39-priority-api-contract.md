# Decizia 39 — Priority API

Status: APPROVED (owner, 19 august 2026)

## 1. Context

`PriorityEngine` există complet, testat unitar, confirmat conform
propriului contract (`19-priority-engine-contract.md`) — verificat
verbatim, zero discrepanțe între cod și contract. Dar motorul nu are
niciun API expus: `src/api/routers/priority.py` nu există,
`get_priority_engine()` nu există în `dependencies.py`, niciun
`PriorityXxxResponse` în `schemas.py`, `priority` nu apare în
`include_router(...)` din `main.py`.

Confirmat explicit în contract 19, secțiunea 10: absența unui
`PriorityAgent` e o **decizie arhitecturală intenționată** ("Fără
agent dedicat în v1... scop strict"), nu un gol. Router-ul apelează
`PriorityEngine` direct.

**Gol de testare identificat la audit, de închis prin acest contract:**
`test_priority_engine.py` conține exclusiv teste unitare cu mock-uri.
Contractul 19, secțiunea 11, cere explicit ca obligatorii un test de
izolare cu 2 lideri reali și un test de integrare PostgreSQL real —
niciunul nu există azi. Deciziile 37/38 au adăugat exact aceste teste
pentru Partner/Mission; Decizia 39 face la fel pentru Priority.

## 2. Scope

**Domeniu (fișiere noi/modificate):**
- `src/api/routers/priority.py` — **NOU**
- `src/api/dependencies.py` — adăugare `get_priority_engine()`
- `src/api/schemas.py` — adăugare `PrioritizedActivityResponse`
- `src/api/main.py` — adăugare `include_router(priority.router)`
- `tests/test_priority_api.py` — **NOU**, HTTP + PostgreSQL real

**Explicit exclus:**
- `src/engines/priority/priority_engine.py` — neatins; motorul e deja
  corect, confirmat prin audit față de contractul 19
- `tests/test_priority_engine.py` — neatins, testele unitare existente
  rămân valabile
- Niciun `PriorityAgent` nou — decizie deja luată în contract 19
- Workbench (frontend) — rămâne Decizia 40, separată

## 3. Decizie de produs — un singur endpoint, Planul Zilei

**`GET /api/v1/priority`** — fără body, fără parametri de query.

Motiv (verbatim din decizia aprobată): `PriorityEngine` are deja
`apply_workload_filter()` cu regula `[:5]` — API-ul expune
comportamentul operațional deja definit, nu inventează unul nou.
Un singur endpoint, fără `?full=true`, păstrează suprafața API mică
și evitată o a doua decizie de produs nefixată încă.

**Flux exact:**
```
JWT (Authorization: Bearer)
      ↓
current_user.id
      ↓
PriorityEngine().build_priority_list(owner_id)
      ↓
PriorityEngine.apply_workload_filter(...)
      ↓
List[PrioritizedActivityResponse]   (max 5, deja sortat)
```

## 4. Schema răspuns

```python
class PrioritizedActivityResponse(BaseModel):
    entity_type: str        # "mission" | "followup"
    entity_id: UUID
    title: str
    impact: float
    urgency: float
    vechime_seconds: float
```

`GET /api/v1/priority` → `response_model=List[PrioritizedActivityResponse]`
— tipar identic cu `GET /api/v1/contacts` și `GET /api/v1/followups`
(bare list, fără wrapper).

**Decizie de serializare, nu de arhitectură:** `priority_key` (tuplul
intern `(impact, urgency, vechime_seconds)`) **nu apare în response**
— e complet derivabil din celelalte trei câmpuri deja expuse, adăugarea
lui ar duplica informație fără valoare nouă pentru client. Aceeași
regulă aplicată deja la alte mapări dataclass → schema (ex.
`ContactSummaryResponse` nu expune câmpuri interne redundante).

## 5. Dependency injection — tipar identic cu `get_objection_engine()`

```python
def get_priority_engine() -> PriorityEngine:
    """PriorityEngine nu are dependințe proprii — fără RuleEngine, fără alt motor."""
    return PriorityEngine()
```

## 6. Autentificare și securitate

- `current_user: CurrentUser = Depends(get_current_user)` — identic cu
  toate celelalte router-e; `owner_id` vine exclusiv din JWT
- Fără request de niciun fel din partea clientului — nu există
  `entity_id`/`owner_id` de validat, deci **niciun risc de enumerare**
  (motorul nu primește niciun ID din exterior, doar `owner_id` din JWT)
- **Niciun exception handler nou necesar** — `PriorityEngine` nu ridică
  nicio excepție custom în condiții normale de date (singura posibilă,
  `ValueError` pentru `contact_status` necunoscut, e imposibil de
  declanșat cu date valide, dat fiind `CHECK` constraint pe
  `contacts.status` la nivel DB)
- Fără autentificare → `401`, comportament deja global (`get_current_user`)

## 7. Criterii de acceptare (RED — `tests/test_priority_api.py`, HTTP + PostgreSQL real)

Închide explicit golul de testare identificat la audit — nu doar teste
funcționale, ci și cele două invariante de securitate lipsă din
contractul 19:

1. `test_get_priority_requires_authentication` — fără token → `401`
2. `test_get_priority_returns_empty_list_when_no_activities` — owner
   fără mission/followup activ → `[]`
3. `test_get_priority_returns_max_five_activities` — owner cu 6+
   activități eligibile (mission + followup create prin HTTP real) →
   răspunsul are exact 5 elemente
4. `test_get_priority_excludes_completed_activities` — o misiune
   `COMPLETED` (via fluxul real assign→start→complete) nu apare în
   răspuns
5. `test_get_priority_orders_mission_before_lower_impact_followup` —
   verifică prin HTTP real invarianta 1 din contract 19 (Impact
   domină): FollowUp cu `contact.status=ARCHIVED` (impact 1.0) nu
   trece niciodată înaintea unui Mission cu impact egal dar urgență
   mai mare, conform priority_key
6. `test_owner_a_vede_exclusiv_activitatile_proprii` — **PostgreSQL
   real**, liderul A creează mission/followup, liderul B (autentificat
   separat) apelează `GET /priority`, activitățile lui A nu apar
7. `test_owner_b_vede_exclusiv_activitatile_proprii` — companion
   invers: B creează activități, A nu le vede — cele două teste
   închid împreună golul de izolare cerut de contractul 19, secțiunea 11
8. `test_get_priority_response_fara_priority_key` — răspunsul JSON nu
   conține niciun câmp `priority_key` (confirmă decizia de serializare
   din secțiunea 4)

## 8. Ordinea de lucru

```
contract (acest document)
   ↓
RED — tests/test_priority_api.py, toate eșuând (endpoint inexistent, 404)
   ↓
GREEN — router.py + dependencies.py + schemas.py + main.py, cod minim
   ↓
regresie completă (439 + N teste noi, toate PASS)
   ↓
39 CLOSED
```

Nu se scrie cod de implementare înainte de RED. `priority_engine.py`
rămâne neatins pe tot parcursul acestei decizii.
