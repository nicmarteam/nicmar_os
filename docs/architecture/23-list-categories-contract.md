# DECIZIA 6 — `list_categories()` — CONTRACT v1

**Status:** precondiție pentru API-ul `ConversationAgent` (rezolvă golul Strat 2 din auditul
funcțional). Verificat direct din cod (`src/engines/objection/library.py`) — `ALL_CATEGORIES`
deja importat în `objection_engine.py`, nu necesită import nou.

## 0. Decizie arhitecturală

`API → ConversationAgent → ObjectionEngine → library.ALL_CATEGORIES` — routerul HTTP (viitor)
NU importă direct `ALL_CATEGORIES` din `library.py`. `list_categories()` există la ambele
niveluri (`ObjectionEngine` și `ConversationAgent`), fiecare o simplă delegare, la fel ca
`classify()`/`get_variants()`.

## 1. Semnături

```python
# ObjectionEngine
def list_categories(self) -> List[str]

# ConversationAgent
def list_categories(self) -> List[str]
```

## 2. Comportament

| | |
|---|---|
| DB | **NU** — pur, `ALL_CATEGORIES` e un `frozenset` static din `library.py` |
| Return | Listă cu exact cele 13 categorii oficiale |
| **Ordine — decizie explicită** | `sorted(ALL_CATEGORIES)` — alfabetic. `ALL_CATEGORIES` e `frozenset`, fără ordine garantată; sortarea alfabetică e alegerea cea mai simplă și deterministă pentru afișare (liderul vede aceeași listă, în aceeași ordine, de fiecare dată). Nu reflectă vreo prioritate de business — dacă va fi nevoie de o ordine specifică (frecvență, relevanță), e o decizie separată, ulterioară. |
| Erori | Niciuna |

## 3. Ce rămâne explicit în afara scopului

- Orice ordine "inteligentă" (frecvență de utilizare, relevanță contextuală) — doar alfabetic în v1.
- Traducerea codurilor (`PRET`, `TIMP`, etc.) în text uman-lizibil pentru UI — rămâne
  responsabilitatea stratului de prezentare (Workbench), nu a backend-ului.
- Test dedicat pe PostgreSQL real — inutil, metoda nu atinge DB (la fel ca `classify()`,
  care nu are test separat pe Postgres real, doar verificare inclusă în fluxul E2E existent).

## 4. Următorul pas

RED → teste pentru `ObjectionEngine.list_categories()` și `ConversationAgent.list_categories()`
→ GREEN → regresie completă (fără test PostgreSQL nou, per motivul de mai sus).
