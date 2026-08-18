# `ObjectionEngine.get_objection()` — CONTRACT v1

**Status:** confirmat de owner, Decizia 8A — precondiție pentru API-ul HTTP al `ConversationAgent`.
Motiv: HTTP e stateless între `/prepare` și `/confirm`; clientul nu poate fi sursă de încredere
pentru `owner_id`/`objection_category`/`objection_text` — trebuie re-citite din DB la fiecare
request, la fel ca `FollowUpEngine._set_status()`/`PartnerEngine._verify_ownership()` (pattern
confirmat identic în tot repo-ul, inclusiv urmă a unui audit real de securitate anterior,
12 august 2026).

## 1. Semnătura

```python
def get_objection(self, objection_id: UUID, owner_id: UUID) -> Objection
```

## 2. Comportament

```sql
SELECT id, owner_id, conversation_id, objection_category, objection_text, resolution_status
FROM objections
WHERE id = %s AND owner_id = %s
```

| | |
|---|---|
| DB | DA — un singur `SELECT`, fără nicio scriere |
| Filtrare | `owner_id` OBLIGATORIU în `WHERE` — existența `objection_id` singură NU acordă acces (identic principiu cu `submit_response`) |
| Return | `Objection` complet, construit din valorile citite |
| Erori | `ObjectionNotFoundError` — rând inexistent SAU aparține altui `owner_id`. Reutilizează excepția deja existentă (folosită de `submit_response`) — nu introducem o excepție nouă pentru același tip de eșec. |

## 3. Ce NU face

Nu verifică `resolution_status`, nu filtrează după stare — orice obiecție a owner-ului, indiferent
de stare, poate fi citită. Filtrarea pe stare (dacă va fi nevoie) e o decizie separată.
