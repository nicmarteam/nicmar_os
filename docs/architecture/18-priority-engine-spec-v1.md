# PRIORITY ENGINE — SPECIFICAȚIE v1

**Status:** specificație de logică, verificată din surse reale — **nu e cod, nu e implementare**
**Data:** 12 august 2026 (continuare, aceeași sesiune)
**Scop:** îngheață deciziile luate azi despre `PriorityEngine v1`, înainte de orice linie de cod

---

## 0. Ce NU e acest document

Nu e specificație executabilă completă — conține explicit secțiuni **TBD**, marcate ca atare, nu completate cu valori inventate. Codul nu pornește până aceste TBD-uri nu sunt rezolvate separat.

---

## 1. Scope — cele 4 intrări reale confirmate azi

Din cele 7 intrări documentate pentru `PriorityEngine` (`05-competente-37-motor1.md`), **doar 4 sunt fezabile pentru v1**:

| Intrare | Status |
|---|---|
| `MissionEngine` | ✅ folosit |
| `FollowUpEngine` | ✅ folosit |
| Date derivate din relație (proxy pentru `RelationshipEngine`) | ✅ folosit, parțial (doar `contacts.status`) |
| `users.preferences` (proxy pentru `Motorul Identității`) | ⚠️ structură există, neconfigurată — **nu folosită activ în v1**, doar rezervată |

**Excluse explicit din v1** (post-MVP real, confirmat azi): `HabitEngine`, `Calendar`, `Dashboard` (reclasificat ca și consumator, nu intrare).

---

## 2. Impact v1 — DECIS, complet

### Regulă
```
ImpactBase:
    Mission  = 1.0
    FollowUp = 1.0
    Partner  = 2.0

FollowUpContextBonus (din contacts.status, doar pentru FollowUp):
    ARCHIVED  = 0.0
    NEW       = 0.5
    ACTIVE    = 1.0
    CONVERTED = 0.0   (fără bonus de proximitate — NU valoare mică, doar "nu se aplică")

Impact(FollowUp) = ImpactBase + FollowUpContextBonus   → interval [1.0, 2.0]
Impact(Mission)  = 1.0   (fix — fără Layer 2, contact_id mereu NULL azi)
Impact(Partner)  = 2.0   (fix — fără Layer 2, context relațional exclus explicit din v1)
```

### Motivul limitării Mission/Partner la valoare fixă
- **Mission**: `generate_mission()` nu acceptă/scrie `contact_id` — verificat în cod, coloana există în schemă dar rămâne mereu `NULL`
- **Partner**: `partners.contact_id` e obligatoriu, dar contactul e aproape sigur deja `CONVERTED` (constant, neinformativ); `partners.status` măsoară maturitate parteneriat, concept diferit de proximitate — exclus deliberat

### Layer 3 (progres real în relație) — **v2, nu v1**
Necesită `state_history` pentru `Contact` (nu există azi — `Contact` are doar `status` curent + `updated_at`, fără istoric de tranziții).

---

## 3. Timp v1 — ✅ DECIS, confirmat explicit

```
Mission:   state_history(new_state='COMPLETED').created_at − missions.created_at
FollowUp:  state_history(new_state='COMPLETED').created_at − follow_ups.created_at
Partner:   events('PartnerInteractionCompleted').created_at
           − events('PartnerDiagnosticGenerated').created_at
```

Toate 3 derivate din timestamp-uri deja scrise de codul existent — fără câmpuri noi, fără presupuneri. **Confirmat explicit de Nic.**

---

## 4. Încărcare v1 — ✅ DECIS complet (formulă + rol)

```
Încărcare(owner_id) = COUNT(missions WHERE owner_id=X AND status IN
                             ('GENERATED','ASSIGNED','IN_PROGRESS'))
                     + COUNT(follow_ups WHERE owner_id=X AND status='PENDING')
```

### Rol în agregare — decis oficial
**Încărcarea NU modifică `PriorityScore` al unei activități.** E filtru aplicat **după** sortare — determină câte activități din vârful listei intră în Planul Zilei, nu cum se calculează scorul fiecăreia.

```
Flux: Impact + Timp + Urgență → PriorityScore → sortare → filtru Încărcare → Planul Zilei (3-5 acțiuni)
```

**Motiv, din sursă**: *"Nu există mai mult de 3-5 acțiuni esențiale"* (plafon dur de afișare) + *"reduce încărcarea cognitivă"* (prin a arăta mai puțin, nu prin recalcularea scorului).

