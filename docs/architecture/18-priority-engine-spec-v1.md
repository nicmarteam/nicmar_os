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

**Rol: retrospectiv, pentru `DIS`/analiză — NU e input live pentru `PriorityScore`** (v. secțiunea 3bis pentru distincția de `Vechime`).

```
Mission:   state_history(new_state='COMPLETED').created_at − missions.created_at
FollowUp:  state_history(new_state='COMPLETED').created_at − follow_ups.created_at
Partner:   events('PartnerInteractionCompleted').created_at
           − events('PartnerDiagnosticGenerated').created_at
```

Toate 3 derivate din timestamp-uri deja scrise de codul existent — fără câmpuri noi, fără presupuneri. **Confirmat explicit de Nic.**

**Limitare structurală, descoperită la definirea formulei agregate:** `Timp` se calculează *doar după* `COMPLETED` — inutilizabil ca input pentru `PriorityScore`, care trebuie să decidă prioritatea printre activități **încă neterminate** (`PENDING`/`IN_PROGRESS`), care n-au încă timestamp de finalizare. De aici, secțiunea următoare.

---

## 3bis. Vechime v1 — ✅ DECIS, concept nou, distinct de Timp

**Rol: live, input real pentru `PriorityScore`** — răspunde la *"de cât timp așteaptă asta, acum"*, nu *"cât a durat, retrospectiv"*.

```
Vechime = ACUM − created_at   (pentru orice activitate încă deschisă)

Mission:   ACUM − missions.created_at
FollowUp:  ACUM − follow_ups.created_at
Partner:   ACUM − events('PartnerDiagnosticGenerated').created_at
```

**`Timp` și `Vechime` NU sunt același concept, deși folosesc surse de date similare** — `Timp` măsoară un interval încheiat (finalizare − creare), `Vechime` măsoară un interval deschis (acum − creare), recalculat continuu. Nu se substituie unul pe altul.

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

## 5. Urgență v1 — ✅ DECIS complet, praguri confirmate

```
UrgențăBase = 1.0   (Mission, Partner — fără date reale de urgență în v1)

UrgențăFollowUp, din follow_ups.scheduled_at comparat cu "acum":
    Îndepărtat (≥3 zile în viitor)  → 1.00
    Apropiat (+1-2 zile)            → 1.33
    Azi (ziua curentă)              → 1.67
    Depășit (orice moment trecut)   → 2.00   (plat — 10 minute sau 3 zile depășite = aceeași valoare)
```

**Confirmat explicit de Nic.** Durata exactă a întârzierii rămâne disponibilă separat, prin `Vechime` (secțiunea 3bis) — nu se introduce o a doua scală de Urgență pentru asta.

### De ce Mission/Partner rămân la valoare de bază
Aceeași asimetrie găsită la Impact: `missions.scheduled_at` există în schemă, dar **nu e niciodată setat** de `generate_mission()` — verificat în cod, rămâne mereu `NULL`. `Partner` n-are echivalent de `scheduled_at` deloc.

---

## 6. Formula agregată — **TBD, nedecisă**

**3 componente intră în `PriorityScore`, dar `Timp` NU e una dintre ele** — corectură conceptuală (secțiunea 3bis): `Timp` e retrospectiv (necesită `COMPLETED`), inutilizabil pentru activități încă deschise. Componenta live corectă e `Vechime`.

```
PriorityScore = f(Impact, Vechime, Urgență)
```

Încărcarea rămâne filtru post-scoring (secțiunea 4), nu intră aici.

Modul exact de combinare **nu a fost stabilit azi**: Sumă ponderată? Produs? Ordine lexicografică (Impact primul, Vechime ca tiebreaker)?

**Nu se inventează această formulă acum** — rămâne următoarea decizie de business, separată.

---

## 7. Ce intră în v1 vs. rămâne v2

