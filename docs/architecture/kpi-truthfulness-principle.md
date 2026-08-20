# KPI Truthfulness Principle

Status: ACTIV (owner, 20 august 2026)

**Natură**: regulă nouă de guvernanță arhitecturală, introdusă acum.
Nu este o regulă găsită în documentația existentă a NicMar OS —
este derivată din disciplina aplicată și validată în practică la
Decizia 44A (ORE Business Definition), și devine de acum standard
obligatoriu pentru orice KPI viitor. 44A rămâne exemplul de aplicare,
nu sursa regulii.

## 1. Purpose

Acest document definește standardul obligatoriu pentru proiectarea,
analiza și aprobarea oricărui KPI nou din NicMar OS, înainte ca acel
KPI să primească un contract tehnic sau cod de implementare.

Scopul nu este să încetinească dezvoltarea, ci să prevină un risc
specific, deja identificat concret în proiect: introducerea unui scor
numeric care pare precis, dar care de fapt ascunde o incertitudine
nefundamentată — fie în formulă, fie în parametrii ei, fie în ce
pretinde că demonstrează.

## 2. Principiul fundamental

> **Un KPI NicMar OS nu are voie să pretindă mai mult decât pot
> demonstra datele sale.**

Pentru fiecare KPI trebuie definit explicit:
- ce observă
- ce calculează
- ce nu observă
- ce nu măsoară
- ce nu poate demonstra
- ce presupuneri sunt necesare
- ce parametri sunt fundamentați de business
- ce parametri rămân calibrare
- când datele sunt insuficiente pentru un scor valid

Și, separat, o a doua regulă la fel de obligatorie:

> **Lipsa unei dovezi nu se transformă automat într-o valoare
> numerică.**

## 3. Ce trebuie demonstrat înainte de definirea unui KPI

Înainte ca un KPI să treacă de la "propunere" la "contract tehnic",
trebuie demonstrat, cu dovadă verificabilă (cod, schemă DB, sau
documentație de business existentă — nu presupunere):

1. Ce anume, concret, măsoară acest KPI (nu o formulă vagă de tipul
   "eficiență" sau "performanță", ci un rezultat observabil precis)
2. Ce date există deja în sistem care pot fundamenta acest KPI, sau ce
   date noi ar trebui colectate — și costul/fezabilitatea colectării
3. Ce semnal concret din sistem reprezintă efectiv KPI-ul (un
   eveniment, o tranziție de stare, o valoare calculată) — nu doar o
   intenție declarată

Dacă niciuna dintre aceste trei nu poate fi demonstrată din surse
reale, KPI-ul rămâne `PROPOSED`, nu avansează spre `DRAFT`.

## 4. Observed vs. inferred vs. causal

Fiecare afirmație făcută despre ce reprezintă un KPI trebuie
clasificată explicit în una din trei categorii, iar aceste categorii
nu se confundă niciodată în formulare:

| Categorie | Ce înseamnă | Exemplu valid |
|---|---|---|
| **Observed** | Un fapt înregistrat direct în sistem, verificabil | "A fost creat un `FollowUp` în 7 zile" |
| **Inferred** | O concluzie derivată dintr-un semnal observat, cu limitele ei recunoscute explicit | "Progresul a fost *observat* după intervenție" (nu "produs de") |
| **Causal** | O afirmație de cauzalitate — **interzisă** fără dovadă directă, imposibilă pentru majoritatea semnalelor comportamentale din acest sistem | "Răspunsul liderului *a cauzat* progresul" — nu se afirmă niciodată dintr-un semnal proxy |

Un KPI care formulează o afirmație `causal` fără dovadă directă (ex.
experiment controlat, nu doar corelație observată) nu poate fi
aprobat în această formă.

## 5. Date disponibile vs. date inexistente

Contractul de business al oricărui KPI trebuie să separe explicit:

- **Date deja disponibile** — verificate direct în schema DB și cod,
  nu presupuse
- **Date inexistente, dar necesare** — consemnate ca gol, cu evaluarea
  costului real de colectare (infrastructură nouă? canal extern nou?
  UI nou?), nu tratate ca detaliu minor de implementare

Un KPI nu poate trece la faza de contract tehnic dacă se bazează pe
date inexistente fără ca acest gol să fie explicit recunoscut și
adresat (fie prin construirea colectării, fie prin amânarea KPI-ului).

## 6. Business decisions vs. calibration parameters

Orice parametru numeric dintr-un KPI trebuie clasificat explicit în
una din două categorii, niciodată amestecate:

- **Decizie de business** — o valoare aleasă pentru un motiv de
  business demonstrabil, ancorat în comportament real deja documentat
  al produsului (exemplu: fereastra de 7 zile la ORE, ancorată în
  "Legea Continuității")
- **Parametru de calibrare tehnică** — o valoare fără fundamentare de
  business găsită, care rămâne deschisă, configurabilă, de stabilit
  empiric ulterior, nu aleasă acum din conveniență

Confundarea celor două categorii — prezentarea unei valori de
calibrare nefundamentate ca și cum ar fi o decizie de business — este
exact eroarea pe care acest principiu o interzice.

## 7. No invented parameters

Regulă strictă, fără excepție:

> Înainte ca un parametru numeric să intre într-un contract tehnic:
> **Documentație → Dovadă de business → Date reale → Decizie.**
>
> Dacă dovada nu există: parametrul rămâne **OPEN**, nu se alege "ceva
> rezonabil".

Nicio valoare (fereastră temporală, prag, pondere, scală) nu se
introduce doar pentru că e convenabilă tehnic sau pentru că trebuie
completat un câmp din formulă. Absența unei valori explicite e
preferabilă unei valori inventate care ar da o falsă impresie de
precizie.

## 8. Handling of insufficient data

Un KPI trebuie să distingă explicit, la nivel de contract și de
afișare, între:

- **Rezultat real, calculat, care se întâmplă să fie 0** (sau minim
  pe scală) — datele există, calculul e valid, rezultatul e pur și
  simplu "fără semnal pozitiv observat"
- **Date insuficiente pentru un calcul semnificativ** — eșantion prea
  mic, sau perioadă de observație neîncheiată — caz în care KPI-ul nu
  se afișează ca număr, ci ca stare explicită ("date insuficiente",
  echivalentul `null`/`MISSING`, nu `0`)

Aceste două stări **nu se confundă niciodată**, nici în calcul, nici
în interfață.

## 9. Explicit "Does Not Measure" contract

Fiecare KPI aprobat trebuie să conțină o secțiune separată, explicită,
care enumeră concret ce **nu** măsoară — nu ca observație secundară,
ci ca parte obligatorie a contractului. Minim trebuie adresate:

- Competența generală a persoanei evaluate (KPI-ul nu e un verdict
  global asupra valorii profesionale a cuiva)
- Factori de context extern care pot influența rezultatul independent
  de acțiunea măsurată
- Orice utilizare de tip clasament/ierarhizare comparativă — neautorizată
  implicit prin definiția unui KPI individual, necesită decizie de
  business separată
- Orice pretenție de valoare predictivă statistic validată, dacă
  aceasta nu a fost testată empiric

## 10. Evidence required for each decision

Fiecare decizie luată în definirea unui KPI (ce măsoară, fereastra
temporală, semnalul folosit, excluderile) trebuie însoțită de sursa ei
exactă:

- Citat/referință verbatim din documentația de arhitectură existentă,
  dacă există, sau
- Verificare explicită prin cod (ex. "verificat direct în
  `X.py`, linia Y: nu există niciun `UPDATE` pe acest câmp"), sau
- Raționament de business explicit, aprobat de owner, consemnat ca
  atare — nu prezentat ca "fapt găsit", dacă a fost de fapt o alegere

Absența unei surse pentru o afirmație e un motiv suficient să nu fie
inclusă în contract.

## 11. When a KPI must rămâne BLOCKED

Un KPI trebuie să rămână explicit `BLOCKED` (nu implementat cu
valoare placeholder, nu forțat cu o formulă inventată) atunci când:

- Definiția lui de business nu e completă (ce măsoară, ce nu măsoară)
- Semnalul ales pentru calcul nu există încă în date, iar colectarea
  lui necesită infrastructură nouă neaprobată încă
- Parametrii de calibrare rămân deschiși și nu există o cale
  rezonabilă de a-i stabili empiric în timp util

`BLOCKED` printr-o decizie explicită, documentată și motivată este un
rezultat legitim și preferabil unei implementări premature. Blocajul
nu e o datorie tehnică — e o decizie de calitate.

## 12. Application to ORE — 44A ca exemplu, nu ca regulă

`44A-ore-business-definition.md` e prima aplicare completă a acestui
principiu, dar principiul nu derivă autoritatea din ORE — e o regulă
generală, ORE e doar cazul concret care a forțat-o să fie articulată.
Orice element specific ORE (fereastra de 7 zile, semnalul `FollowUp
created`, excluderea `BLOCK`) rămâne particular acelui KPI — nu se
generalizează automat la alte KPI-uri viitoare fără propria lor
analiză, condusă după acest principiu de la zero.

## 13. Checklist obligatoriu pentru viitorii KPI

Înainte ca un contract tehnic de KPI să fie scris, toate punctele de
mai jos trebuie bifate explicit, cu sursă/dovadă pentru fiecare:

- [ ] Ce măsoară KPI-ul — formulat ca rezultat observabil, nu concept vag
- [ ] Ce NU măsoară — secțiune explicită, minim 3-5 excluderi concrete
- [ ] Ce date există deja (verificate în cod/schemă, nu presupuse)
- [ ] Ce date lipsesc și ce cost real ar avea colectarea lor
- [ ] Fiecare parametru numeric — clasificat explicit: decizie de
      business (cu sursă) sau parametru de calibrare (marcat deschis)
- [ ] Comportamentul exact pentru date insuficiente (stare distinctă
      de 0/valoare minimă)
- [ ] Afirmațiile de tip observed/inferred/causal — verificate să nu
      alunece spre causal fără dovadă
- [ ] Momentul și mecanismul de calcul (live vs. persistat, evenimente
      care îl actualizează sau motiv explicit pentru absența lor)
- [ ] Dacă intră într-un KPI compus (ex. OPI) — pondere fundamentată
      sau explicit deferată, nu inventată izolat
- [ ] Decizie finală: `APPROVED` pentru contract tehnic, sau `BLOCKED`
      cu motiv explicit documentat