---

## 5. Urgență v1 — DECIS parțial, praguri **TBD explicit**

```
UrgențăBase = 1.0   (Mission, Partner — fără date reale de urgență în v1)

UrgențăFollowUp = derivat din follow_ups.scheduled_at, comparat cu "acum":
    TBD — pragurile exacte (ce înseamnă "depășit", "azi", "apropiat", "îndepărtat",
    în unități de timp concrete) NU sunt decise. Nu se inventează acum.
```

### De ce Mission/Partner rămân la valoare de bază
Aceeași asimetrie găsită la Impact: `missions.scheduled_at` există în schemă, dar **nu e niciodată setat** de `generate_mission()` — verificat în cod, rămâne mereu `NULL`. `Partner` n-are echivalent de `scheduled_at` deloc.

---

## 6. Formula agregată — **TBD, nedecisă**

Cele 4 componente (Impact, Timp, Încărcare, Urgență) au fost definite **individual**, dar modul lor de combinare într-un scor final de prioritate **nu a fost stabilit azi**:
- Sumă ponderată? Produs? Ordine lexicografică (Impact primul, Timp ca tiebreaker)?
- Încărcarea intră în formulă, sau rămâne filtru separat (v. secțiunea 4)?

**Nu se inventează această formulă acum** — rămâne următoarea decizie de business, separată.

---

## 7. Ce intră în v1 vs. rămâne v2

| Componentă | v1 | v2 |
|---|---|---|
| Impact — Layer 1 (tip) | ✅ | — |
| Impact — Layer 2 (context, doar FollowUp) | ✅ | — |
| Impact — Layer 3 (progres real relație) | ❌ | ✅ (necesită `state_history` pentru Contact) |
| Timp | ✅ decis, confirmat | — |
| Încărcare (formulă) | ✅ | — |
| Încărcare (rol în agregare) | ✅ filtru post-scoring | — |
| Urgență (concept + sursă date) | ✅ (doar FollowUp) | — |
| Urgență (praguri numerice) | ❌ TBD | — |
| Urgență pentru Mission/Partner | ❌ (valoare de bază) | ✅ (necesită `scheduled_at` populat real) |
| Formula agregată finală | ❌ TBD | — |
| `HabitEngine`, `Calendar`, `Dashboard` ca intrări | ❌ | post-MVP, nedatat |

---

## 8. Limite cunoscute, explicite

1. **Mission e sistematic dezavantajat** față de FollowUp în Impact și Urgență, nu din decizie de business, ci din lipsă de date (`contact_id`, `scheduled_at` nesetate) — risc real de a subprioritiza Mission-uri, dacă formula agregată nu compensează
2. **`CONVERTED = 0.0` bonus** poate fi interpretat greșit ca "valoare mică" dacă nu e documentat clar în UI/Dashboard — necesită atenție la implementare
3. **Încărcarea și Urgența au 2 TBD-uri fiecare** (rol în agregare / praguri) — engine-ul nu poate fi complet fără ele

---

## 9. Teste necesare înainte de implementare (checklist, nu implementate încă)

- [ ] Impact: Mission → mereu `1.0`, indiferent de context
- [ ] Impact: Partner → mereu `2.0`
- [ ] Impact: FollowUp × 4 contexte → `1.0`/`1.5`/`2.0`/`1.0` (ARCHIVED/NEW/ACTIVE/CONVERTED)
- [ ] Timp: calculat corect din `state_history`, pentru toate 3 tipuri
- [ ] Timp: gestionare corectă dacă entitatea nu e încă `COMPLETED` (fără eroare, valoare `None`/`TBD`)
- [ ] Încărcare: numărătoare corectă, izolată per `owner_id` (verificare de securitate, ca la toate celelalte azi)
- [ ] Urgență: Mission/Partner → mereu `1.0`
- [ ] Test de regresie: cele 115+ teste existente rămân verzi

---

## 10. Următorul pas real

**Nu cod încă.** Rămân 3 decizii de business explicite, separate, înainte de implementare:
1. Pragurile numerice pentru Urgență (FollowUp)
2. Rolul Încărcării în agregare (filtru vs. componentă de scor)
3. Formula agregată finală (cum se combină Impact+Timp+Urgență[+Încărcare])

---
*Document canonic. Fiecare valoare din secțiunile 2-3 e verificată din cod/schemă reală. Fiecare TBD e marcat explicit, nu completat cu presupuneri.*