| Componentă | v1 | v2 |
|---|---|---|
| Impact — Layer 1 (tip) | ✅ | — |
| Impact — Layer 2 (context, doar FollowUp) | ✅ | — |
| Impact — Layer 3 (progres real relație) | ❌ | ✅ (necesită `state_history` pentru Contact) |
| Timp (retrospectiv, pentru DIS) | ✅ decis, confirmat | — |
| **Vechime** (live, pentru `PriorityScore`) | ✅ decis, confirmat | — |
| Încărcare (formulă) | ✅ | — |
| Încărcare (rol în agregare) | ✅ filtru post-scoring | — |
| Urgență (concept + sursă date) | ✅ (doar FollowUp) | — |
| Urgență (praguri numerice) | ✅ decis, confirmat | — |
| Urgență pentru Mission/Partner | ❌ (valoare de bază) | ✅ (necesită `scheduled_at` populat real) |
| Formula agregată finală | ❌ TBD | — |
| `HabitEngine`, `Calendar`, `Dashboard` ca intrări | ❌ | post-MVP, nedatat |

---

## 8. Limite cunoscute, explicite

1. **Mission e sistematic dezavantajat** față de FollowUp în Impact și Urgență, nu din decizie de business, ci din lipsă de date (`contact_id`, `scheduled_at` nesetate) — risc real de a subprioritiza Mission-uri, dacă formula agregată nu compensează
2. **`CONVERTED = 0.0` bonus** poate fi interpretat greșit ca "valoare mică" dacă nu e documentat clar în UI/Dashboard — necesită atenție la implementare
3. **`Timp` și `Vechime` sunt concepte distincte, deși similare ca sursă de date** — orice implementare viitoare trebuie să respecte separarea (secțiunea 3bis), nu le trateze ca interschimbabile
4. **Singura decizie rămasă: formula agregată** `PriorityScore = f(Impact, Vechime, Urgență)` — restul componentelor sunt închise

---

## 9. Teste necesare înainte de implementare (checklist, nu implementate încă)

- [ ] Impact: Mission → mereu `1.0`, indiferent de context
- [ ] Impact: Partner → mereu `2.0`
- [ ] Impact: FollowUp × 4 contexte → `1.0`/`1.5`/`2.0`/`1.0` (ARCHIVED/NEW/ACTIVE/CONVERTED)
- [ ] Timp: calculat corect din `state_history`, pentru toate 3 tipuri (doar entități `COMPLETED`)
- [ ] Timp: **nu se calculează** pentru entități încă deschise — folosesc `Vechime`, nu `Timp`, în acel caz
- [ ] Vechime: calculat corect (`ACUM − created_at`), pentru toate 3 tipuri, doar pe entități încă deschise
- [ ] Urgență FollowUp × 4 praguri → `1.00`/`1.33`/`1.67`/`2.00` (Îndepărtat/Apropiat/Azi/Depășit)
- [ ] Urgență: un FollowUp depășit cu 10 minute și unul depășit cu 3 zile → **aceeași valoare** (`2.00`, plat, confirmat)
- [ ] Urgență: Mission/Partner → mereu `1.0`
- [ ] Încărcare: numărătoare corectă, izolată per `owner_id` (verificare de securitate, ca la toate celelalte azi)
- [ ] `PriorityScore` **nu folosește Încărcarea** — verificat explicit, nu presupus
- [ ] `PriorityScore` **nu folosește `Timp`** (retrospectiv) — folosește `Vechime` (live) — verificat explicit
- [ ] Modificarea numărului de activități active **nu modifică scorul individual** al unei activități
- [ ] Încărcarea afectează doar **numărul de activități selectate în Planul Zilei**, nu ordinea/scorul lor
- [ ] Test de regresie: cele 115+ teste existente rămân verzi

---

## 10. Următorul pas real

**Nu cod încă.** Rămâne **o singură** decizie de business explicită, înainte de implementare (Impact, Timp, Vechime, Încărcare, Urgență — toate închise, niciuna nu se redeschide):

**Formula agregată finală** — cum se combină `Impact + Vechime + Urgență` într-un `PriorityScore`.

---
*Document canonic. Fiecare valoare din secțiunile 2-3bis, 5 e verificată din cod/schemă reală sau confirmată explicit de Nic. Singurul TBD rămas e marcat explicit, nu completat cu presupuneri.*
