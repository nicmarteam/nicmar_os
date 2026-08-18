# DECIZIA 7 — DEPENDENCY WIRING (`ObjectionEngine`/`ConversationAgent`) — CONTRACT v1

**Status:** precondiție pentru API-ul `ConversationAgent` (Strat 1 din auditul funcțional).
Verificat direct din cod (`src/api/dependencies.py`, `src/auth/dependencies.py`,
`src/api/routers/missions.py`/`followups.py`/`partners.py`) — nu din memorie.

## 0. Auditul (rezumat, verificat direct din cod)

- `src/api/dependencies.py` actual: funcții simple, **fără** `Depends()` intern, fără
  singleton/cache — fiecare funcție (`get_mission_agent`, `get_mission_engine`, etc.)
  construiește graful de zero, independent. Confirmat: `get_mission_agent()` și
  `get_mission_engine()` creează fiecare propriul `RuleEngine`, fără nicio garanție de
  instanță comună — funcționează doar pentru că engine-urile sunt fără stare.
- `get_current_user()`/`CurrentUser` (`src/auth/dependencies.py`) — neschimbat aici,
  rămâne exact cum e, nu se amestecă cu wiring-ul `Objection`/`Conversation`.
- Routerele existente (`missions.py`, `followups.py`, `partners.py`) — pattern identic:
  `Depends(get_current_user)` + `Depends(get_X_agent)`, uneori și `Depends(get_X_engine)`
  separat pentru citiri directe.
- **Nu există `tests/test_dependencies.py`** — wiring-ul existent e validat doar indirect,
  prin testele `*_api.py`, care cer `TestClient` + `DATABASE_URL` real.

## 1. Decizia — Varianta B: chaining real

Spre deosebire de precedentul Mission/FollowUp/Partner (wiring independent, fără garanție
de instanță comună), `ConversationAgent`/`ObjectionEngine` folosesc `Depends()` chaining
intern în `dependencies.py`:

```python
def get_objection_engine() -> ObjectionEngine:
    return ObjectionEngine()


def get_conversation_agent(
    objection_engine: ObjectionEngine = Depends(get_objection_engine),
) -> ConversationAgent:
    return ConversationAgent(objection_engine=objection_engine)
```

**Motiv:** relația `ConversationAgent → ObjectionEngine` e directă și unică (un singur
constructor argument, fără `RuleEngine` intermediar ca la Mission/FollowUp/Partner) — merită
exprimată explicit prin chaining, nu prin duplicare independentă. FastAPI cache-uiește
rezultatul unui `Depends()` per-callable, în cadrul aceluiași request — dacă un endpoint
viitor cere ambele dependințe (`get_objection_engine` și `get_conversation_agent`), va primi
garantat aceeași instanță de `ObjectionEngine`.

**Notă explicită:** aceasta e o abatere conștientă de la pattern-ul existent (Mission/
FollowUp/Partner nu fac chaining), nu o generalizare — precedentul rămâne valabil acolo unde
există, dar nu e o regulă obligatorie de reprodus orbește.

## 2. Ce NU se schimbă

`get_current_user()`/`CurrentUser` — neatinse, fără nicio modificare.

## 3. Testarea — `tests/test_dependencies.py` (fișier nou, fără precedent în repo)

Fără `TestClient`, fără `DATABASE_URL`, fără router — teste unitare pure, apelează direct
funcțiile din `dependencies.py`:

1. `get_objection_engine()` → returnează o instanță `ObjectionEngine`.
2. `get_conversation_agent()` → returnează o instanță `ConversationAgent`.
3. `ConversationAgent` returnat are `.objection_engine` de tip `ObjectionEngine`.
4. Chaining-ul e verificat structural — `get_conversation_agent()` apelat cu o instanță
   `ObjectionEngine` explicită (parametru injectat manual în test, simulând ce ar face
   FastAPI) produce un `ConversationAgent` care păstrează EXACT acea instanță (verificare
   `is`, nu doar `isinstance`) — previne o eventuală regresie unde agentul ar construi
   silențios propriul `ObjectionEngine`, ignorând dependency injection-ul.

## 4. Ce rămâne explicit în afara scopului

- Routerul HTTP (`src/api/routers/objections.py` sau similar) — pas separat, următorul.
- Orice test `TestClient`/`DATABASE_URL` pentru acest strat — nu e necesar, funcțiile din
  `dependencies.py` nu ating DB (construiesc doar obiecte Python).
