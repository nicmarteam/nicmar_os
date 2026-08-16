# PRIORITY ENGINE — SPECIFICAȚIE v1

**Status:** specificație de logică, verificată din surse reale — **nu e cod, nu e implementare**
**Data:** 12 august 2026 (continuare, aceeași sesiune)
**Scop:** îngheață deciziile luate azi despre `PriorityEngine v1`, înainte de orice linie de cod

---

## 0. Ce NU e acest document

Nu e cod, nu e implementare. **Este acum o specificație de decizie completă** — toate componentele (Impact, Timp, Vechime, Încărcare, Urgență, Formula agregată) au fost verificate din surse/cod real sau confirmate explicit, fără valori inventate. Zero TBD rămase.

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

**Rol: retrospectiv, pentru `DIS`/analiză — NU e input live pentru `PriorityKey`** (v. secțiunea 3bis pentru distincția de `Vechime`).

```
Mission:   state_history(new_state='COMPLETED').created_at − missions.created_at
FollowUp:  state_history(new_state='COMPLETED').created_at − follow_ups.created_at
Partner:   events('PartnerInteractionCompleted').created_at
           − events('PartnerDiagnosticGenerated').created_at
```

Toate 3 derivate din timestamp-uri deja scrise de codul existent — fără câmpuri noi, fără presupuneri. **Confirmat explicit de Nic.**

**Limitare structurală, descoperită la definirea formulei agregate:** `Timp` se calculează *doar după* `COMPLETED` — inutilizabil ca input pentru `PriorityKey`, care trebuie să decidă prioritatea printre activități **încă neterminate** (`PENDING`/`IN_PROGRESS`), care n-au încă timestamp de finalizare. De aici, secțiunea următoare.

---

## 3bis. Vechime v1 — ✅ DECIS, concept nou, distinct de Timp

**Rol: live, input real pentru `PriorityKey`** — răspunde la *"de cât timp așteaptă asta, acum"*, nu *"cât a durat, retrospectiv"*.

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
**Încărcarea NU modifică `PriorityKey` al unei activități.** E filtru aplicat **după** sortare — determină câte activități din vârful listei intră în Planul Zilei, nu cum se calculează scorul fiecăreia.

