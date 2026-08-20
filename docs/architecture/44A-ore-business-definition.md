# Decizia 44A — ORE Business Definition

Status: ÎN LUCRU (owner, 20 august 2026) — 11 din 13 puncte decizionale
înghețate. Rămân deschise, ca parametri de calibrare fără bază de
business găsită: **5a** (lungimea ferestrei mobile de agregare) și
**6a** (pragul minim de intervenții pentru afișarea unui procent).

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

## 10. Cum intră ulterior în OPI — 🔒 ÎNGHEȚAT (deferat)

> Integrarea ORE în OPI **nu poate fi decisă izolat**. `OPI` are o
> structură formală definită (`OPI = Σ(wᵢ × KPIᵢ)`, `Σwᵢ = 1`), dar
> **nicio pondere `wᵢ` concretă nu există pentru niciunul dintre cei
> 12 KPI operaționali**, iar formula proprie a OPI rămâne `PROPOSED`,
> identic ca statut cu ORE. Decizia ponderii ORE în OPI trebuie luată
> ca parte a unei decizii de business separate și mai ample —
> definirea completă a OPI — nu inventată izolat aici. Politica
> documentată pentru date lipsă (`03-rule-model-001.md`, secțiunea 17:
> „un input lipsă nu primește automat 0”, statusuri
> `MISSING`/`NOT_APPLICABLE`) confirmă independent principiul deja
> înghețat la Punctul 6 pentru ORE.
>
> **Notă tehnică de consemnat pentru contractul viitor**: frecvența
> documentată a OPI (`EVENT-DRIVEN + DAILY`) presupune un model de
> snapshot periodic, în tensiune cu decizia de la Punctul 8 (ORE
> calculat live, fără persistare) — de rezolvat explicit când se
> definește integrarea, nu presupus acum.

**Verificare de audit efectuată**: `KPI-ARCH-001` (documentul care ar
conține politica oficială de date lipsă) **nu există în repo**, la fel
ca `KPI-MODEL-001`. Nicio valoare `wᵢ` concretă nu apare nicăieri
pentru niciunul dintre cei 12 KPI.

**Descoperire de validare independentă**: regula deja înghețată la
Punctul 6 pentru ORE (`"date insuficiente" ≠ 0%`) e confirmată,
independent, de politica arhitecturală transversală deja documentată
pentru toată familia de KPI (`03-rule-model-001.md`, secțiunea 17).
ORE nu doar corect semantic — e aliniat cu o regulă deja existentă la
nivel de sistem, descoperită abia acum.

## 11. Ce NU măsoară ORE — 🔒 ÎNGHEȚAT

> ORE este o metrică descriptivă a progresului observabil după
> intervențiile eligibile asupra obiecțiilor; nu este o metrică de
> competență generală, cauzalitate, satisfacție, conversie comercială
> sau performanță comparativă între lideri.

**Interpretare corectă vs. incorectă, consemnată explicit**:
- ❌ *"Nic are ORE 40%, deci Nic este un lider slab."*
- ✅ *"În setul de intervenții eligibile și maturizate incluse în
  calcul, 40% au fost urmate de un FollowUp creat în fereastra
  definită."*

**A — excluderi deja stabilite prin punctele anterioare (consolidate):**
1. Auto-declararea liderului că a rezolvat obiecția
2. Preferința pentru varianta de răspuns
3. Simpla continuare a conversației
4. Rezolvarea obiectivă a obiecției
5. O relație cauzală demonstrată între răspuns și progres
6. Intervențiile `BLOCK`
7. Obiecțiile fără `conversation_id`
8. Follow-up-urile marcate `COMPLETED` ca dovadă de progres
9. Conversia în `Partner`

**B — limite semantice explicite, noi:**
10. Competența generală a liderului
11. Dificultatea obiecțiilor gestionate
12. Satisfacția generală a prospectului/clientului
13. Rezultatul comercial final (conversie, vânzare)
14. Viteza de răspuns a liderului
15. Clasamentul sau ierarhizarea liderilor — **ORE nu este definit ca
    metrică de clasament sau ierarhizare între lideri**; două valori
    pot fi comparate tehnic, dar contractul nu autorizează un
    leaderboard/ranking fără o decizie de business separată
16. Un predictor statistic/econometric validat al succesului comercial
    pe termen lung
17. Contextul extern al prospectului (indisponibilitate,
    circumstanțe, independent de calitatea răspunsului)

**Notă de implementare reținută, dar nu decisă acum**: punctele B10 și
B15 (competența generală, clasamentul) au risc real de interpretare
greșită în afara sistemului (discuții de management), nu doar risc
tehnic — merită reflectate ulterior explicit în eticheta din
Workbench, similar cu "valoare operațională curentă" de la DIS. Decizia
de UX rămâne separată, ulterioară înghețării contractului de business.

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
| 10 | Integrare în OPI | 🔒 deferat explicit — depinde de definiția completă a OPI |
| 11 | Ce NU măsoară (listă explicită) | 🔒 A1-A9 + B10-B17 |

**11 din 13 puncte decizionale înghețate.** Rămân deschise exclusiv
**5a** și **6a** — doi parametri de calibrare numerică, fără bază de
business documentată găsită prin audit exhaustiv, spre deosebire de
toate celelalte valori din acest document (7 zile, scala 0-100,
excluderile), toate ancorate fie în documentație existentă, fie în
raționament de business explicit aprobat.

**Nu se scrie contractul tehnic final** până când 5a și 6a sunt
rezolvate — fie empiric (după acumularea de date reale din utilizare),
fie printr-o decizie de business separată, dacă apare un reper nou.
