# Decizia 44A — ORE Business Definition

Status: ÎN LUCRU (owner, 20 august 2026) — Punctele 1-4, 3A, 3B, 5
(principiu), 6 (principiu), 8, 9 înghețate. Punctele 5a, 6a, 10, 11
rămân deschise.

## 0. Context și regulă de lucru

Decizia 44 (implementarea tehnică a ORE) a fost blocată explicit
(`44-objection-ore-status.md`) după ce auditul a demonstrat că ORE nu
are nicio formulă, componente sau date necesare definite oficial
nicăieri — doar o mențiune în registrul KPI care trimite la un
document (`KPI-MODEL-001`) inexistent în repo.

Regula de lucru pentru 44A, respectată strict pe tot parcursul:
**definiție de business → contract tehnic → cod**, niciodată invers.
Fiecare punct a fost analizat pe criterii explicite (ce măsoară, ce
comportament reflectă, ce date necesită, ce risc de interpretare are,
compatibilitate cu filosofia deja aplicată în restul sistemului)
înainte de a fi înghețat. Acolo unde auditul nu a găsit o bază de
business reală pentru o valoare numerică, valoarea a rămas explicit
deschisă — nu a fost inventată.

**Nu s-a scris niciun cod în această decizie.**

## 1. Ce măsoară ORE — 🔒 ÎNGHEȚAT

> ORE trebuie să fie orientat către eficiența reală a intervenției
> asupra obiecției, nu către preferința liderului, auto-raportarea lui
> sau simpla utilizare a unei variante de răspuns. Reacția/rezultatul
> prospectului este direcția conceptuală preferată, dar mecanismul
> exact de măsurare rămâne de definit. Rezultatul conversației
> (Opțiunea 2) rămâne disponibil ca semnal secundar de validare, nu ca
> substitut al reacției prospectului.

Opțiuni respinse explicit: varianta de răspuns folosită (măsoară
preferință, nu eficiență), auto-declararea liderului (risc Goodhart),
combinație ponderată (prematur, ascunde incertitudine într-o formulă).

## 2. Ce rezultat exact măsoară — 🔒 ÎNGHEȚAT

> ORE măsoară progresul concret **observat după** intervenția asupra
> obiecției — avansare observabilă printr-un follow-up nou, o
> programare sau un alt pas concret în relație. Nu măsoară rezolvarea
> declarativă a obiecției și nu presupune că progresul observat a fost
> cauzat exclusiv de răspunsul liderului. Confirmarea explicită a
> prospectului rămâne ținta conceptuală pe termen lung, spre care acest
> semnal proxy se poate apropia ulterior, dacă va exista un canal real
> de colectare.

Distincție reținută: "obiecția a fost rezolvată" (A) vs. "intervenția
a produs progres" (B) — aleasă B, restrânsă la avansare comportamentală
observabilă, nu declarativă.

## 3A. Fereastra temporală de observație — 🔒 ÎNGHEȚAT

> Fereastra temporală ORE este de maximum **7 zile** de la momentul
> `ObjectionResponseSubmitted`. Această durată este fundamentată pe
> ritmul comercial deja definit în NicMar OS prin „Legea
> Continuității”, care include explicit opțiunea „Săptămâna viitoare”.
> Evenimentele relevante observate după această fereastră nu sunt
> atribuite intervenției respective pentru calculul ORE. Fereastra de
> 7 zile stabilește doar limita temporală de observare și nu implică o
> relație cauzală între intervenție și evenimentul observat.

**Sursă de business confirmată**: `05-competente-37-motor1.md`,
secțiunea „Programarea Inteligentă a Următorului Pas (Legea
Continuității)” — patru opțiuni exacte oferite liderului: Mâine
(~24h), Peste 2 zile (~48h), Săptămâna viitoare (~7 zile), Aleg eu
data. 7 zile e cea mai largă fereastră cu susținere explicită în UX-ul
deja proiectat.

`scheduled_at` (intenția liderului) exclusă explicit ca sursă a
ferestrei — ar lăsa liderul să controleze indirect limita metricii.

## 3B. Semnalul observabil — 🔒 ÎNGHEȚAT

> Există un `FollowUp` nou, asociat aceleiași conversații cu obiecția,
> creat în maximum 7 zile de la `ObjectionResponseSubmitted`.

**Excluderi explicite, cu motivare:**
- `FollowUp.COMPLETED` — exclus din semnalul de bază: confirmare
  declarativă a liderului, reintroduce riscul Goodhart deja respins la
  Punctul 1