```
Flux: Impact + Vechime + Urgență → PriorityKey → sortare → filtru Încărcare → Planul Zilei (3-5 acțiuni)
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

## 6. Formula agregată — ✅ DECIS, ordine lexicografică

**Nu sumă ponderată** — respinsă explicit, fiindcă ar permite unui scor mare de Urgență/Vechime să compenseze un Impact inferior, contrazicând ancora găsită în sursă.

### Ancora textuală, singurul sprijin documentat pentru ierarhie
> *"Utilizatorul începe să lucreze după impact, nu după urgență."* (`05`, secțiunea PriorityEngine, "PARTEA C — Audit de implementare")

Corroborare slabă suplimentară: ordinea enumerării proceselor `PriorityEngine` (*"calcul impact; calcul urgență; calcul timp..."*) pune Impact înaintea Urgenței.

**Nicio sursă nu compară `Vechime` cu `Impact` sau `Urgență`** — poziția ei (ultimul criteriu) e decizie de business explicită, nu documentată, dar consecventă cu rolul ei de "departajare la egalitate", nu de magnitudine proprie.

### `PriorityKey` — nu formulă numerică, cheie de sortare
```
PriorityKey = (Impact DESC, Urgență DESC, Vechime DESC)
```

1. **Impact decide primul, mereu** — o activitate cu Impact inferior nu poate depăși una cu Impact superior, indiferent de Urgență/Vechime
2. **Urgență** — tiebreaker, doar dacă Impact e egal
3. **Vechime** — tiebreaker final, doar dacă Impact ȘI Urgență sunt egale

### Exemplu de verificare
| Activitate | Impact | Urgență | Vechime | Ordine |
|---|---:|---:|---:|---|
| A — FollowUp ACTIVE | 2.0 | 1.0 | 80 | 1 |
| B — FollowUp ACTIVE | 2.0 | 2.0 | 20 | 2 |
| C — Mission | 1.0 | 2.0 | 90 | 3 |

C, deși foarte urgent și foarte vechi, nu poate depăși A/B — Impact inferior decide.

### Flux complet, final
```
PriorityKey → sortare → filtru Încărcare → Planul Zilei (3-5 acțiuni)
```

---

## 7. Ce intră în v1 vs. rămâne v2

| Componentă | v1 | v2 |
|---|---|---|
| Impact — Layer 1 (tip) | ✅ | — |
| Impact — Layer 2 (context, doar FollowUp) | ✅ | — |
| Impact — Layer 3 (progres real relație) | ❌ | ✅ (necesită `state_history` pentru Contact) |
| Timp (retrospectiv, pentru DIS) | ✅ decis, confirmat | — |
| **Vechime** (live, pentru `PriorityKey`) | ✅ decis, confirmat | — |
| Încărcare (formulă) | ✅ | — |
| Încărcare (rol în agregare) | ✅ filtru post-scoring | — |
| Urgență (concept + sursă date) | ✅ (doar FollowUp) | — |
| Urgență (praguri numerice) | ✅ decis, confirmat | — |
| Urgență pentru Mission/Partner | ❌ (valoare de bază) | ✅ (necesită `scheduled_at` populat real) |
| **Formula agregată (`PriorityKey`, ordine lexicografică)** | ✅ decis, confirmat | — |
| `HabitEngine`, `Calendar`, `Dashboard` ca intrări | ❌ | post-MVP, nedatat |

---

## 8. Limite cunoscute, explicite

1. **Mission e sistematic dezavantajat** față de FollowUp în Impact și Urgență, nu din decizie de business, ci din lipsă de date (`contact_id`, `scheduled_at` nesetate). **Ordinea lexicografică amplifică asta**, nu o atenuează: un Mission nu poate depăși niciodată un FollowUp `ACTIVE`, indiferent cât de veche e misiunea — risc real de a bloca sistematic Mission-urile la coada listei
2. **`CONVERTED = 0.0` bonus** poate fi interpretat greșit ca "valoare mică" dacă nu e documentat clar în UI/Dashboard — necesită atenție la implementare
3. **`Timp` și `Vechime` sunt concepte distincte, deși similare ca sursă de date** — orice implementare viitoare trebuie să respecte separarea (secțiunea 3bis), nu le trateze ca interschimbabile
4. **Ordinea lexicografică e strictă, nu graduală** — o diferență infimă de Impact (`1.0` vs `1.5`) domină complet o diferență masivă de Urgență/Vechime; acceptat explicit ca decizie corectă (ancora din sursă), dar efectul practic trebuie verificat cu date reale înainte de lansare

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
- [ ] `PriorityKey` **nu folosește Încărcarea** — verificat explicit, nu presupus
- [ ] `PriorityKey` **nu folosește `Timp`** (retrospectiv) — folosește `Vechime` (live) — verificat explicit
- [ ] **Sortare lexicografică, nu sumă**: o activitate cu Impact `1.0` nu poate niciodată depăși una cu Impact `2.0`, indiferent de Urgență/Vechime — testat explicit cu cazul din secțiunea 6 (exemplul A/B/C)
- [ ] Modificarea numărului de activități active **nu modifică scorul individual** al unei activități
- [ ] Încărcarea afectează doar **numărul de activități selectate în Planul Zilei**, nu ordinea/scorul lor
- [ ] Test de regresie: cele 115+ teste existente rămân verzi

---

## 10. Următorul pas real

**Toate deciziile de business sunt închise.** Impact, Timp, Vechime, Încărcare, Urgență, Formula agregată — toate confirmate explicit, niciuna nu se redeschide.

`PriorityEngine v1` e acum suficient de specificat pentru implementare: contract → cod → cele 3 verificări (sintaxă, audit contractual, teste unitare) → test de integrare stateful → PostgreSQL real → regresie completă — aceeași disciplină aplicată la Mission/FollowUp/Partner.

---
*Document canonic, ÎNCHIS. Fiecare valoare din secțiunile 2-6 e verificată din cod/schemă reală sau confirmată explicit de Nic. Zero TBD rămase.*