- `Partner` creat — exclus din ORE v1: semnal puternic dar rar și
  tardiv; păstrat ca semnal candidat pentru o versiune viitoare, nu ca
  a doua treaptă a scorului actual
- `conversations.status` — exclus definitiv: **verificat direct în
  cod, zero `UPDATE conversations ... SET status` există în tot
  `src/`** — statusul rămâne fix la valoarea de creare, nu există
  nicio tranziție de observat
- Inferența prin `contact_id` — exclusă când `objections.conversation_id
  IS NULL` (nullable în schemă) — fără lanțul obiectiv
  `objection → conversation → follow_up`, ORE nu se calculează pentru
  acea intervenție

**Principiu explicit reținut**: absența FollowUp-ului în 7 zile nu
demonstrează că intervenția a eșuat — demonstrează doar că sistemul nu
a observat semnalul de progres definit în fereastră.

## 4. Date eligibile — 🔒 ÎNGHEȚAT

> ORE utilizează numai intervențiile `ObjectionResponseSubmitted` care
> reprezintă un răspuns efectiv persistat. Sunt eligibile nivelurile
> `PASS`, `PARTIAL_VALIDATION` și `HUMAN_REVIEW`. Evenimentele `BLOCK`
> sunt excluse complet din calcul, deoarece răspunsul nu a fost
> trimis/persistat și, prin urmare, nu a existat o intervenție
> efectivă asupra prospectului. Un `BLOCK` nu este considerat nici
> succes, nici eșec ORE și nu intră în numitorul KPI-ului.

Lanțul minim de date confirmat:

```
ObjectionResponseSubmitted
   ├── validation_level ∈ {PASS, PARTIAL_VALIDATION, HUMAN_REVIEW}
   ├── persisted = true
   └── objection_id → objections.conversation_id → follow_ups.conversation_id
                                                        └── created_at ≤ 7 zile
```

izolat prin `owner_id`. Toate datele brute necesare există deja în
schema curentă — zero migrare nouă necesară pentru acest lanț.

## 5. Agregarea — 🔒 ÎNGHEȚAT (principiu) / 🟡 DESCHIS (parametru)

> ORE este o rată calculată exclusiv pe intervențiile maturizate
> (vârstă ≥ 7 zile) dintr-o fereastră temporală mobilă. Intervențiile
> aflate încă în perioada de observație de 7 zile sunt excluse complet
> — nu contează ca 0, nu intră în numărător, nu intră în numitor.
> Lungimea exactă a ferestrei mobile de agregare rămâne un parametru
> tehnic nedecis — spre deosebire de fereastra de maturare de 7 zile
> (ancorată în „Legea Continuității”), nu există în prezent nicio bază
> de business documentată pentru o valoare specifică. Acest parametru
> va fi stabilit fie empiric, fie printr-o decizie de business
> separată, înainte de scrierea contractului tehnic final al ORE.

Formula conceptuală, fără lungimea ferestrei aleasă:

```
ORE = (intervenții maturizate cu FollowUp) / (total intervenții maturizate) × 100
```

ambele componente filtrate în aceeași fereastră mobilă.

**Căutare de audit efectuată, fără rezultat**: nu există în
documentație niciun echivalent al „Legii Continuității” pentru o
perioadă de agregare (30/60/90 zile). Singurul tipar de cadență
documentat e zilnic (`Mission`, `DailyPlan`, `DailyReview`), dar
descrie ritmul de lucru al liderului, nu o fereastră de agregare
istorică pentru un KPI.

Respinse explicit: agregare all-time (istoricul vechi ar masca
deteriorarea recentă), agregare pe ultimele N intervenții (prag la
fel de arbitrar ca lungimea ferestrei, plus volatilitate mare pentru
lideri cu puține intervenții).

## 6. Scală și interpretare — 🔒 ÎNGHEȚAT (principiu) / 🟡 DESCHIS (parametru)

> ORE este exprimat ca procent (0–100), calculat direct din rata
> definită la Punctul 5, fără transformări sau ponderi suplimentare.
> Scorul nu are etichete calitative atașate automat (ex.
> „slab”/„bun”) — orice interpretare de acest tip rămâne o decizie de
> business separată, neluată încă. Sub un prag minim de intervenții
> maturizate, ORE nu se afișează ca procent, ci ca stare explicită
> „date insuficiente” — exact ca `dis_score: null` afișat astăzi ca
> „-”, nu ca `0`. Pragul minim exact (N) rămâne, la fel ca lungimea
> ferestrei mobile (Punctul 5), un parametru tehnic nedecis, fără bază
> de business documentată în acest moment.

Distincție reținută explicit pentru contract: **`0%` ≠ „date
insuficiente”**. `0%` înseamnă date suficiente, dar niciun progres
observat. „Date insuficiente” înseamnă eșantion prea mic pentru ca
procentul să fie informativ.

## 8. Când se calculează — 🔒 ÎNGHEȚAT

> ORE se calculează live, la citire, din datele brute existente, fără
> persistare proprie în `scores` și fără job periodic. La fiecare
> calcul, sistemul identifică intervențiile eligibile și maturizate,
> aplică fereastra mobilă de agregare și verifică existența unui
> `FollowUp` creat în cele 7 zile de observație. Valoarea afișată
> reflectă astfel starea actuală a datelor, fără întârziere de
> sincronizare.

**Consecință arhitecturală majoră**: ORE e un **KPI derivat**, nu
evenimențial — diferit deliberat de tiparul DIS/PDI/PIP
(`_emit_event` + `INSERT INTO scores`), fără să fie o inconsecvență.
DIS/PDI/PIP răspund la „ce a rezultat din ultimul eveniment?"; ORE
răspunde la „care e rata actuală din setul relevant de intervenții?".
Arhitectural mai apropiat de `PriorityEngine` (citire/calcul pur, zero
scriere) decât de celelalte KPI. Zero infrastructură nouă necesară
(fără job scheduler).

| Aspect | Decizie |
|---|---|
| Calcul | Live |
| Persistare `scores` | Nu |
| Job scheduler | Nu |
| Snapshot istoric ORE | Nu în v1 |
| Sursa adevărului | Datele operaționale brute |
| Recalculare | La fiecare citire |

## 9. Ce evenimente îl actualizează — 🔒 ÎNGHEȚAT

> ORE nu este actualizat prin emiterea unui eveniment KPI și nu
> generează rânduri în `scores`. Valoarea sa se modifică implicit
> atunci când se modifică sau devin eligibile datele operaționale din
> care este calculat.

Nu se introduce un eveniment `OREUpdated` — nu are nicio necesitate
reală, dat fiind Punctul 8. Datele operaționale care pot schimba
rezultatul: crearea de noi `ObjectionResponseSubmitted` eligibile,
crearea de noi `FollowUp`, trecerea timpului (maturizarea
intervențiilor).

## 10. Cum intră ulterior în OPI — 🟡 DESCHIS

Neanalizat încă. `OPI` (Overall Performance Index) e compozit din cei
12 KPI operaționali (`04-KPI-REG-001.md`), dar propria lui formulă e
tot `PROPOSED`/nedefinită. Dependent de rezolvarea parametrilor
deschiși de mai sus (5a, 6a) și de propria definiție a OPI, care nu a
fost auditată în cadrul acestei decizii.

## 11. Ce NU măsoară ORE — 🟡 DESCHIS

Neanalizat explicit ca punct separat, deși implicit consemnat prin
excluderile din Punctele 1, 3B, 4. De formalizat ca listă explicită
înainte de contractul tehnic final, pentru a preveni ambiguități
viitoare (cerința inițială a owner-ului).

## 12. Status consolidat

| Punct | Subiect | Status |
|---|---|---|
| 1 | Ce înseamnă eficiență | 🔒 |
| 2 | Ce rezultat măsurăm | 🔒 |
| 3A | Fereastra de observație | 🔒 7 zile |
| 3B | Semnal observabil | 🔒 FollowUp creat |
| 4 | Date eligibile | 🔒 persisted / BLOCK exclus |
| 5 | Agregare (principiu) | 🔒 fereastră mobilă |
| 5a | Lungimea ferestrei mobile | 🟡 deschis — fără bază de business |
| 6 | Scală și semantică (principiu) | 🔒 0–100, fără etichete calitative |
| 6a | Prag minim N | 🟡 deschis — fără bază de business |
| 8 | Când se calculează | 🔒 live, fără persistare |
| 9 | Ce evenimente îl actualizează | 🔒 niciunul direct |
| 10 | Integrare în OPI | 🟡 deschis — neanalizat |
| 11 | Ce NU măsoară (listă explicită) | 🟡 deschis — neformalizat |

**Nu se scrie contractul tehnic final** până când Punctele 10 și 11
sunt rezolvate și, opțional, până când 5a/6a primesc fie o bază de
business, fie o decizie explicită de a le stabili empiric/tehnic.
