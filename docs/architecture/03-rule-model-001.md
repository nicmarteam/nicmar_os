# NicMar OS — Document 07: Rule Definition & Evaluation Model (RULE-MODEL-001)

*Sursă: _RULE-MODEL-001___Rule_Definition___Evaluation_Model.txt*

**⚠️ NOTĂ IMPORTANTĂ:** Acest fișier conține, printre altele, draftul original al secțiunilor KPI-REG-001 și KPI-MODEL-001 §3 (Nivelul 6). Acele secțiuni sunt **depășite** — documentul canonic pentru registrul KPI este acum `KPI-REG-001.md`, care rezolvă și conflictul PES/ORE găsit în acest draft. Restul documentului (Rule Definition & Evaluation Model, Nivelul 5) rămâne valabil ca sursă.

---

﻿NicMar OS – Core Architecture – Document 07.1
RULE-MODEL-001
Rule Definition & Evaluation Model
Business Domain: Core Architecture / Rules & Decision Architecture
Nivel: Nivelul 5 – Rules & Decision Architecture
Versiune: 1.0
Status: 🟡 Propunere pentru validare
Metodologie: Declarative & Deterministic Rule Engine Architecture
SSOT Sursă: RULE-ARCH-001
Dependințe:
* Documentul 01 – Business Objects
* DB-ARCH-001
* DB-BO-001
* DB-REL-001
* DB-STATE-001
* DB-EVENT-001
* DB-AUDIT-001
* ENG-ARCH-001
* Nivelul 3 – Workflow Architecture
________________


1. Scopul Documentului
RULE-MODEL-001 definește modelul tehnic standard prin care regulile de business din NicMar OS sunt:
* definite;
* identificate;
* versionate;
* activate;
* evaluate;
* executate;
* explicate;
* auditate;
* testate;
* dezactivate.
Documentul reprezintă modelul tehnic derivat din RULE-ARCH-001.
RULE-ARCH-001 definește arhitectura și principiile stratului de reguli.
RULE-MODEL-001 definește structura concretă a unei reguli și mecanismul standard de evaluare.
________________


2. Poziționarea în Arhitectura NicMar OS
Fluxul oficial este:
EVENT
   ↓
WORKFLOW
   ↓
ENGINE
   ↓
RULE ENGINE
   ↓
RULE EVALUATION
   ↓
DECISION OUTCOME
   ↓
STATE / EVENT / WORKFLOW / KPI
   ↓
AUDITLOG


Regula reprezintă unitatea logică minimă de decizie a stratului Rules & Decision.
Engine-ul furnizează contextul și solicită evaluarea.
Rule Engine identifică regulile aplicabile, le evaluează și returnează rezultatul standardizat.
Engine-ul utilizează rezultatul pentru continuarea procesului operațional.
________________


3. Principiul Fundamental
O regulă trebuie să producă același rezultat atunci când primește același context de intrare și aceeași versiune de regulă.
Same Context
      +
Same Rule Version
      ↓
Same Decision Outcome


Rezultatul unei reguli este determinist și trasabil.
________________


4. Structura Canonica a unei Reguli
Fiecare regulă NicMar OS are următoarea structură logică:
Rule
│
├── Identity
├── Ownership
├── Target
├── Trigger
├── Context
├── Conditions
├── Thresholds
├── Evaluation
├── Outcome
├── Actions
├── Priority
├── Version
├── Status
└── Audit Metadata


________________


5. Rule Identity
Fiecare regulă primește un identificator unic.
Câmpuri
* rule_id
* rule_code
* rule_name
* rule_version
* rule_type
Exemplu
rule_id: UUID
rule_code: RULE-PARTNER-QUAL-001
rule_name: Partner Qualification
rule_version: 1.0
rule_type: QUALIFICATION


rule_code rămâne identificatorul logic stabil al regulii.
Versiunea se modifică atunci când logica regulii se modifică.
________________


6. Rule Ownership
Fiecare regulă are un proprietar arhitectural și un motor țintă.
Câmpuri
* owner_domain
* owner_engine
* target_object
* target_state_machine
* created_by
* approved_by
Exemplu:
owner_domain: Partner
owner_engine: ENG-PRE-001
target_object: Partner
target_state_machine: SM-PARTNER-001


Regula rămâne asociată responsabilității sale funcționale pe întreg ciclul de viață.
________________


7. Rule Types
Modelul standard acceptă următoarele categorii:
7.1 Qualification
QUALIFICATION


Determină îndeplinirea criteriilor de calificare.
7.2 Threshold
THRESHOLD


Evaluează atingerea unui prag.
7.3 Scoring
SCORING


Determină un scor sau o categorie de scor.
7.4 Prioritization
PRIORITIZATION


Determină prioritatea operațională.
7.5 Transition
TRANSITION


Validează o tranziție permisă în State Machine.
7.6 Conversion
CONVERSION


Evaluează condițiile pentru conversia unui obiect.
7.7 Continuity
CONTINUITY


Evaluează continuitatea activității și condițiile pentru intervenție.
7.8 Notification
NOTIFICATION


Determină condițiile pentru generarea unei notificări.
________________


8. Rule Status
Fiecare regulă are un ciclu de viață propriu:
DRAFT
   ↓
TESTING
   ↓
APPROVED
   ↓
ACTIVE
   ↓
SUSPENDED
   ↓
RETIRED


DRAFT
Regula este în construcție.
TESTING
Regula este evaluată în mediul de testare.
APPROVED
Regula a fost aprobată pentru activare.
ACTIVE
Regula participă la evaluări operaționale.
SUSPENDED
Regula este temporar scoasă din execuție.
RETIRED
Regula a fost retrasă din utilizarea operațională.
Istoricul versiunilor rămâne păstrat.
________________


9. Rule Context
Evaluarea unei reguli utilizează un Context Payload.
Contextul poate conține:
object
object_state
related_objects
events
history
metrics
scores
timestamps
user_context
team_context
system_context


Structura conceptuală:
{
  "object": {},
  "state": {},
  "relations": {},
  "history": {},
  "events": [],
  "metrics": {},
  "context": {}
}


Contextul este furnizat de Engine sau Workflow.
________________


10. Condition Model
Condițiile unei reguli sunt definite declarativ.
Operatorii fundamentali sunt:
IF
AND
OR
NOT
EQUALS
NOT_EQUALS
GREATER_THAN
GREATER_OR_EQUAL
LESS_THAN
LESS_OR_EQUAL
IN
NOT_IN
EXISTS
NOT_EXISTS


Structura logică:
IF
    Condition A
    AND
    Condition B
THEN
    Outcome X


Pentru condiții complexe:
IF
    (
        Condition A
        AND Condition B
    )
    OR
    (
        Condition C
        AND Condition D
    )
THEN
    Outcome X


________________


11. Threshold Model
Pragurile sunt definite separat de expresia logică.
Exemplu conceptual:
threshold_code: PARTNER_ACTIVITY_MIN
value: 5
operator: GREATER_OR_EQUAL
unit: missions
period: 30_days


Structura permite modificarea parametrilor operaționali prin versionarea regulii.
________________


12. Evaluation Model
Evaluarea unei reguli urmează următoarea secvență:
1. Receive Evaluation Request
        ↓
2. Identify Target Object
        ↓
3. Load Active Rule Version
        ↓
4. Load Context
        ↓
5. Validate Context
        ↓
6. Evaluate Conditions
        ↓
7. Evaluate Thresholds
        ↓
8. Calculate Outcome
        ↓
9. Generate Decision Result
        ↓
10. Write Audit Record
        ↓
11. Return Result


________________


13. Evaluation Request
O cerere standard de evaluare conține:
evaluation_id
rule_code
rule_version
target_object_type
target_object_id
trigger_event
context_payload
requested_at
actor_id
correlation_id


Exemplu:
{
  "evaluation_id": "UUID",
  "rule_code": "RULE-PARTNER-QUAL-001",
  "rule_version": "1.0",
  "target_object_type": "Partner",
  "target_object_id": "UUID",
  "trigger_event": "PartnerActivityUpdated",
  "context_payload": {},
  "actor_id": "UUID",
  "correlation_id": "UUID"
}


________________


14. Decision Outcome
Rule Engine returnează un rezultat standardizat.
Structura:
DecisionResult
│
├── evaluation_id
├── rule_code
├── rule_version
├── result
├── outcome_code
├── score
├── thresholds_met
├── conditions_met
├── actions
├── explanation
└── timestamp


Rezultatul poate fi:
TRUE
FALSE
PASS
FAIL
THRESHOLD_MET
THRESHOLD_NOT_MET
SCORE
NO_ACTION


________________


15. Exemplu de Decision Result
{
  "evaluation_id": "UUID",
  "rule_code": "RULE-PARTNER-QUAL-001",
  "rule_version": "1.0",
  "result": true,
  "outcome_code": "QUALIFIED",
  "score": 82,
  "thresholds_met": true,
  "actions": [
    "PartnerQualificationConfirmed"
  ],
  "explanation": {
    "conditions_met": [
      "activity_threshold_met",
      "required_steps_completed"
    ]
  }
}


________________


16. Action Output
O regulă poate produce următoarele tipuri de rezultate:
State Change
StateTransitionRequested


Event
BusinessEvent
SystemEvent


Workflow Trigger
WorkflowTrigger


Mission
MissionGenerationRequested


Notification
NotificationRequested


KPI Update
KPIRecalculationRequested


Score Update
ScoreUpdateRequested


Regula furnizează decizia.
Engine-ul sau Workflow Engine execută acțiunea rezultată.
________________


17. Separarea Evaluării de Execuție
Regula are două responsabilități distincte:
RULE ENGINE
     │
     ├── Evaluate
     │
     └── Return Decision
              ↓
        ENGINE / WORKFLOW
              ↓
        Execute Action


Rule Engine nu preia responsabilitatea orchestration-ului operațional.
Această separare păstrează delimitarea dintre:
* Rules;
* Engines;
* Workflows;
* Events;
* State Machines.
________________


18. Rule Priority
Regulile pot avea prioritate de evaluare.
priority: INTEGER


Exemplu:
1 = Critical
2 = High
3 = Normal
4 = Low


Prioritatea este utilizată pentru ordonarea evaluării atunci când mai multe reguli sunt eligibile în același context.
________________


19. Rule Conflict Resolution
În cazul în care mai multe reguli produc rezultate diferite pentru același context, Rule Engine utilizează următoarea ordine:
1. Rule Priority
2. Rule Specificity
3. Rule Version
4. Explicit Conflict Policy


Conflictele sunt înregistrate în AuditLog.
Un conflict nerezolvat produce:
RULE_CONFLICT


și transmite cazul către mecanismul de intervenție definit de arhitectură.
________________


20. Rule Versioning
Regulile sunt versionate independent.
Exemplu:
RULE-PARTNER-QUAL-001 v1.0
RULE-PARTNER-QUAL-001 v1.1
RULE-PARTNER-QUAL-001 v2.0


O versiune activă este identificată explicit.
Evenimentele istorice păstrează versiunea regulii care a produs decizia.
Astfel:
Decision
   ↓
Rule Code
   +
Rule Version
   ↓
Exact Logic Used


________________


21. Rule Evaluation Persistence
Evaluările regulilor sunt persistate pentru trasabilitate.
Structură logică:
rule_evaluations
* evaluation_id UUID PK
* rule_id UUID
* rule_code VARCHAR
* rule_version VARCHAR
* target_object_type VARCHAR
* target_object_id UUID
* trigger_event VARCHAR
* result VARCHAR
* outcome_code VARCHAR
* score NUMERIC NULL
* context_payload JSONB
* result_payload JSONB
* correlation_id UUID
* evaluated_at TIMESTAMPTZ
* actor_id UUID NULL
________________


22. Rule Definition Persistence
Structura logică a registrului regulilor:
rules
* id UUID PK
* rule_code VARCHAR UNIQUE
* rule_name VARCHAR
* rule_type VARCHAR
* owner_domain VARCHAR
* target_engine VARCHAR
* target_object_type VARCHAR
* target_state_machine VARCHAR NULL
* condition_expression JSONB
* thresholds JSONB
* action_output JSONB
* priority INTEGER
* version VARCHAR
* status VARCHAR
* effective_from TIMESTAMPTZ
* effective_until TIMESTAMPTZ NULL
* created_at TIMESTAMPTZ
* updated_at TIMESTAMPTZ
* created_by UUID
* approved_by UUID NULL
________________


23. Relația cu Database Architecture
RULE-MODEL-001 utilizează infrastructura definită în Nivelul 2.
rules
   ↓
rule_evaluations
   ↓
Event Store
   ↓
AuditLog


Regulile active sunt persistate în rules.
Rezultatele evaluării sunt persistate în rule_evaluations.
Deciziile care produc evenimente sunt înregistrate în Event Store.
Acțiunile și deciziile sunt urmărite în AuditLog.
________________


24. Relația cu State Machines
Rule Engine poate evalua condițiile unei tranziții, însă tranziția oficială aparține State Machine-ului.
Flux:
Event
 ↓
Engine
 ↓
Rule Evaluation
 ↓
Transition Allowed
 ↓
State Machine
 ↓
State Change
 ↓
Event
 ↓
AuditLog


State Machine-ul rămâne SSOT pentru stările și tranzițiile oficiale.
________________


25. Relația cu Workflow Engine
Workflow Engine poate solicita evaluarea unei reguli într-un anumit pas.
Workflow Step
     ↓
Rule Evaluation
     ↓
Decision
     ↓
Branch A / Branch B


Exemplu:
IF Partner qualification score >= threshold
THEN
    continue onboarding workflow
ELSE
    create follow-up mission


________________


26. Relația cu Engine Architecture
Engine-urile consumă rezultatele regulilor.
Exemple:
MissionEngine
      ↓
Priority Rule
      ↓
Priority Outcome


ContinuityEngine
      ↓
Continuity Rule
      ↓
Continuity Outcome


PerformanceEvaluationEngine
      ↓
Threshold / Scoring Rule
      ↓
Performance Outcome


CustomerRelationshipEngine
      ↓
Relationship Rule
      ↓
Relationship Outcome


________________


27. Explainability Model
Fiecare evaluare trebuie să poată răspunde la întrebările:
Ce regulă a fost evaluată?
Ce versiune?
Pentru ce obiect?
Ce eveniment a declanșat evaluarea?
Ce date au fost folosite?
Ce condiții au fost evaluate?
Ce praguri au fost verificate?
Care a fost rezultatul?
Ce acțiune a fost solicitată?


Aceste date sunt păstrate prin rule_evaluations și AuditLog.
________________


28. Error Model
Erorile de evaluare sunt standardizate.
RULE_NOT_FOUND
Regula solicitată nu există în registru.
RULE_VERSION_NOT_FOUND
Versiunea solicitată nu există.
RULE_NOT_ACTIVE
Regula există, însă versiunea respectivă nu este activă.
INVALID_CONTEXT
Contextul primit este incomplet sau invalid.
EVALUATION_ERROR
Evaluarea condițiilor a produs o eroare.
RULE_CONFLICT
Mai multe reguli eligibile produc rezultate incompatibile.
ACTION_OUTPUT_INVALID
Rezultatul regulii nu poate fi transformat într-o acțiune validă.
Toate erorile sunt înregistrate în AuditLog.
________________


29. Testing Model
Fiecare regulă trebuie să aibă cazuri de test definite înainte de activare.
Structura minimă:
Test Case
│
├── Input Context
├── Expected Conditions
├── Expected Thresholds
├── Expected Result
├── Expected Outcome
└── Expected Action


Exemplu:
Rule:
RULE-PARTNER-QUAL-001


Input:
activity_score = 85


Threshold:
>= 80


Expected:
TRUE


Outcome:
QUALIFIED


________________


30. Rule Activation
Activarea unei reguli urmează fluxul:
DRAFT
   ↓
TESTING
   ↓
APPROVED
   ↓
ACTIVE


O regulă devine operațională numai după validarea versiunii sale.
Activarea este înregistrată în AuditLog.
________________


31. Rule Retirement
Retragerea unei reguli urmează:
ACTIVE
   ↓
SUSPENDED
   ↓
RETIRED


Regula retrasă rămâne disponibilă pentru istoricul deciziilor.
Deciziile istorice continuă să indice exact versiunea utilizată.
________________


32. Integritate și Constrângeri
Sistemul trebuie să asigure:
* rule_code unic;
* versiune explicită;
* o singură versiune activă pentru combinația definită de regulă și domeniu;
* target_engine valid;
* target_object_type valid;
* expresie de condiții validă;
* praguri valide;
* rezultat valid;
* trasabilitate prin evaluation_id;
* trasabilitate prin correlation_id.
________________


33. Audit obligatoriu
Fiecare evaluare produce o urmă de audit.
Rule
+
Version
+
Input
+
Evaluation
+
Outcome
+
Action
+
Actor
+
Timestamp


Acest mecanism asigură reconstrucția completă a deciziei.
________________


34. Principiul de Separare a Responsabilităților
Arhitectura finală este:
STATE MACHINE
Definește:
STĂRI + TRANZIȚII


WORKFLOW ENGINE
Definește:
ORDINEA PAȘILOR


ENGINE
Definește:
ORCHESTRAREA LOGICII OPERAȚIONALE


RULE ENGINE
Definește:
EVALUAREA CONDIȚIILOR


RULE
Definește:
LOGICA DECLARATIVĂ


EVENT BUS
Definește:
PROPAGAREA EVENIMENTELOR


DATABASE
Definește:
PERSISTENȚA


AUDITLOG
Definește:
TRASABILITATEA


Această separare constituie contractul structural al Nivelului 5.
________________


35. Contractul Tehnic Final
Interfața logică standard este:
Evaluate(
    rule_code,
    rule_version,
    target_object,
    context_payload,
    correlation_id
)


Rezultatul standard:
DecisionResult(
    evaluation_id,
    rule_code,
    rule_version,
    result,
    outcome_code,
    score,
    conditions_met,
    thresholds_met,
    actions,
    explanation
)


________________


36. Fluxul Complet de Execuție
EVENT
  ↓
WORKFLOW
  ↓
ENGINE
  ↓
RULE ENGINE
  ↓
LOAD ACTIVE RULE
  ↓
LOAD CONTEXT
  ↓
VALIDATE CONTEXT
  ↓
EVALUATE CONDITIONS
  ↓
EVALUATE THRESHOLDS
  ↓
GENERATE DECISION
  ↓
PERSIST EVALUATION
  ↓
AUDITLOG
  ↓
ENGINE / WORKFLOW
  ↓
ACTION
  ↓
STATE / EVENT / KPI / NOTIFICATION


________________


37. Business Rules Registry
RULE-MODEL-001 stabilește infrastructura necesară pentru registrul oficial de reguli.
Registrul complet al regulilor operaționale va fi definit într-un document derivat ulterior:
RULE-REG-001
Business Rules Registry


Acesta va conține inventarul regulilor efective ale NicMar OS.
RULE-MODEL-001 definește modelul.
RULE-REG-001 va defini catalogul.
________________


38. Documente Derivate
Din RULE-MODEL-001 vor deriva:
RULE-REG-001
Business Rules Registry


RULE-TEST-001
Rule Testing & Validation Model


RULE-VERSION-001
Rule Versioning & Change Control


Acestea vor fi construite în ordinea stabilită de arhitectura Nivelului 5.
________________


39. SSOT Chain
Lanțul oficial este:
Document 01
Business Objects
        ↓
RULE-ARCH-001
Rules & Decision Architecture Standard
        ↓
RULE-MODEL-001
Rule Definition & Evaluation Model
        ↓
RULE-REG-001
Business Rules Registry
        ↓
Rule Evaluation
        ↓
Engine
        ↓
Workflow
        ↓
Event / State / KPI


________________


40. Status Arhitectural
Document: NicMar OS – Core Architecture – Document 07.1
Identificator: RULE-MODEL-001
Business Domain: Core Architecture / Rules & Decision Architecture
Nivel: Nivelul 5 – Rules & Decision Architecture
Versiune: 1.0
Status:validat  
SSOT Sursă: RULE-ARCH-001
Rol
RULE-MODEL-001 este standardul tehnic pentru definirea și evaluarea regulilor NicMar OS.
Următorul document oficial
RULE-MODEL-001
        ↓
VALIDARE
        ↓
RULE-REG-001
Business Rules Registry
        ↓
RULE-TEST-001
Rule Testing & Validation
        ↓
NIVELUL 5
🔒 100% ÎNCHIS






Da. Mai jos este forma finală, curățată și aliniată cu DB-BO-001, RULE-ARCH-001, RULE-REG-001 și cele 15 Engine-uri. Este gata de copiat și introdus în arhitectură.
NICMAR OS — CORE ARCHITECTURE
DOCUMENT 07.2 — RULE DEFINITION & EVALUATION MODEL
Identificator: RULE-MODEL-001
Business Domain: Core Architecture / Rules & Decision Architecture
Nivel: Nivelul 5 – Rules & Decision Architecture
Versiune: 1.0
Status: 🔒 VALIDAT / ÎNGHEȚAT
Metodologie: Declarative & Deterministic Rule Engine Architecture
SSOT Surse: RULE-ARCH-001, RULE-REG-001, DB-BO-001, ENG-ARCH-001
________________


1. SCOPUL DOCUMENTULUI
RULE-MODEL-001 definește modelul tehnic oficial pentru reprezentarea, versionarea, validarea și evaluarea regulilor de business în NicMar OS.
Documentul stabilește contractul structural dintre:
Business Object
      ↓
Rule
      ↓
Rule Evaluation
      ↓
Decision Outcome
      ↓
Engine
      ↓
Event / Workflow / State / KPI


Modelul asigură:
* reprezentarea declarativă a regulilor;
* evaluarea deterministă;
* versionarea regulilor;
* trasabilitatea fiecărei decizii;
* separarea regulilor de codul Engine-urilor;
* reutilizarea regulilor de către mai multe Engine-uri;
* auditarea completă a deciziilor.
RULE-MODEL-001 reprezintă SSOT pentru structura tehnică și mecanismul de evaluare al unei reguli.
________________


2. POZIȚIONAREA ÎN ARHITECTURA NICMAR OS
Regula este executată în cadrul fluxului operațional controlat de Engine și Workflow Layer.
Fluxul oficial este:
Event
   ↓
Workflow
   ↓
Engine
   ↓
Rule Evaluation
   ↓
Decision Outcome
   ↓
Action
   ↓
Event / State Change / Workflow / KPI


Responsabilitățile sunt separate astfel:
Workflow Engine
Orchestrează pașii procesului.
Engine
Coordonează logica operațională a domeniului.
Rule Engine
Evaluează condițiile declarative și produce rezultatul logic.
Database
Persistă regulile, versiunile, rezultatele și trasabilitatea.
Event Bus
Transportă evenimentele rezultate.
________________


3. PRINCIPII ARHITECTURALE
3.1 Declarativitate
Regulile sunt definite ca date structurale și expresii logice declarative.
Logica unei reguli este separată de implementarea Engine-ului.
________________


3.2 Determinism
Aceleași date de intrare, aceeași versiune de regulă și același context trebuie să producă același rezultat.
Input Context
+
Rule Version
+
Evaluation Time
        ↓
Deterministic Outcome


________________


3.3 Versionare
O regulă activă este identificată prin:
rule_code
+
rule_version


Modificarea logicii unei reguli produce o versiune nouă.
Versiunile anterioare sunt păstrate pentru trasabilitate și audit.
________________


3.4 Imuabilitatea Versiunilor Active
O versiune de regulă care a fost activată și utilizată în producție devine imuabilă.
Modificările ulterioare sunt realizate printr-o versiune nouă.
________________


3.5 Separarea Evaluării de Execuție
Rule Engine produce decizia.
Engine-ul responsabil interpretează decizia și execută acțiunea operațională.
Rule Engine
    ↓
Decision
    ↓
Domain Engine
    ↓
Action


________________


3.6 Explicabilitate
Fiecare evaluare trebuie să poată identifica:
* regula;
* versiunea;
* obiectul evaluat;
* valorile de intrare;
* condițiile evaluate;
* pragurile utilizate;
* rezultatul;
* motivul rezultatului;
* momentul evaluării;
* Engine-ul care a solicitat evaluarea.
________________


4. MODELUL CANONIC AL OBIECTULUI RULE
Obiectul Rule este unul dintre cele 38 Business Objects definite în DB-BO-001.
Tabelul canonic este:
rules


Structura logică minimă este:
id
rule_code
rule_name
version
status
target_engine_code
business_object_type
conditions_json
thresholds_ref
decision_outcome
action_output
effective_from
effective_until
created_at
updated_at


________________


5. ATRIBUTELE CANONICE ALE UNEI REGULI
id
Identificator UUID unic al înregistrării regulii.
________________


rule_code
Codul business unic al regulii.
Exemplu:
RULE-CONTACT-QUAL-001


________________


rule_name
Denumirea descriptivă a regulii.
Exemplu:
Contact Qualification Rule


________________


version
Versiunea regulii.
Format recomandat:
MAJOR.MINOR.PATCH


Exemplu:
1.0.0


________________


status
Starea ciclului de viață al regulii.
Valori canonice:
PROPOSED
DRAFT
VALIDATED
ACTIVE
DEPRECATED
ARCHIVED


________________


target_engine_code
Engine-ul care utilizează regula.
Exemplu:
ENG-PRIORITY-001


sau:
ENG-MISSION-001


Referința trebuie să utilizeze codul oficial din ENG-ARCH-001.
________________


business_object_type
Business Object asupra căruia este evaluată regula.
Exemple:
Contact
Partner
Client
Mission
Conversation


Valoarea trebuie să provină din registrul oficial al celor 38 Business Objects.
________________


conditions_json
Arborele logic al regulii.
Structura utilizează expresii declarative de tip AST / JSON Logic.
________________


thresholds_ref
Referința către pragurile utilizate de regulă.
Pragurile trebuie să fie identificabile și versionabile independent.
________________


decision_outcome
Rezultatul logic al evaluării.
Exemple:
TRUE
FALSE
QUALIFIED
NOT_QUALIFIED
THRESHOLD_MET
THRESHOLD_NOT_MET


Valorile utilizate trebuie să fie definite în registrul oficial al regulii.
________________


action_output
Acțiunea operațională asociată rezultatului.
Exemple:
TRIGGER_WORKFLOW
UPDATE_STATE
GENERATE_MISSION
UPDATE_SCORE
CREATE_NOTIFICATION


________________


effective_from
Momentul de la care versiunea regulii devine valabilă.
________________


effective_until
Momentul până la care versiunea regulii rămâne valabilă.
Pentru versiunea activă curentă, câmpul poate rămâne NULL.
________________


6. STRUCTURA EXPRESIEI LOGICE
Condițiile sunt reprezentate printr-un arbore logic.
Modelul permite:
AND
OR
NOT
==
!=
>
<
>=
<=
IN
NOT IN
BETWEEN
EXISTS
NOT EXISTS


Structura trebuie să fie declarativă și serializabilă.
Evaluarea expresiei se realizează exclusiv prin operatorii acceptați de Rule Evaluation Engine.
________________


7. EXEMPLU DE REGULĂ
Exemplu conceptual:
{
  "and": [
    {
      ">=": [
        {
          "var": "Contact.profile_completeness"
        },
        60
      ]
    },
    {
      "==": [
        {
          "var": "Contact.initial_interest_flag"
        },
        true
      ]
    }
  ]
}


Interpretarea este:
IF
    Contact.profile_completeness >= 60
AND
    Contact.initial_interest_flag = true
THEN
    Decision Outcome = QUALIFIED


________________


8. MODELUL CONTEXTULUI DE EVALUARE
Rule Engine primește un Evaluation Context.
Structura logică:
Evaluation Context
│
├── rule_code
├── rule_version
├── business_object_type
├── business_object_id
├── current_state
├── object_data
├── related_objects
├── event_context
├── actor_context
├── timestamp
└── requested_by_engine


Contextul conține strict datele necesare evaluării.
________________


9. FLUXUL OFICIAL DE EVALUARE
Evaluarea unei reguli urmează secvența:
1. Engine Request
        ↓
2. Rule Resolution
        ↓
3. Version Resolution
        ↓
4. Context Assembly
        ↓
5. Condition Parsing
        ↓
6. Variable Resolution
        ↓
7. Threshold Resolution
        ↓
8. Condition Evaluation
        ↓
9. Decision Outcome
        ↓
10. Reason Code
        ↓
11. Evaluation Result
        ↓
12. Audit / Event


________________


10. RULE RESOLUTION
Rule Engine identifică regula după:
rule_code


Apoi determină versiunea aplicabilă conform:
status = ACTIVE
effective_from <= evaluation_time
effective_until > evaluation_time


Rezultatul este o singură versiune canonică pentru evaluarea respectivă.
________________


11. CONDITION EVALUATION
După încărcarea versiunii active:
conditions_json
        ↓
AST Parser
        ↓
Variable Resolver
        ↓
Operator Evaluation
        ↓
Boolean / Numeric / Categorical Result


Fiecare nod al arborelui este evaluat în ordinea definită de structură.
________________


12. THRESHOLD EVALUATION
Pragurile sunt evaluate separat de expresia logică atunci când regula utilizează valori parametrizate.
Exemplu:
qualification_threshold = 60


Evaluarea:
profile_completeness = 72
threshold = 60


72 >= 60
    ↓
TRUE


Rezultatul pragului este inclus în rezultatul final al regulii.
________________


13. DECISION OUTCOME
Rezultatul standard al Rule Engine trebuie să permită identificarea completă a deciziei.
Structura recomandată:
{
  "rule_code": "RULE-CONTACT-QUAL-001",
  "rule_version": "1.0.0",
  "business_object_type": "Contact",
  "business_object_id": "UUID",
  "outcome": "QUALIFIED",
  "result": true,
  "reason_code": "QUALIFICATION_THRESHOLD_MET",
  "evaluated_at": "TIMESTAMP"
}


________________


14. REASON CODE
Fiecare decizie relevantă trebuie să poată furniza un reason_code.
Exemple:
QUALIFICATION_THRESHOLD_MET
QUALIFICATION_THRESHOLD_NOT_MET
PRIORITY_THRESHOLD_MET
FOLLOWUP_REQUIRED
MISSION_READY
MISSION_BLOCKED
CLIENT_ELIGIBILITY_MET
PARTNER_ELIGIBILITY_MET


reason_code permite explicarea deciziei și analiza ulterioară.
________________


15. ACTION OUTPUT
După generarea deciziei, Rule Engine poate returna un action_output.
Exemplu:
{
  "action_type": "TRIGGER_WORKFLOW",
  "action_code": "WF-CONTACT-QUALIFY-001"
}


Alte tipuri:
UPDATE_STATE
GENERATE_MISSION
UPDATE_SCORE
CREATE_NOTIFICATION
TRIGGER_WORKFLOW
REQUEST_FOLLOWUP


Rule Engine furnizează rezultatul.
Engine-ul responsabil execută acțiunea conform contractului său.
________________


16. CONTRACTUL TEHNIC RULE EVALUATION
Intrarea standard:
{
  "rule_code": "RULE-CONTACT-QUAL-001",
  "business_object_type": "Contact",
  "business_object_id": "UUID",
  "context": {}
}


Ieșirea standard:
{
  "rule_code": "RULE-CONTACT-QUAL-001",
  "rule_version": "1.0.0",
  "result": true,
  "outcome": "QUALIFIED",
  "reason_code": "QUALIFICATION_THRESHOLD_MET",
  "action_output": {
    "action_type": "TRIGGER_WORKFLOW",
    "action_code": "WF-CONTACT-QUALIFY-001"
  }
}


________________


17. TRATAREA ERORILOR DE EVALUARE
Rule Engine trebuie să diferențieze între:
Evaluation Success
Regula a fost evaluată cu succes.
Evaluation False
Condițiile regulii au fost evaluate, iar rezultatul este FALSE.
Evaluation Error
Evaluarea tehnică a eșuat.
Exemple:
RULE_NOT_FOUND
RULE_VERSION_NOT_FOUND
INVALID_RULE_STATUS
INVALID_CONDITION_STRUCTURE
MISSING_CONTEXT_VALUE
INVALID_OPERATOR
THRESHOLD_NOT_FOUND
INVALID_THRESHOLD_VALUE


O eroare tehnică de evaluare este diferită de rezultatul logic FALSE.
________________


18. TRASABILITATE ȘI AUDIT
Fiecare evaluare relevantă produce date de trasabilitate:
Rule
Rule Version
Business Object
Business Object ID
Engine
Input Context
Decision Outcome
Reason Code
Timestamp
Correlation ID


Datele sunt disponibile pentru AuditLog conform DB-AUDIT-001.
Evenimentele generate în urma deciziei sunt transmise către Event Bus conform arhitecturii Event-Driven.
________________


19. RELAȚIA CU ENGINE ARCHITECTURE
RULE-MODEL-001 este consumat de Engine-urile oficiale din ENG-ARCH-001.
Fluxul:
Engine
   ↓
Rule Evaluation Request
   ↓
Rule Engine
   ↓
Decision Outcome
   ↓
Engine
   ↓
Action


Engine-ul păstrează responsabilitatea pentru logica operațională a domeniului.
Rule Engine păstrează responsabilitatea pentru evaluarea regulilor declarative.
________________


20. RELAȚIA CU WORKFLOW ENGINE
Rule Evaluation poate produce un rezultat care declanșează un Workflow.
Exemplu:
Contact
   ↓
Qualification Rule
   ↓
QUALIFIED
   ↓
TRIGGER_WORKFLOW
   ↓
WF-CONTACT-QUALIFY-001


Workflow Engine preia orchestrarea procesului.
________________


21. RELAȚIA CU STATE MACHINES
O regulă poate valida condițiile necesare pentru o tranziție.
Flux:
Current State
      ↓
Rule Evaluation
      ↓
Transition Eligible
      ↓
State Machine Event
      ↓
New State


Regula furnizează eligibilitatea.
State Machine controlează tranziția oficială.
________________


22. RELAȚIA CU KPI & PERFORMANCE
Regulile pot utiliza praguri provenite din arhitectura KPI și pot genera acțiuni pentru actualizarea scorurilor.
Exemplu:
KPI Value
    ↓
Threshold Rule
    ↓
Threshold Met
    ↓
UPDATE_SCORE


Formulele oficiale ale KPI-urilor aparțin Nivelului 6 — KPI & Performance Architecture.
RULE-MODEL-001 definește mecanismul de consum al rezultatelor și pragurilor.
________________


23. SECURITATEA EVALUĂRII
Rule Engine trebuie să opereze exclusiv pe:
* reguli validate;
* versiuni autorizate;
* operatori acceptați;
* contexte autorizate;
* Business Objects existente;
* Engine-uri autorizate.
Expresiile de regulă sunt declarative.
Executarea arbitrară de cod în interiorul conditions_json este exclusă din modelul de evaluare.
________________


24. VALIDAREA UNEI REGULI ÎNAINTE DE ACTIVARE
O regulă poate deveni ACTIVE după parcurgerea ciclului:
PROPOSED
   ↓
DRAFT
   ↓
VALIDATED
   ↓
ACTIVE


Validarea trebuie să confirme:
1. existența unui rule_code;
2. existența unei versiuni valide;
3. existența unui Engine țintă valid;
4. existența Business Object-ului țintă;
5. validitatea structurii conditions_json;
6. validitatea operatorilor;
7. validitatea pragurilor;
8. existența unui decision_outcome;
9. validitatea action_output;
10. existența perioadei de valabilitate;
11. trecerea testelor definite în RULE-TEST-001.
________________


25. REGULA DE VERSIONARE
Versiunea unei reguli este identificată prin:
rule_code + version


Exemplu:
RULE-CONTACT-QUAL-001
Version 1.0.0


O modificare logică produce:
RULE-CONTACT-QUAL-001
Version 1.1.0


Ambele versiuni pot rămâne în istoricul sistemului, fiecare cu perioada proprie de valabilitate.
________________


26. REGULA DE ACTIVARE
O singură versiune a aceluiași rule_code poate fi activă pentru același interval temporal și același context de aplicare.
Această regulă protejează determinismul sistemului și elimină ambiguitatea în rezolvarea versiunii.
________________


27. RELAȚIA CU REGISTRUL DE REGULI
RULE-REG-001 reprezintă registrul oficial al regulilor.
RULE-MODEL-001 definește modul tehnic în care fiecare regulă din registru este reprezentată și evaluată.
Relația este:
RULE-REG-001
     ↓
Rule Code
     ↓
RULE-MODEL-001
     ↓
Rule Definition
     ↓
Rule Evaluation


________________


28. RELAȚIA CU DATABASE ARCHITECTURE
Persistența regulilor utilizează Business Object-ul:
Rule


și tabelul:
rules


Conform:
DB-BO-001
DB-REL-001
DB-STATE-001
DB-EVENT-001
DB-AUDIT-001


Evaluările și deciziile sunt corelate cu Event Store și AuditLog prin mecanismele oficiale ale arhitecturii de persistență.
________________


29. CRITERII DE CONFORMITATE
RULE-MODEL-001 este conform dacă:
Rule
  ↓
Has Version
  ↓
Has Status
  ↓
Has Target Engine
  ↓
Has Business Object
  ↓
Has Conditions
  ↓
Has Thresholds when required
  ↓
Produces Decision Outcome
  ↓
Produces Reason Code
  ↓
Produces Action Output when required
  ↓
Is Auditable
  ↓
Is Deterministic


________________


30. STATUS OFICIAL
Document: NicMar OS – Core Architecture – Document 07.2
Titlu: Rule Definition & Evaluation Model
Identificator: RULE-MODEL-001
Nivel: Nivelul 5 – Rules & Decision Architecture
Versiune: 1.0
Status: 🔒 VALIDAT / ÎNGHEȚAT
SSOT Surse: RULE-ARCH-001, RULE-REG-001, DB-BO-001, ENG-ARCH-001
________________


31. POZIȚIA ÎN SECVENȚA NIVELULUI 5
RULE-ARCH-001
Business Rules & Decision Architecture Standard
        ↓
RULE-REG-001
Business Rules Registry
        ↓
RULE-MODEL-001
Rule Definition & Evaluation Model
        ↓
RULE-TEST-001
Rule Testing & Validation
        ↓
RULE-INT-001
Rule Integration & Execution Contract
        ↓
NIVELUL 5
RULES & DECISION ARCHITECTURE
🔒 100% ÎNCHIS


RULE-MODEL-001 reprezintă SSOT pentru modelul tehnic de definire și evaluare a regulilor de business din NicMar OS.
Acesta este documentul pe care îl poți introduce acum în Core Architecture ca 07.2. După el, execuția logică merge direct în RULE-TEST-001, unde vom defini cum se testează fiecare regulă înainte de activare.




NICMAR OS — CORE ARCHITECTURE
DOCUMENT 07.4 — RULE TESTING & VALIDATION
Identificator: RULE-TEST-001
Business Domain: Core Architecture / Rules & Decision Architecture
Nivel: Nivelul 5 — Rules & Decision Architecture
Versiune: 1.0
Status: 🔒 VALIDAT / SSOT
Metodologie: Deterministic Rule Testing & Validation
SSOT Sursă: RULE-ARCH-001, RULE-REG-001, RULE-MODEL-001
________________


1. SCOPUL DOCUMENTULUI
RULE-TEST-001 definește standardul oficial prin care regulile de business din NicMar OS sunt testate, validate și aprobate înainte de activarea lor în producție.
Documentul garantează că fiecare regulă:
* produce rezultate deterministe;
* respectă structura definită în RULE-MODEL-001;
* utilizează exclusiv operatori și date autorizate;
* respectă Business Object-ul și Engine-ul asociat;
* produce rezultatul decizional așteptat;
* generează trasabilitate completă în AuditLog;
* respectă versiunile și perioada de valabilitate;
* poate fi verificată înainte de activare;
* poate fi regresată după modificări.
RULE-TEST-001 reprezintă poarta oficială dintre:
RULE-MODEL-001 → Rule Validation → Rule Activation.
________________


2. PRINCIPIUL DE VALIDARE
Nicio regulă nu devine ACTIVE până când nu trece setul obligatoriu de teste definit în acest document.
Fluxul oficial este:
RULE Definition
      ↓
Schema Validation
      ↓
Structural Validation
      ↓
Logic Validation
      ↓
Positive Tests
      ↓
Negative Tests
      ↓
Boundary Tests
      ↓
Regression Tests
      ↓
Determinism Test
      ↓
Audit Validation
      ↓
Engine Integration Test
      ↓
Approval
      ↓
ACTIVE


________________


3. CICLUL DE VIAȚĂ AL TESTĂRII
Fiecare regulă trece prin următoarele faze:
3.1 PROPOSED
Regula este definită și înregistrată în registrul oficial.
3.2 DRAFT
Structura regulii este pregătită pentru testare.
3.3 TESTING
Rule Test Suite este executat.
3.4 VALIDATED
Toate testele obligatorii au fost trecute cu succes.
3.5 ACTIVE
Regula este autorizată pentru execuție operațională.
3.6 FAILED
Cel puțin un test obligatoriu a eșuat.
3.7 DEPRECATED
Regula a fost înlocuită de o versiune ulterioară.
3.8 ARCHIVED
Regula este păstrată exclusiv pentru istoric și audit.
________________


4. STRUCTURA STANDARD A UNUI RULE TEST
Fiecare test asociat unei reguli trebuie să conțină:
* test_id — UUID unic;
* rule_id — identificatorul regulii;
* rule_code — codul regulii;
* rule_version — versiunea testată;
* test_type — tipul testului;
* input_context — contextul de intrare;
* expected_outcome — rezultatul așteptat;
* actual_outcome — rezultatul obținut;
* expected_reason_code — motivul așteptat;
* actual_reason_code — motivul obținut;
* expected_actions — acțiunile așteptate;
* actual_actions — acțiunile generate;
* execution_time_ms — timpul de execuție;
* test_status — PASSED / FAILED;
* executed_at — momentul execuției;
* executed_by — utilizator, sistem sau pipeline;
* metadata — informații suplimentare.
________________


5. CATEGORIILE OFICIALE DE TESTE
5.1 Schema Test
Verifică integritatea structurală a regulii.
Se verifică:
* existența rule_code;
* existența versiunii;
* existența Engine-ului asociat;
* existența Business Object-ului;
* validitatea conditions_json;
* validitatea decision_outcome;
* validitatea action_output;
* validitatea perioadei de valabilitate.
Rezultat: SCHEMA_VALID sau SCHEMA_INVALID.
________________


6. STRUCTURAL TEST
Verifică dacă regula respectă modelul tehnic RULE-MODEL-001.
Se validează:
* structura AST;
* operatorii autorizați;
* variabilele autorizate;
* referințele către Business Objects;
* referințele către Engine;
* pragurile;
* acțiunile;
* identificatorii canonici.
Orice element în afara contractului determină eșecul testului structural.
________________


7. POSITIVE TEST
Testează situația în care toate condițiile regulii sunt îndeplinite.
Exemplu:
Regulă:
RULE-CONTACT-QUAL-001


Condiții:
profile_completeness >= 60
initial_interest_flag = true


Input:
profile_completeness = 75
initial_interest_flag = true


Expected Outcome:
QUALIFIED


Expected Action:
TRIGGER_WORKFLOW


Rezultatul trebuie să fie:
PASS


________________


8. NEGATIVE TEST
Testează situația în care una sau mai multe condiții obligatorii nu sunt îndeplinite.
Exemplu:
profile_completeness = 75
initial_interest_flag = false


Expected Outcome:
NOT_QUALIFIED


Testul verifică faptul că regula nu produce accidental rezultatul pozitiv.
________________


9. BOUNDARY TEST
Testează valorile aflate exact la limitele pragurilor.
Pentru o regulă:
profile_completeness >= 60


se testează obligatoriu:
59
60
61


Rezultatele trebuie să fie:
59 → FALSE
60 → TRUE
61 → TRUE


Boundary Testing este obligatoriu pentru toate regulile care utilizează praguri.
________________


10. NULL / MISSING DATA TEST
Regula trebuie testată și atunci când datele necesare lipsesc.
Exemple:
profile_completeness = NULL
initial_interest_flag = true


sau:
profile_completeness = 70
initial_interest_flag = NULL


Motorul trebuie să producă un rezultat controlat și documentat.
Rezultatul poate fi:
INVALID_CONTEXT


sau rezultatul logic definit explicit de regulă.
Comportamentul pentru date lipsă trebuie definit înainte de activarea regulii.
________________


11. TYPE VALIDATION TEST
Verifică tipurile datelor introduse în evaluare.
Exemplu:
profile_completeness = "seventy"


într-o regulă care așteaptă:
INTEGER / NUMERIC


trebuie să producă:
TYPE_VALIDATION_ERROR


Motorul de reguli nu execută conversii implicite nesigure.
________________


12. DETERMINISM TEST
Aceeași regulă, executată cu exact același context, trebuie să producă exact același rezultat.
Exemplu:
Input Context A
      ↓
Rule Evaluation
      ↓
Outcome X


Același Input Context A
      ↓
Rule Evaluation
      ↓
Outcome X


Se execută minimum 3 evaluări consecutive pentru confirmarea determinismului.
Rezultatul trebuie să fie identic pentru:
* decision_outcome;
* reason_code;
* action_output.
________________


13. REGRESSION TEST
Orice modificare a unei reguli declanșează executarea testelor existente ale regulii.
Se verifică:
Current Rule Version
        ↓
Existing Test Suite
        ↓
Previous Expected Outcomes
        ↓
New Results
        ↓
Regression Status


O modificare care schimbă intenționat rezultatul unei reguli generează o versiune nouă și actualizarea explicită a testelor.
________________


14. VERSION TEST
Fiecare versiune a unei reguli trebuie testată independent.
Exemplu:
RULE-CONTACT-QUAL-001
Version 1.0.0 → VALIDATED
Version 1.1.0 → TESTING
Version 2.0.0 → DRAFT


Versiunile istorice rămân disponibile pentru audit și reproducerea deciziilor anterioare.
________________


15. VALIDITY PERIOD TEST
Se verifică respectarea:
effective_from
effective_until


Testele obligatorii includ:
Before effective_from
At effective_from
During validity period
At effective_until
After effective_until


Motorul trebuie să selecteze exclusiv versiunea validă pentru momentul evaluării.
________________


16. DECISION OUTCOME TEST
Se verifică faptul că rezultatul logic al regulii corespunde contractului definit.
Rezultatele standard pot include:
TRUE
FALSE
QUALIFIED
NOT_QUALIFIED
THRESHOLD_MET
THRESHOLD_NOT_MET
PRIORITY_HIGH
PRIORITY_MEDIUM
PRIORITY_LOW
INVALID_CONTEXT


Rezultatul trebuie să fie definit în contractul regulii.
________________


17. ACTION OUTPUT TEST
După evaluarea regulii se verifică acțiunea generată.
Exemple:
UPDATE_STATE
CREATE_MISSION
TRIGGER_WORKFLOW
UPDATE_SCORE
CREATE_NOTIFICATION
CREATE_FOLLOW_UP
NO_ACTION


Testul verifică simultan:
Decision Outcome
        ↓
Action Output


Astfel se confirmă că rezultatul logic produce acțiunea operațională corectă.
________________


18. AUDIT TEST
Fiecare evaluare care produce o decizie operațională trebuie să poată fi urmărită în AuditLog.
Auditul trebuie să permită identificarea:
Rule Code
Rule Version
Business Object
Object ID
Input Context Reference
Decision Outcome
Reason Code
Action Output
Engine
Workflow
Timestamp
Actor
Correlation ID


Testul este valid atunci când decizia poate fi reconstruită integral din datele de audit.
________________


19. ENGINE INTEGRATION TEST
Regula trebuie testată în contextul Engine-ului care o utilizează.
Exemplu:
Event
 ↓
Workflow
 ↓
MissionEngine
 ↓
Rule Evaluation
 ↓
Decision Outcome
 ↓
Action
 ↓
Event


Se verifică:
* identificarea corectă a regulii;
* transmiterea corectă a contextului;
* evaluarea corectă;
* interpretarea rezultatului;
* executarea acțiunii;
* generarea evenimentelor secundare.
________________


20. WORKFLOW INTEGRATION TEST
Atunci când o regulă declanșează un Workflow, se verifică întregul traseu:
Rule
 ↓
Decision
 ↓
Workflow Trigger
 ↓
Workflow Instance
 ↓
Workflow Execution
 ↓
Expected Outcome


Testul confirmă integrarea dintre:
Rule Layer → Engine Layer → Workflow Layer.
________________


21. EVENT INTEGRATION TEST
Atunci când evaluarea unei reguli produce un eveniment, acesta trebuie verificat în Event Store.
Se validează:
* event_id;
* event_type;
* source_object;
* source_object_id;
* timestamp;
* payload;
* actor_id;
* correlation_id.
Evenimentul trebuie să poată fi corelat cu evaluarea regulii care l-a generat.
________________


22. TEST MATRIX
Fiecare regulă activă trebuie să aibă minimum următoarea matrice:
Test
	Obligatoriu
	Schema Test
	DA
	Structural Test
	DA
	Positive Test
	DA
	Negative Test
	DA
	Boundary Test
	DA, pentru praguri
	NULL / Missing Data
	DA
	Type Validation
	DA
	Determinism Test
	DA
	Regression Test
	DA
	Version Test
	DA
	Validity Period Test
	DA
	Decision Outcome Test
	DA
	Action Output Test
	DA
	Audit Test
	DA
	Engine Integration Test
	DA
	Workflow Integration Test
	DA, când există Workflow
	Event Integration Test
	DA, când există Event
	________________


23. CRITERII DE VALIDARE
O regulă primește statutul:
VALIDATED


atunci când:
1. toate testele obligatorii au statut PASSED;
2. schema este validă;
3. AST-ul este valid;
4. rezultatul este determinist;
5. pragurile au fost testate;
6. cazurile negative au fost testate;
7. datele lipsă au un comportament definit;
8. integrarea cu Engine-ul este validată;
9. AuditLog-ul poate reconstrui decizia;
10. Workflow-urile și evenimentele asociate sunt validate;
11. versiunea testată este identificată explicit;
12. rezultatele testelor sunt păstrate pentru audit.
________________


24. TEST FAILURE
Dacă un test obligatoriu eșuează:
Rule Status
    ↓
FAILED
    ↓
Rule cannot become ACTIVE
    ↓
Issue recorded
    ↓
Rule corrected
    ↓
Test Suite re-executed


Corecția unei reguli produce o nouă versiune atunci când modificarea afectează logica decizională.
________________


25. TEST RESULT MODEL
Rezultatul unui test utilizează următoarea structură standard:
TEST RESULT


test_id
rule_id
rule_code
rule_version
test_type
input_context
expected_outcome
actual_outcome
expected_reason_code
actual_reason_code
expected_actions
actual_actions
test_status
execution_time_ms
executed_at
executed_by
correlation_id
metadata


________________


26. RULE TEST SUITE
Fiecare regulă activă are asociat un Rule Test Suite.
Structura:
RULE
  ↓
RULE TEST SUITE
  ├── Schema Tests
  ├── Structural Tests
  ├── Positive Tests
  ├── Negative Tests
  ├── Boundary Tests
  ├── Null Tests
  ├── Type Tests
  ├── Determinism Tests
  ├── Regression Tests
  ├── Integration Tests
  └── Audit Tests


Rule Test Suite devine parte din istoricul permanent al regulii.
________________


27. RELAȚIA CU RESTUL ARHITECTURII
RULE-TEST-001 se conectează cu:
RULE-ARCH-001
        ↓
RULE-REG-001
        ↓
RULE-MODEL-001
        ↓
RULE-TEST-001
        ↓
ENGINE ARCHITECTURE
        ↓
WORKFLOW ENGINE
        ↓
EVENT STORE
        ↓
AUDITLOG
        ↓
KPI / PERFORMANCE


Rolurile sunt clar separate:
* RULE-ARCH-001 definește standardul arhitectural;
* RULE-REG-001 definește registrul regulilor;
* RULE-MODEL-001 definește structura tehnică;
* RULE-TEST-001 validează comportamentul;
* Engine-urile execută regulile;
* Workflow-urile orchestrează procesele;
* Event Store păstrează evenimentele;
* AuditLog păstrează trasabilitatea;
* KPI Architecture utilizează rezultatele relevante.
________________


28. REGULA DE ACTIVARE
Activarea unei reguli respectă următorul flux:
PROPOSED
   ↓
DRAFT
   ↓
TESTING
   ↓
ALL REQUIRED TESTS PASSED
   ↓
VALIDATED
   ↓
APPROVED
   ↓
ACTIVE


Activarea este permisă exclusiv pentru versiunea validată.
________________


29. REGULA DE DEZACTIVARE
O regulă activă poate trece în:
DEPRECATED


atunci când este înlocuită de o versiune nouă.
Fluxul:
ACTIVE v1.0
      ↓
ACTIVE v2.0
      ↓
v1.0 = DEPRECATED


Istoricul versiunii vechi rămâne disponibil pentru audit și reproducerea deciziilor istorice.
________________


30. GUVERNANȚA TESTELOR
Fiecare modificare a următoarelor componente declanșează revalidarea regulii:
* conditions_json;
* thresholds_ref;
* decision_outcome;
* action_output;
* business_object_type;
* engine_id;
* perioada de valabilitate;
* operatorii utilizați;
* sursele de date.
Modificările structurale sau logice majore generează versiune nouă a regulii.
________________


31. STATUS OFICIAL
Document: NicMar OS — Core Architecture — Document 07.4
Identificator: RULE-TEST-001
Business Domain: Core Architecture / Rules & Decision Architecture
Nivel: Nivelul 5 — Rules & Decision Architecture
Versiune: 1.0
Status: 🔒 VALIDAT / SSOT
Metodologie: Deterministic Rule Testing & Validation
________________


32. ÎNCHIDEREA NIVELULUI 5
Odată cu finalizarea:
RULE-ARCH-001
      ↓
RULE-REG-001
      ↓
RULE-MODEL-001
      ↓
RULE-TEST-001


stratul fundamental Rules & Decision Architecture este complet definit.
NIVELUL 5 — RULES & DECISION ARCHITECTURE
STATUS: 🔒 100% ÎNCHIS
Următorul nivel oficial din Master Architecture Roadmap este:
NIVELUL 6
KPI & PERFORMANCE ARCHITECTURE


Document 08
        ↓
KPI-ARCH-001
KPI & Performance Architecture Standard


Acesta va defini standardul matematic și operațional pentru indicatorii NicMar OS, inclusiv:
DIS, CRH, PDI, PIP, OPI, ERI, OAS, LRI, AMS, MEI, TDI.








NICMAR OS — CORE ARCHITECTURE
DOCUMENT 08 — KPI & PERFORMANCE ARCHITECTURE
KPI & PERFORMANCE ARCHITECTURE STANDARD
Identificator: KPI-ARCH-001
Business Domain: Core Architecture / KPI & Performance Architecture
Nivel: Nivelul 6 – KPI & Performance Architecture
Versiune: 1.0
Status: 🟡 PROPUNERE PENTRU VALIDARE
Metodologie: Event-Driven Performance Measurement & Deterministic KPI Architecture
SSOT Sursă:
* Documentul 01 – Business Objects
* DB-ARCH-001 – Database Architecture Standard
* DB-BO-001 – Business Object Data Model
* DB-REL-001 – Relationship & Foreign Key Model
* DB-STATE-001 – State Persistence Model
* DB-EVENT-001 – Event Store Model
* DB-AUDIT-001 – AuditLog Model
* DB-KPI-001 – KPI & Score Model
* ENG-ARCH-001 – Engine Architecture Standard
* RULE-ARCH-001 – Business Rules & Decision Architecture
* RULE-MODEL-001 – Rule Definition & Evaluation Model
Documente derivate:
* KPI-REG-001 – KPI Registry
* KPI-MODEL-001 – KPI Definition & Calculation Model
* KPI-TEST-001 – KPI Testing & Validation
* KPI-DASH-001 – KPI Dashboard & Presentation Model
________________


1. SCOPUL DOCUMENTULUI
KPI-ARCH-001 definește standardul arhitectural oficial pentru indicatorii de performanță, scorurile și măsurătorile operaționale din NicMar OS.
Acest document stabilește:
* ce reprezintă un KPI în NicMar OS;
* cum este identificat și versionat;
* ce structură trebuie să aibă fiecare KPI;
* cum este legat un KPI de Business Objects;
* cum este legat un KPI de Engine-uri;
* cum este legat un KPI de Rules;
* ce evenimente pot declanșa recalcularea;
* cum este persistat rezultatul;
* cum este transmis către Dashboard;
* cum este auditat calculul;
* cum este menținută consistența între KPI, Score, Rules, Engines și Event Store.
KPI-ARCH-001 este standardul structural.
Definițiile matematice și formulele concrete ale KPI-urilor sunt stabilite în documentele derivate.
________________


2. POZIȚIONAREA KPI ÎN ARHITECTURA NICMAR OS
KPI Layer este poziționat între datele operaționale, Engine Layer, Rules Layer și Dashboard/Application Layer.
Fluxul oficial este:
Business Objects
↓
State / Events
↓
Event Store
↓
Engine
↓
KPI Calculation
↓
KPI / Score
↓
Rules & Decision
↓
Workflow / Mission / Notification
↓
Dashboard / Reporting
↓
AuditLog
KPI-urile reprezintă stratul standardizat prin care activitatea operațională este transformată în măsurători de performanță.
________________


3. PRINCIPII ARHITECTURALE KPI
3.1. Single Source of Truth
Fiecare KPI oficial are un singur cod canonic și o singură definiție activă pentru fiecare versiune.
Același KPI nu poate avea definiții matematice concurente în module diferite ale sistemului.
3.2. Determinism
Pentru aceleași date de intrare, aceeași perioadă de calcul și aceeași versiune de KPI, rezultatul trebuie să fie identic.
3.3. Trasabilitate
Fiecare valoare KPI trebuie să poată fi urmărită până la:
* datele de intrare;
* Business Objects sursă;
* evenimentul declanșator;
* Engine-ul care a executat calculul;
* versiunea formulei;
* momentul calculului;
* rezultatul calculului.
3.4. Versionare
Orice modificare a definiției, formulei, pragurilor sau surselor de date generează o versiune nouă a KPI-ului.
Istoricul versiunilor este păstrat pentru audit și comparații istorice.
3.5. Separarea Calculului de Prezentare
Calculul KPI este realizat independent de UI.
Dashboard-ul consumă rezultatele calculate și persistate.
3.6. Event-Driven Calculation
Recalcularea KPI-urilor este declanșată de evenimente relevante sau de procese programate, în funcție de definiția fiecărui KPI.
3.7. Auditabilitate
Fiecare calcul semnificativ trebuie să poată fi corelat cu Event Store și AuditLog.
________________


4. MODELUL STANDARD AL UNUI KPI
Fiecare KPI oficial trebuie să conțină următoarele elemente:
4.1. Identitate
* metric_id
* metric_code
* metric_name
* version
* status
metric_code este identificatorul canonic al indicatorului.
4.2. Definiție
* definition
* business_purpose
* measurement_scope
* target_entity
Definește exact ce măsoară KPI-ul și pentru ce entitate este calculat.
4.3. Formula
* formula
* calculation_method
* aggregation_method
Formula trebuie să fie deterministă și versionată.
4.4. Input-uri
* input_metrics
* input_fields
* input_events
* input_objects
* time_window
Sunt definite toate datele necesare calculului.
4.5. Data Source
Pentru fiecare KPI trebuie identificată sursa oficială:
* Business Object;
* tabel persistent;
* Event Store;
* State History;
* AuditLog;
* alt KPI;
* Score;
* agregare derivată.
4.6. Update Trigger
Fiecare KPI trebuie să definească evenimentele sau procesele care determină recalcularea.
Exemple:
* Business Event;
* State Transition;
* MissionCompleted;
* MissionValidated;
* Daily Review;
* scheduled calculation;
* period closing.
4.7. Calculation Frequency
Fiecare KPI trebuie să aibă o frecvență explicită:
* real-time;
* event-driven;
* hourly;
* daily;
* weekly;
* monthly;
* on-demand.
4.8. Owner Engine
Fiecare KPI trebuie asociat cu Engine-ul responsabil de calcul.
Asocierea se face exclusiv cu Engine-uri existente în ENG-ARCH-001.
4.9. Storage
Rezultatul calculului este persistat conform DB-KPI-001.
Structura minimă include:
* metric_id;
* metric_code;
* entity_type;
* entity_id;
* score_value;
* calculation_date;
* engine_source;
* metadata;
* version.
4.10. Dashboard Representation
Fiecare KPI trebuie să definească modul în care este consumat de Dashboard:
* numeric;
* procentual;
* scor;
* trend;
* status;
* ranking;
* indicator comparativ;
* agregare pe perioadă.
________________


5. MODELUL KPI — FLUX COMPLET DE CALCUL
Fluxul standard este:
EVENT
↓
IDENTIFICARE KPI
↓
LOAD INPUT DATA
↓
VALIDARE INPUT
↓
KPI ENGINE
↓
APLICARE FORMULĂ
↓
CALCUL RESULT
↓
VALIDARE RESULT
↓
PERSIST KPI
↓
UPDATE SCORE
↓
RULE EVALUATION
↓
WORKFLOW / ACTION
↓
DASHBOARD
↓
AUDIT
Fiecare etapă trebuie să fie trasabilă.
________________


6. RELAȚIA KPI CU EVENT STORE
Evenimentele reprezintă sursa temporală pentru activitatea operațională.
Exemplu:
MissionCompleted
↓
MissionValidated
↓
KPI recalculation
↓
DIS update
↓
PerformanceEvaluationEngine
↓
Dashboard
Acest model respectă fluxul deja definit în arhitectura persistentă NicMar OS, în care evenimentul produce tranziția de stare, actualizarea istoricului, Event Store și AuditLog.
________________


7. RELAȚIA KPI CU ENGINE ARCHITECTURE
Engine-urile execută calculul KPI conform responsabilităților definite în ENG-ARCH-001.
Principiul este:
EVENT
↓
WORKFLOW
↓
ENGINE
↓
KPI CALCULATION
↓
KPI RESULT
Engine-ul responsabil trebuie să fie identificabil pentru fiecare KPI.
KPI Layer nu duplică logica Engine-urilor.
KPI Layer standardizează măsurarea rezultatului.
________________


8. RELAȚIA KPI CU RULES & DECISION ARCHITECTURE
KPI-urile pot furniza input pentru Rules & Decision Layer.
Flux:
KPI VALUE
↓
RULE
↓
THRESHOLD
↓
DECISION
↓
ACTION
Exemple arhitecturale:
KPI ≥ Threshold
↓
Rule Evaluation
↓
Decision Outcome
↓
Workflow Trigger
KPI < Threshold
↓
Rule Evaluation
↓
Reactivation / Priority / Mission
↓
Workflow
Regulile concrete sunt definite în RULE-ARCH-001 și RULE-MODEL-001.
________________


9. REGISTRUL OFICIAL AL KPI-URILOR
Catalogul oficial de KPI-uri confirmat în arhitectura NicMar OS conține:
1. DIS
2. CRH
3. PDI
4. PIP
5. OPI
6. ERI
7. OAS
8. LRI
9. AMS
10. MEI
11. TDI
Această listă reprezintă registrul de indicatori care trebuie închis formal în Nivelul 6.
Pentru fiecare indicator se va defini separat:
* definiția;
* scopul;
* formula;
* input-urile;
* sursele de date;
* trigger-ele;
* frecvența;
* Engine-ul proprietar;
* metoda de stocare;
* reprezentarea în Dashboard;
* regulile asociate;
* testele de validare.
Lista de mai sus este derivată din Master Architecture și reprezintă setul de KPI-uri care trebuie închis formal în Nivelul 6.
________________


10. KPI VS SCORE
NicMar OS separă conceptual:
KPI
indicator măsurat conform unei definiții și formule.
SCORE
valoare derivată sau agregată utilizată pentru evaluare, clasificare sau decizie.
Flux:
Raw Data
↓
KPI
↓
Score
↓
Rule
↓
Decision
Un KPI poate alimenta unul sau mai multe Score-uri.
Un Score poate utiliza unul sau mai multe KPI-uri.
Relațiile exacte sunt definite în KPI-MODEL-001.
________________


11. KPI PERIODIC ȘI KPI EVENT-DRIVEN
Sistemul suportă două categorii principale:
11.1. Event-Driven KPI
Recalcularea este declanșată de un eveniment.
Exemplu:
MissionValidated
↓
KPI Calculation
↓
DIS Update
11.2. Periodic KPI
Calculul este realizat la un interval prestabilit.
Exemplu:
Daily Review
↓
Daily KPI Calculation
↓
Score Update
Un KPI poate utiliza simultan evenimente declanșatoare și recalculări periodice, dacă definiția sa o impune.
________________


12. KPI TIME WINDOW
Fiecare KPI trebuie să specifice intervalul temporal asupra căruia se calculează.
Exemple de categorii:
* instant;
* zi;
* săptămână;
* lună;
* rolling period;
* lifetime;
* custom period.
Time window-ul face parte din definiția KPI și trebuie versionat împreună cu formula.
________________


13. VALIDAREA DATELOR DE INTRARE
Înaintea calculului:
1. se identifică toate input-urile obligatorii;
2. se verifică existența datelor;
3. se verifică tipurile de date;
4. se verifică perioada;
5. se verifică versiunea sursei;
6. se verifică integritatea relațiilor;
7. se execută calculul.
Un KPI cu input-uri incomplete trebuie să producă un rezultat controlat și auditabil, conform regulilor definite în KPI-MODEL-001.
________________


14. VERSIONAREA KPI
Structura minimă:
metric_code
version
effective_from
effective_until
status
Exemplu:
DIS
v1.0
ACTIVE
O modificare semnificativă a formulei produce:
DIS
v2.0
ACTIVE
Versiunea anterioară rămâne disponibilă pentru istoricul calculurilor.
________________


15. KPI STATUS LIFECYCLE
KPI-ul urmează următorul ciclu:
PROPOSED
↓
DRAFT
↓
VALIDATED
↓
ACTIVE
↓
DEPRECATED
↓
ARCHIVED
Un KPI intră în calcul operațional numai după VALIDATED și ACTIVE.
________________


16. KPI AUDIT MODEL
Pentru fiecare calcul trebuie să poată fi identificat:
* KPI;
* versiunea;
* entitatea;
* perioada;
* input-urile;
* formula;
* Engine-ul;
* timestamp-ul;
* rezultatul;
* event/correlation ID.
Flux:
KPI Calculation
↓
KPI Result
↓
AuditLog
↓
Correlation ID
↓
Event Store
________________


17. KPI CONSISTENCY RULES
Se aplică următoarele reguli:
1. Un metric_code identifică un singur KPI.
2. O versiune KPI are o singură formulă activă.
3. Formula trebuie să fie deterministă.
4. Toate input-urile trebuie identificate.
5. Sursa fiecărui input trebuie identificată.
6. Engine-ul proprietar trebuie identificat.
7. Frecvența calculului trebuie definită.
8. Time window-ul trebuie definit.
9. Rezultatul trebuie persistat.
10. Calculul trebuie auditabil.
11. Modificarea formulei generează o versiune nouă.
12. Dashboard-ul consumă rezultatul oficial persistat.
________________


18. DEPENDENȚE
KPI Architecture depinde de:
Business Objects
↓
Database Architecture
↓
Event Store
↓
Engine Architecture
↓
Rules Architecture
↓
KPI Architecture
Nivelurile următoare consumă KPI Architecture:
* Identity & Security;
* Notification;
* API;
* AI / Agent Architecture;
* Application;
* UI / UX;
* Integrations;
* Observability;
* Testing;
* Infrastructure;
* Implementation.
Master Architecture stabilește că KPI & Performance Architecture definește matematic indicatorii și, pentru fiecare KPI, trebuie stabilite definiția, formula, input-urile, sursa de date, trigger-ul, frecvența, Engine-ul proprietar, stocarea și reprezentarea în Dashboard.
________________


19. DOCUMENTELE DERIVATE DIN KPI-ARCH-001
Structura oficială:
KPI-ARCH-001
KPI & Performance Architecture Standard
│
├── KPI-REG-001
│ KPI Registry
│
├── KPI-MODEL-001
│ KPI Definition & Calculation Model
│
├── KPI-TEST-001
│ KPI Testing & Validation
│
└── KPI-DASH-001
KPI Dashboard & Presentation Model
________________


20. CONDIȚIA DE ÎNCHIDERE A NIVELULUI 6
Nivelul 6 — KPI & Performance Architecture este considerat complet atunci când sunt validate și înghețate:
KPI-ARCH-001
↓
KPI-REG-001
↓
KPI-MODEL-001
↓
KPI-TEST-001
↓
KPI-DASH-001
↓
🔒 NIVELUL 6
KPI & PERFORMANCE ARCHITECTURE
100% ÎNCHIS
________________


21. POZIȚIA ÎN MASTER ARCHITECTURE ROADMAP
Nivelul 1
CORE ARCHITECTURE
↓
Nivelul 2
DATABASE ARCHITECTURE
↓
Nivelul 3
EVENT & WORKFLOW ARCHITECTURE
↓
Nivelul 4
ENGINE ARCHITECTURE
↓
Nivelul 5
RULES & DECISION ARCHITECTURE
↓
Nivelul 6
KPI & PERFORMANCE ARCHITECTURE
↓
Nivelul 7
IDENTITY, ROLES & SECURITY
↓
Nivelul 8
NOTIFICATION
↓
Nivelul 9
API & SERVICES
↓
Nivelul 10
AI / AGENT ARCHITECTURE
↓
NIVELURILE URMĂTOARE
↓
NICMAR OS
________________


22. STATUS ARHITECTURAL
Document:
NicMar OS – Core Architecture – Document 08
Identificator:
KPI-ARCH-001
Business Domain:
Core Architecture / KPI & Performance Architecture
Nivel:
Nivelul 6 – KPI & Performance Architecture
Versiune:
1.0
Status:
Rol:
SSOT pentru standardul arhitectural KPI.
Următorul document:
KPI-REG-001 — KPI Registry
________________


23. REGULĂ DE ÎNGHEȚARE
După validarea oficială:
KPI-ARCH-001 = 🔒 ÎNGHEȚAT
Orice modificare ulterioară a standardului se realizează prin versiune arhitecturală nouă și proces formal de schimbare.
________________










Da. Intrăm direct în KPI-REG-001. Am verificat materialele existente ca să păstrăm exact terminologia deja folosită. Sursa confirmă cei 11 KPI ai roadmap-ului, iar PerformanceEvaluationEngine este motorul care îi centralizează.
Un punct important de arhitectură: în materialele existente apare și PES și ORE în lista de metric codes din Business Objects, în timp ce roadmap-ul Nivelului 6 enumeră oficial DIS, CRH, PDI, PIP, OPI, ERI, OAS, LRI, AMS, MEI, TDI. Pentru KPI-REG-001 păstrez registrul oficial al Nivelului 6 cu cei 11 KPI; PES și ORE rămân menționate ca metric codes existente în modelul Business Object și vor fi reconciliate formal în etapa de validare a registrului.
Mai jos este documentul gata de copiat.
NICMAR OS — CORE ARCHITECTURE
DOCUMENT 08.1 — KPI REGISTRY
KPI REGISTRY
Identificator: KPI-REG-001
Business Domain: Core Architecture / KPI & Performance Architecture
Nivel: Nivelul 6 – KPI & Performance Architecture
Versiune: 1.0
Status: 🟡 PROPUNERE PENTRU VALIDARE
Metodologie: Event-Driven Performance Measurement & Deterministic KPI Architecture
SSOT Sursă:
* KPI-ARCH-001
* Documentul 01 – Business Objects
* DB-ARCH-001
* DB-KPI-001
* ENG-ARCH-001
* RULE-ARCH-001
________________


1. SCOPUL DOCUMENTULUI
KPI-REG-001 definește registrul oficial al indicatorilor de performanță utilizați în NicMar OS.
Registrul stabilește pentru fiecare KPI:
* codul oficial;
* denumirea oficială;
* scopul;
* domeniul funcțional;
* entitatea principală măsurată;
* categoria KPI;
* Engine-ul responsabil;
* obiectele Business Objects relevante;
* relația cu Score;
* relația cu Rules;
* starea în lifecycle;
* referința către documentul tehnic în care formula va fi definită.
KPI-REG-001 reprezintă catalogul oficial al KPI-urilor.
Formulele matematice și algoritmii concreți sunt definiți ulterior în:
KPI-MODEL-001 — KPI Definition & Calculation Model
________________


2. PRINCIPIUL REGISTRULUI
Fiecare KPI oficial trebuie să aibă:
KPI Code
↓
KPI Name
↓
Business Purpose
↓
Target Entity
↓
Category
↓
Owner Engine
↓
Input Sources
↓
Calculation Model
↓
Score Relationship
↓
Rules Relationship
↓
Dashboard Representation
Un KPI poate fi utilizat de mai multe Engine-uri, Rules și Workflows, însă are un singur Owner Engine responsabil pentru calculul său oficial.
________________


3. REGISTRUL OFICIAL — KPI-URI NICMAR OS
Registrul oficial al Nivelului 6 conține 11 KPI:
1. DIS
2. CRH
3. PDI
4. PIP
5. OPI
6. ERI
7. OAS
8. LRI
9. AMS
10. MEI
11. TDI
Această listă este confirmată în Master Architecture pentru Nivelul 6.
________________


4. KPI-001 — DIS
Cod:
DIS
Denumire oficială:
Daily Impact Score
Categorie:
Operational Performance / Daily Execution
Scop:
Măsoară impactul operațional realizat într-o perioadă zilnică de activitate.
Entitate principală:
User
Business Objects relevante:
* Mission
* Task
* DailyPlan
* DailyReview
* Habit
* FollowUp
* Meeting
* Conversation
* Partner
* Client
Owner Engine:
PerformanceEvaluationEngine
Engine-uri asociate:
* MissionEngine
* PriorityEngine
* ContinuityEngine
Input-uri principale:
* misiuni;
* activități executate;
* misiuni validate;
* activități planificate;
* activități finalizate;
* rezultate operaționale relevante.
Evenimente relevante:
* MissionGenerated
* MissionCompleted
* MissionValidated
* activități zilnice relevante.
Relație Score:
DIS poate alimenta Score-ul general de performanță.
Relație Rules:
Poate furniza praguri pentru:
* PriorityEngine;
* ContinuityEngine;
* MissionEngine;
* reactivare;
* recalibrarea activității.
Dashboard:
* scor zilnic;
* evoluție;
* trend;
* comparație planificat / realizat.
Formula:
Va fi definită în KPI-MODEL-001.
Status:
PROPOSED
________________


5. KPI-002 — CRH
Cod:
CRH
Denumire oficială:
Customer Relationship Health
Categorie:
Relationship Performance
Scop:
Măsoară sănătatea relației cu clientul și calitatea relației comerciale.
Entitate principală:
Client
Business Objects relevante:
* Client
* Contact
* Conversation
* FollowUp
* Meeting
* Experience
* Objection
* Assessment
Owner Engine:
CustomerRelationshipEngine
Engine-uri asociate:
* RelationshipEngine
* FollowUpEngine
* ContinuityEngine
* PerformanceEvaluationEngine
Input-uri principale:
* interacțiuni;
* conversații;
* follow-up-uri;
* experiențe;
* activitatea relațională;
* starea clientului;
* evenimente relevante ale clientului.
Relație Score:
CRH poate alimenta scoruri relaționale și evaluarea generală.
Relație Rules:
Poate declanșa:
* follow-up;
* reactivare;
* misiuni relaționale;
* prioritizare.
Dashboard:
* scor relațional;
* trend;
* status relație;
* segmente de sănătate relațională.
Formula:
Va fi definită în KPI-MODEL-001.
Status:
PROPOSED
________________


6. KPI-003 — PDI
Cod:
PDI
Denumire oficială:
Partner Development Index
Categorie:
Partner Development
Scop:
Măsoară evoluția și dezvoltarea partenerului de-a lungul parcursului operațional.
Entitate principală:
Partner
Business Objects relevante:
* Partner
* Mission
* Habit
* Assessment
* Experience
* Team
* Leader
* Conversation
* Contact
Owner Engine:
PerformanceEvaluationEngine
Engine-uri asociate:
* PartnerRelationshipEngine
* ContinuityEngine
* MissionEngine
* LeadershipDevelopmentEngine
* MentorGuidanceEngine
Input-uri principale:
* progresul partenerului;
* activități;
* rezultate;
* competențe;
* autonomie;
* leadership;
* activitatea relațională.
Evenimente relevante:
* PartnerActivated
* OnboardingCompleted
* FirstResultAchieved
* AutonomyReached
* LeadershipActivated
* PartnerReactivated
* InactivityDetected.
Documentele sursă confirmă PDI ca indicator al dezvoltării partenerului.
Relație Score:
PDI contribuie la evaluarea dezvoltării partenerului.
Relație Rules:
Poate participa la decizii privind:
* progres;
* autonomie;
* prioritizare;
* dezvoltare;
* reactivare.
Dashboard:
* progres;
* trend;
* nivel de dezvoltare;
* comparație temporală.
Formula:
Va fi definită în KPI-MODEL-001.
Status:
PROPOSED
________________


7. KPI-004 — PIP
Cod:
PIP
Denumire oficială:
Partner Integration Progress
Categorie:
Partner Integration
Scop:
Măsoară progresul partenerului prin etapa de integrare și onboarding.
Entitate principală:
Partner
Business Objects relevante:
* Partner
* Mission
* Habit
* Assessment
* Contact
* Conversation
Owner Engine:
PerformanceEvaluationEngine
Engine-uri asociate:
* PartnerRelationshipEngine
* MissionEngine
* HabitEngine
* ContinuityEngine
Evenimente relevante:
* PartnerActivated
* OnboardingStarted
* OnboardingCompleted
* OnboardingTimeout.
Sursele existente confirmă PIP ca KPI influențat de evenimentele de onboarding și timeout.
Relație Score:
PIP furnizează măsurarea progresului integrării.
Relație Rules:
Poate alimenta praguri pentru:
* continuarea onboarding-ului;
* intervenția mentorului;
* misiuni;
* follow-up;
* reactivare.
Dashboard:
* progres onboarding;
* procent / scor;
* etapă curentă;
* trend.
Formula:
Va fi definită în KPI-MODEL-001.
Status:
PROPOSED
________________


8. KPI-005 — OPI
Cod:
OPI
Denumire oficială:
Overall Performance Index
Categorie:
Overall Performance
Scop:
Măsoară performanța generală prin agregarea indicatorilor relevanți ai sistemului.
Entitate principală:
User
Entități secundare:
* Partner
* Team
* Leader
Business Objects relevante:
* Mission
* Partner
* Client
* KPI
* Score
* Assessment
* DailyReview
Owner Engine:
PerformanceEvaluationEngine
Input-uri:
* KPI operaționali;
* KPI relaționali;
* KPI de dezvoltare;
* KPI de leadership;
* KPI de autonomie;
* alte componente aprobate în KPI-MODEL-001.
Relație Score:
OPI reprezintă un indicator agregat de performanță.
Relație Rules:
Poate alimenta:
* evaluări;
* prioritizare;
* recalibrare;
* misiuni;
* recomandări de dezvoltare.
Dashboard:
* scor general;
* trend;
* componente;
* evoluție temporală.
Formula:
Va fi definită în KPI-MODEL-001.
Status:
PROPOSED
________________


9. KPI-006 — ERI
Cod:
ERI
Denumire oficială:
ERI
Categorie:
Performance / Relationship / Operational Evaluation
Scop:
Indicator oficial al arhitecturii NicMar OS.
Definiția semantică extinsă și formula exactă vor fi stabilite în KPI-MODEL-001, pe baza documentelor SSOT disponibile.
Entitate principală:
Va fi stabilită în KPI-MODEL-001.
Owner Engine:
PerformanceEvaluationEngine
Relație Score:
Rezultatul poate alimenta Score și evaluările de performanță.
Relație Rules:
Poate furniza input pentru reguli și praguri.
Dashboard:
* scor;
* trend;
* evoluție.
Formula:
KPI-MODEL-001
Status:
PROPOSED
________________


10. KPI-007 — OAS
Cod:
OAS
Denumire oficială:
OAS
Categorie:
Performance / Operational Assessment
Scop:
Indicator oficial utilizat în arhitectura de performanță NicMar OS.
Definiția semantică extinsă și formula exactă vor fi stabilite în KPI-MODEL-001.
Entitate principală:
Va fi stabilită în KPI-MODEL-001.
Owner Engine:
PerformanceEvaluationEngine
Relație Score:
Poate alimenta scoruri agregate.
Relație Rules:
Poate alimenta praguri și decizii.
Dashboard:
* scor;
* trend;
* evoluție.
Formula:
KPI-MODEL-001
Status:
PROPOSED
________________


11. KPI-008 — LRI
Cod:
LRI
Denumire oficială:
Leadership Readiness Index
Categorie:
Leadership Development
Scop:
Măsoară nivelul de pregătire al partenerului pentru asumarea rolului de leadership.
Entitate principală:
Partner
Business Objects relevante:
* Partner
* Leader
* Team
* Assessment
* Mission
* Habit
* Experience
Owner Engine:
PerformanceEvaluationEngine
Engine-uri asociate:
* LeadershipDevelopmentEngine
* TeamCoordinationEngine
* MentorGuidanceEngine
Evenimente relevante:
* LeadershipActivated
* AutonomyReached
* MentoringStarted
* PerformanceReviewTriggered.
Sursele existente confirmă LRI ca indicator asociat progresului spre leadership.
Relație Score:
LRI poate alimenta evaluarea maturității și dezvoltării liderului.
Relație Rules:
Poate furniza praguri pentru:
* leadership;
* dezvoltare;
* mentorat;
* coordonare de echipă.
Dashboard:
* readiness score;
* progres;
* trend;
* componente.
Formula:
Va fi definită în KPI-MODEL-001.
Status:
PROPOSED
________________


12. KPI-009 — AMS
Cod:
AMS
Denumire oficială:
Autonomy Maturity Score
Categorie:
Partner Maturity / Autonomy
Scop:
Măsoară nivelul de maturitate și autonomie operațională al partenerului.
Entitate principală:
Partner
Business Objects relevante:
* Partner
* Mission
* Habit
* Assessment
* Leader
* Team
Owner Engine:
PerformanceEvaluationEngine
Engine-uri asociate:
* PartnerRelationshipEngine
* MentorGuidanceEngine
* ContinuityEngine
* LeadershipDevelopmentEngine
Evenimente relevante:
* AutonomyReached
* LeadershipActivated
* MentoringStarted
* PerformanceReviewTriggered.
Sursele existente confirmă AMS ca indicator asociat autonomiei partenerului.
Relație Score:
AMS poate constitui componentă a evaluării generale.
Relație Rules:
Poate controla:
* intensitatea mentoratului;
* tranziția spre autonomie;
* dezvoltarea leadership-ului.
Dashboard:
* autonomie;
* maturitate;
* progres;
* trend.
Formula:
Va fi definită în KPI-MODEL-001.
Status:
PROPOSED
________________


13. KPI-010 — MEI
Cod:
MEI
Denumire oficială:
Mentoring Effectiveness Index
Categorie:
Mentoring / Leadership Development
Scop:
Măsoară eficiența activității de mentorat în dezvoltarea partenerilor și liderilor.
Entitate principală:
Leader / Partner
Business Objects relevante:
* Partner
* Leader
* Team
* Mission
* Assessment
* Experience
Owner Engine:
PerformanceEvaluationEngine
Engine-uri asociate:
* MentorGuidanceEngine
* LeadershipDevelopmentEngine
* TeamCoordinationEngine
Evenimente relevante:
* AutonomyReached
* LeadershipActivated
* MentoringStarted
* PerformanceReviewTriggered.
Sursele existente confirmă MEI ca indicator asociat mentoratului și dezvoltării liderilor.
Relație Score:
MEI contribuie la evaluarea eficienței mentoratului.
Relație Rules:
Poate alimenta:
* recomandări de mentorat;
* prioritizare;
* dezvoltare;
* intervenții de mentor.
Dashboard:
* eficiență mentorat;
* progres;
* trend;
* comparație temporală.
Formula:
Va fi definită în KPI-MODEL-001.
Status:
PROPOSED
________________


14. KPI-011 — TDI
Cod:
TDI
Denumire oficială:
Team Development Index
Categorie:
Team Development
Scop:
Măsoară dezvoltarea și evoluția unei echipe.
Entitate principală:
Team
Business Objects relevante:
* Team
* Partner
* Leader
* Mission
* Assessment
* KPI
* Score
Owner Engine:
PerformanceEvaluationEngine
Engine-uri asociate:
* TeamCoordinationEngine
* LeadershipDevelopmentEngine
* MentorGuidanceEngine
Evenimente relevante:
* LeadershipActivated
* MentoringStarted
* PerformanceReviewTriggered
* PartnerReactivated.
Sursele existente confirmă TDI ca indicator asociat dezvoltării echipei.
Relație Score:
TDI poate alimenta scorul colectiv al echipei.
Relație Rules:
Poate alimenta:
* prioritizare;
* dezvoltarea liderilor;
* coordonare;
* intervenții de mentorat.
Dashboard:
* scor echipă;
* trend;
* evoluție;
* comparație perioade.
Formula:
Va fi definită în KPI-MODEL-001.
Status:
PROPOSED
________________


15. MATRICEA OFICIALĂ KPI
Cod
	KPI
	Domeniu
	Entitate principală
	Owner Engine
	DIS
	Daily Impact Score
	Operational
	User
	PerformanceEvaluationEngine
	CRH
	Customer Relationship Health
	Relationship
	Client
	CustomerRelationshipEngine
	PDI
	Partner Development Index
	Partner Development
	Partner
	PerformanceEvaluationEngine
	PIP
	Partner Integration Progress
	Partner Integration
	Partner
	PerformanceEvaluationEngine
	OPI
	Overall Performance Index
	Overall Performance
	User
	PerformanceEvaluationEngine
	ERI
	ERI
	Performance / Evaluation
	TBD
	PerformanceEvaluationEngine
	OAS
	OAS
	Performance / Assessment
	TBD
	PerformanceEvaluationEngine
	LRI
	Leadership Readiness Index
	Leadership
	Partner
	PerformanceEvaluationEngine
	AMS
	Autonomy Maturity Score
	Autonomy
	Partner
	PerformanceEvaluationEngine
	MEI
	Mentoring Effectiveness Index
	Mentoring
	Leader / Partner
	PerformanceEvaluationEngine
	TDI
	Team Development Index
	Team Development
	Team
	PerformanceEvaluationEngine
	________________


16. RELAȚIA CU PERFORMANCEEVALUATIONENGINE
PerformanceEvaluationEngine reprezintă motorul central al stratului de performanță.
Responsabilitățile sale confirmate în arhitectura existentă includ:
* centralizarea KPI-urilor;
* analiza evoluției utilizatorului;
* detectarea tendințelor;
* identificarea punctelor forte;
* identificarea oportunităților de dezvoltare;
* generarea recomandării cu impact maxim;
* furnizarea tabloului unic de performanță.
Fluxul central este:
Business Data
↓
KPI Calculation
↓
PerformanceEvaluationEngine
↓
Performance View
↓
Rules / Decisions
↓
Missions / Workflows
↓
Dashboard
________________


17. RELAȚIA CU DATABASE ARCHITECTURE
KPI-urile sunt persistate în structura definită de Database Architecture.
Modelul existent include:
kpis
cu:
* id
* metric_code
* name
* description
* entity_type
* status
* calculation_rule_id
* created_at
* updated_at
* version
* context_data
* relations_meta
Rezultatele calculate sunt persistate prin structura KPI / Score definită în DB-KPI-001.
Modelul existent pentru Score include:
* kpi_id
* entity_type
* entity_id
* score_value
* calculated_at
* engine_source
* version
________________


18. RELAȚIA CU EVENT STORE
KPI-urile sunt actualizate pe baza evenimentelor relevante.
Exemplu:
PartnerActivated
↓
OnboardingStarted
↓
OnboardingCompleted
↓
PIP / DIS
↓
PerformanceEvaluationEngine
↓
KPI Result
Pentru partener, documentele existente asociază explicit evenimentele cu KPI precum PIP, DIS, PDI, AMS, LRI, MEI și TDI.
________________


19. RELAȚIA CU RULES
KPI-urile pot deveni input pentru Rule Engine.
Structura:
KPI
↓
Threshold
↓
Rule
↓
Decision
↓
Action
Exemple arhitecturale deja confirmate:
AMS
↓
Autonomy threshold
↓
AutonomyReached
PIP
↓
Onboarding progress
↓
Continuation / Intervention
LRI
↓
Leadership readiness
↓
Leadership decision
DIS
↓
Performance level
↓
Mission / Priority adjustment
Pragurile și formulele exacte vor fi definite în documentele dedicate.
________________


20. RELAȚIA CU DASHBOARD
Dashboard-ul consumă rezultatele KPI persistate.
Pentru fiecare KPI, Dashboard-ul poate utiliza:
* valoare curentă;
* valoare anterioară;
* trend;
* progres;
* comparație;
* status;
* componente;
* Score rezultat.
Dashboard-ul nu recalculează formula KPI.
Formula oficială aparține KPI Layer.
________________


21. KPI LIFECYCLE
Fiecare KPI urmează:
PROPOSED
↓
DRAFT
↓
VALIDATED
↓
ACTIVE
↓
DEPRECATED
↓
ARCHIVED
Registrul actual:
Toți cei 11 KPI
PROPOSED
Trecerea în ACTIVE se realizează după finalizarea:
KPI-MODEL-001
+
KPI-TEST-001
________________


22. RECONCILIEREA METRIC CODES EXISTENTE
Modelul Business Object existent include următoarele metric codes:
DIS
CRH
PDI
PES
ORE
OAS
PIP
MEI
TDI
LRI
ERI
OPI
AMS
Master Architecture pentru Nivelul 6 definește însă explicit următorul set oficial:
DIS
CRH
PDI
PIP
OPI
ERI
OAS
LRI
AMS
MEI
TDI
Prin urmare:
* PES și ORE rămân înregistrate ca metric codes existente în modelul Business Object;
* PES și ORE nu sunt incluse în registrul oficial principal al celor 11 KPI din Nivelul 6;
* statutul lor arhitectural va fi clarificat printr-o decizie formală de reconciliere;
* această reconciliere se finalizează înainte de înghețarea definitivă a KPI-REG-001.
________________


23. CONDIȚIA DE VALIDARE A REGISTRULUI
KPI-REG-001 poate fi validat după confirmarea:
1. listei finale de KPI;
2. denumirii oficiale;
3. entității principale;
4. categoriei;
5. Owner Engine;
6. metric codes suplimentare existente;
7. relației KPI → Score;
8. relației KPI → Rules;
9. relației KPI → Event Store.
Formulele concrete rămân în KPI-MODEL-001.
________________


24. DOCUMENTUL URMĂTOR
După validarea registrului:
KPI-REG-001
KPI Registry
↓
KPI-MODEL-001
KPI Definition & Calculation Model
↓
Definirea matematică a fiecărui KPI
↓
Inputs
↓
Data Sources
↓
Triggers
↓
Frequency
↓
Formula
↓
Calculation Algorithm
↓
Score Mapping
↓
KPI-TEST-001
↓
KPI-DASH-001
________________


25. STATUS ARHITECTURAL
Document:
NicMar OS – Core Architecture – Document 08.1
Identificator:
KPI-REG-001
Business Domain:
Core Architecture / KPI & Performance Architecture
Nivel:
Nivelul 6 – KPI & Performance Architecture
Versiune:
1.0
Status:
🟡 PROPUNERE PENTRU VALIDARE
Rol:
Registrul oficial al KPI-urilor NicMar OS.
Număr KPI în registrul principal:
11
Owner Engine central:
PerformanceEvaluationEngine
Următorul document:
KPI-MODEL-001 — KPI Definition & Calculation Model
________________


FINAL
KPI-REG-001 stabilește registrul oficial al celor 11 KPI ai Nivelului 6 și creează baza formală pentru definirea matematică, calculul, testarea și reprezentarea lor în NicMar OS.
REGISTRU KPI
↓
11 KPI OFICIALI
↓
KPI-MODEL-001
↓
FORMULE + CALCUL
↓
KPI-TEST-001
↓
VALIDARE
↓
KPI-DASH-001
↓
🔒 NIVELUL 6 — KPI & PERFORMANCE ARCHITECTURE








Da. Am verificat sursele disponibile pentru Nivelul 6. Există o nealiniere importantă în materialele existente: documentele confirmă 11 KPI-uri componente, iar OPI este definit separat ca indicator strategic compozit. În plus, sursele existente descriu componentele unor KPI-uri, dar nu conțin încă ponderile numerice finale și formulele matematice complete pentru fiecare indicator. De aceea, documentul de mai jos fixează modelul tehnic și formulele structurale fără să inventeze valori care nu sunt în SSOT.
NICMAR OS — CORE ARCHITECTURE
DOCUMENT 08.3 — KPI DEFINITION & CALCULATION MODEL
Identificator: KPI-MODEL-001
Business Domain: Core Architecture / KPI & Performance Architecture
Nivel: Nivelul 6 — KPI & Performance Architecture
Versiune: 1.0
Status: 🟡 PROPUNERE PENTRU VALIDARE
Metodologie: Deterministic KPI Calculation & Event-Driven Performance Evaluation
SSOT Surse:
* KPI-ARCH-001 — KPI & Performance Architecture Standard
* KPI-REG-001 — KPI Registry
* Documentul 01 — Business Objects
* DB-KPI-001 — KPI & Score Model
* EVT-CAT-* — Event Catalogs
* ENG-ARCH-001 — Engine Architecture
* RULE-ARCH-001 — Business Rules & Decision Architecture
============================================================
1. SCOPUL DOCUMENTULUI
============================================================
KPI-MODEL-001 definește modelul tehnic de definire și calcul al indicatorilor de performanță din NicMar OS.
Documentul stabilește pentru fiecare KPI:
   * definiția operațională;
   * obiectul sau utilizatorul evaluat;
   * input-urile;
   * sursele de date;
   * evenimentele care pot declanșa recalcularea;
   * frecvența calculului;
   * motorul responsabil;
   * metoda de normalizare;
   * metoda de agregare;
   * rezultatul calculului;
   * persistența rezultatului;
   * utilizarea în Dashboard;
   * relația cu PerformanceEvaluationEngine;
   * relația cu Rule Engine;
   * relația cu MissionEngine;
   * trasabilitatea prin Event Store și AuditLog.
============================================================
2. POZIȚIONAREA KPI-MODEL-001
Fluxul oficial este:
Business Object
↓
Event / Activity Data
↓
Event Store / Operational Database
↓
KPI Calculation Input
↓
KPI Calculation Engine
↓
Normalization
↓
Aggregation
↓
KPI Score
↓
KPI Store
↓
PerformanceEvaluationEngine
↓
OPI / Decision / Recommendation
↓
Dashboard / Mission / Workflow
KPI-urile sunt calculate de motoarele responsabile și persistate pentru analiză, dashboard-uri și raportare.
============================================================
3. REGISTRUL KPI OFICIAL
Modelul KPI utilizează următorii 11 indicatori majori:
   1. DIS — Daily Impact Score
   2. CRH — Customer Relationship Health
   3. PDI — Partner Development Index
   4. PIP — Partner Integration Progress
   5. OAS — Onboarding Activation Success
   6. ERI — Experience Reuse Index
   7. LRI — Leadership Readiness Index
   8. MEI — Mentoring Effectiveness Index
   9. TDI — Team Development Index
   10. AMS — Autonomy Maturity Score
   11. ERI — Experience Reuse Index
Indicatorul strategic suplimentar:
   12. OPI — Overall Performance Index
OPI nu reprezintă un KPI operațional independent, ci indicatorul strategic compozit care sintetizează KPI-urile majore ale Motorului 1.
NOTĂ DE RECONCILIERE:
Registrul trebuie menținut identic cu KPI-REG-001. În materialele istorice apar și PES — Presentation Effectiveness Score și ORE — Objection Resolution Effectiveness. Acestea apar ca KPI-uri componente într-o versiune anterioară a arhitecturii.
Înainte de înghețarea KPI-MODEL-001, registrul final trebuie reconciliat oficial cu KPI-REG-001.
============================================================
4. STANDARDUL GENERAL DE CALCUL
Fiecare KPI este calculat în patru etape:
ETAPA 1 — Colectarea inputurilor
Sunt colectate datele operaționale relevante din:
   * Business Objects;
   * Events;
   * Missions;
   * Conversations;
   * FollowUps;
   * Meetings;
   * Presentations;
   * Habits;
   * Assessments;
   * Experiences;
   * Knowledge;
   * Teams;
   * Partners;
   * Clients;
   * AuditLog;
   * KPI Store.
ETAPA 2 — Normalizarea
Valorile brute sunt transformate într-o scară comună.
Standardul recomandat pentru KPI-urile operaționale:
0 ≤ KPI ≤ 100
ETAPA 3 — Agregarea
Atunci când un KPI are mai multe componente:
KPI = Σ(wᵢ × componentᵢ)
unde:
   * componentᵢ = valoarea normalizată a componentei;
   * wᵢ = ponderea componentei;
   * Σwᵢ = 1.
ETAPA 4 — Persistența
Rezultatul este salvat în kpi_scores:
   * metric_id
   * metric_code
   * entity_type
   * entity_id
   * score_value
   * calculation_date
   * engine_source
   * metadata
Structura kpi_scores este deja definită în arhitectura Database.
============================================================
5. DIS — DAILY IMPACT SCORE
Cod: DIS
Denumire: Daily Impact Score
Scop:
Măsoară impactul operațional realizat într-o zi prin activitățile executate și rezultatele produse.
Obiect evaluat:
User
Inputuri:
   * Missions finalizate;
   * Missions validate;
   * FollowUps executate;
   * Conversations relevante;
   * activități relaționale;
   * activități de dezvoltare;
   * activități de continuitate;
   * priorități executate.
Surse:
   * missions
   * follow_ups
   * conversations
   * events
   * daily_reviews
Formula structurală:
DIS = Σ(wᵢ × ImpactComponentᵢ)
unde fiecare componentă este normalizată la 0–100.
Trigger:
   * MissionCompleted
   * MissionValidated
   * finalizarea Daily Review;
   * recalculare zilnică.
Frecvență:
DAILY
Motor responsabil:
PerformanceEvaluationEngine
Motoare furnizoare:
   * MissionEngine
   * FollowUpEngine
   * PriorityEngine
   * ContinuityEngine
============================================================
6. CRH — CUSTOMER RELATIONSHIP HEALTH
Cod: CRH
Denumire: Customer Relationship Health
Scop:
Măsoară sănătatea relației cu un Client sau Contact.
Inputuri:
   * frecvența interacțiunilor;
   * recența interacțiunilor;
   * continuitatea conversațiilor;
   * răspunsurile;
   * FollowUps;
   * evoluția relației;
   * semnale de inactivitate.
Surse:
   * contacts
   * clients
   * conversations
   * follow_ups
   * events
Model:
CRH = Σ(wᵢ × RelationshipComponentᵢ)
Trigger:
   * interacțiune nouă;
   * mesaj trimis;
   * mesaj primit;
   * FollowUp executat;
   * detectarea inactivității;
   * recalculare periodică.
Frecvență:
REAL-TIME / DAILY
Motor responsabil:
CustomerRelationshipEngine
CRH este explicit influențat de evenimentele de activare, calificare și conversie ale Contactului.
============================================================
7. PDI — PARTNER DEVELOPMENT INDEX
Cod: PDI
Denumire: Partner Development Index
Scop:
Măsoară gradul de dezvoltare al unui Partener.
Documentele existente definesc PDI prin:
   * continuitate;
   * progres în competențe;
   * consecvență;
   * implicare;
   * autonomie;
   * ritm de creștere.
Formula structurală:
PDI = Σ(wᵢ × DevelopmentComponentᵢ)
Componente:
   * Continuity Score
   * Competency Progress
   * Consistency Score
   * Engagement Score
   * Autonomy Score
   * Growth Rate Score
Surse:
   * partners
   * missions
   * habits
   * learning_records
   * assessments
   * events
   * kpi_scores
Trigger:
   * progres de competență;
   * Mission validată;
   * Assessment;
   * activare;
   * reactivare;
   * detectarea inactivității.
Frecvență:
DAILY + EVENT-DRIVEN
Motor responsabil:
PerformanceEvaluationEngine
Motoare furnizoare:
   * PartnerRelationshipEngine
   * ContinuityEngine
   * MissionEngine
   * HabitEngine
   * MentorGuidanceEngine
============================================================
8. PIP — PARTNER INTEGRATION PROGRESS
Cod: PIP
Denumire: Partner Integration Progress
Scop:
Măsoară progresul Partenerului în procesul de integrare și onboarding.
Inputuri:
   * activarea;
   * completarea onboardingului;
   * primele misiuni;
   * primele activități;
   * progresul în competențe;
   * interacțiunea cu mentorul;
   * continuitatea parcursului.
Surse:
   * partners
   * missions
   * learning_records
   * events
   * assessments
Formula:
PIP = Σ(wᵢ × IntegrationComponentᵢ)
Trigger:
   * PartnerActivated
   * onboarding step completed;
   * OnboardingCompleted;
   * OnboardingTimeout;
   * activitate nouă de onboarding.
Frecvență:
EVENT-DRIVEN
Motor responsabil:
PerformanceEvaluationEngine
PIP este explicit influențat de activarea și onboardingul Partenerului.
============================================================
9. OAS — ONBOARDING ACTIVATION SUCCESS
Cod: OAS
Denumire: Onboarding Activation Success
Scop:
Măsoară succesul procesului de activare și onboarding.
Inputuri:
   * timpul de activare;
   * completarea pașilor;
   * rata de finalizare;
   * blocajele;
   * claritatea procesului;
   * activarea primelor acțiuni.
Surse:
   * partners
   * missions
   * events
   * workflow_instances
   * assessments
Formula:
OAS = Σ(wᵢ × OnboardingComponentᵢ)
Trigger:
   * PartnerActivated
   * OnboardingCompleted
   * OnboardingTimeout
Frecvență:
EVENT-DRIVEN
Motor:
PerformanceEvaluationEngine
Datele despre durata activării, blocaje, claritatea procesului și rata de finalizare sunt deja definite ca inputuri pentru optimizarea onboardingului.
============================================================
10. ERI — EXPERIENCE REUSE INDEX
Cod: ERI
Denumire: Experience Reuse Index
Scop:
Măsoară gradul în care experiențele validate sunt reutilizate în activitatea operațională.
Inputuri:
   * Experiences capturate;
   * Experiences validate;
   * Knowledge generată;
   * utilizări ulterioare;
   * recomandări bazate pe experiențe;
   * reutilizarea în activități.
Surse:
   * experiences
   * knowledge
   * library_items
   * missions
   * events
Formula:
ERI = Σ(wᵢ × ExperienceReuseComponentᵢ)
Trigger:
   * Experience validată;
   * Knowledge creată;
   * reutilizare în workflow;
   * reutilizare într-o Mission;
   * publicare în Library.
Frecvență:
EVENT-DRIVEN + WEEKLY
Motor:
ExperienceEngine / PerformanceEvaluationEngine
============================================================
11. LRI — LEADERSHIP READINESS INDEX
Cod: LRI
Denumire: Leadership Readiness Index
Scop:
Măsoară gradul de pregătire al unui Partener pentru asumarea responsabilităților de leadership.
Inputuri:
   * PDI;
   * TDI;
   * MEI;
   * autonomie;
   * progres în competențe;
   * rezultate;
   * consistență;
   * capacitate de dezvoltare a altor persoane.
Surse:
   * partners
   * leaders
   * teams
   * assessments
   * kpi_scores
Formula:
LRI = Σ(wᵢ × LeadershipComponentᵢ)
Regulă structurală:
Trecerea către nivelul de Leader este condiționată de atingerea criteriilor definite de Rules & Decision Layer.
Trigger:
   * Assessment;
   * atingerea pragului de autonomie;
   * progres leadership;
   * dezvoltare echipă.
Frecvență:
WEEKLY / EVENT-DRIVEN
Motor:
LeadershipDevelopmentEngine
============================================================
12. MEI — MENTORING EFFECTIVENESS INDEX
Cod: MEI
Denumire: Mentoring Effectiveness Index
Scop:
Măsoară eficiența intervențiilor de mentorare.
Inputuri:
   * intervenții de mentorare;
   * progresul Partenerului;
   * misiuni rezultate din mentorare;
   * progresul în competențe;
   * feedback;
   * continuitatea intervenției.
Surse:
   * partners
   * missions
   * conversations
   * learning_records
   * assessments
   * events
Formula:
MEI = Σ(wᵢ × MentoringComponentᵢ)
Trigger:
   * intervenție de mentorare finalizată;
   * feedback;
   * progres de competență;
   * Assessment.
Frecvență:
EVENT-DRIVEN + WEEKLY
Motor:
MentorGuidanceEngine / PerformanceEvaluationEngine
MEI este deja asociat în arhitectură cu PDI, LRI și TDI.
============================================================
13. TDI — TEAM DEVELOPMENT INDEX
Cod: TDI
Denumire: Team Development Index
Scop:
Măsoară dezvoltarea colectivă a unei echipe.
Inputuri:
   * dezvoltarea Partenerilor;
   * activitatea echipei;
   * progresul în competențe;
   * mentorare;
   * leadership;
   * continuitate;
   * retenție;
   * rezultate colective.
Surse:
   * teams
   * partners
   * leaders
   * missions
   * assessments
   * kpi_scores
Formula:
TDI = Σ(wᵢ × TeamDevelopmentComponentᵢ)
Trigger:
   * schimbare relevantă în echipă;
   * progres Partener;
   * Assessment;
   * schimbare leadership;
   * recalculare periodică.
Frecvență:
WEEKLY
Motor:
TeamCoordinationEngine / PerformanceEvaluationEngine
============================================================
14. AMS — AUTONOMY MATURITY SCORE
Cod: AMS
Denumire: Autonomy Maturity Score
Scop:
Măsoară gradul de autonomie operațională al utilizatorului.
Definiția existentă:
AMS integrează KPI-urile Motorului 1 și capacitatea utilizatorului de a produce rezultate constante, de a dezvolta relații, Parteneri și lideri utilizând NicMar OS ca sistem de ghidare.
Inputuri:
   * OPI;
   * CRH;
   * PDI;
   * OAS;
   * PIP;
   * MEI;
   * TDI;
   * LRI;
   * ERI;
   * DIS;
   * rezultate operaționale;
   * consistență;
   * utilizarea sistemului.
Formula structurală:
AMS = Σ(wᵢ × AutonomyComponentᵢ)
Trigger:
   * Assessment;
   * atingerea unor praguri de performanță;
   * evaluare periodică;
   * schimbare semnificativă a OPI.
Frecvență:
WEEKLY / ASSESSMENT
Motor:
AutonomyEngine
AMS devine indicatorul care susține evaluarea maturității operaționale și activarea următorului ciclu de dezvoltare.
============================================================
15. OPI — OVERALL PERFORMANCE INDEX
Cod: OPI
Denumire: Overall Performance Index
Tip:
STRATEGIC COMPOSITE KPI
Scop:
OPI sintetizează evoluția globală a utilizatorului prin agregarea ponderată a KPI-urilor majore.
Definiția este explicită în arhitectura PerformanceEvaluationEngine.
Inputuri:
   * DIS
   * CRH
   * PDI
   * PIP
   * OAS
   * ERI
   * LRI
   * MEI
   * TDI
   * AMS
   * ceilalți KPI aprobați în registrul final.
Formula structurală:
OPI = Σ(wᵢ × KPIᵢ)
cu:
Σwᵢ = 1
și:
0 ≤ OPI ≤ 100
OPI este calculat numai din valori KPI normalizate.
Trigger:
   * actualizarea unui KPI component;
   * Assessment;
   * recalculare periodică;
   * eveniment strategic.
Frecvență:
EVENT-DRIVEN + DAILY
Motor:
PerformanceEvaluationEngine
Outputuri:
   * Dashboard de performanță;
   * recomandare strategică;
   * priorități;
   * actualizarea Missions;
   * suport pentru AutonomyEngine.
PerformanceEvaluationEngine este definit ca motorul care centralizează KPI-urile, analizează evoluția, detectează tendințe și generează recomandarea cu impact maxim.
============================================================
16. NORMALIZAREA KPI
Toate KPI-urile destinate agregării în OPI trebuie convertite într-o scară comună.
Standard:
0 — 100
Regulă:
   * 0 = nivel minim;
   * 100 = nivel maxim definit pentru indicator;
   * valorile intermediare sunt calculate determinist.
Pentru o valoare brută x într-un interval [min,max]:
NormalizedScore = ((x - min) / (max - min)) × 100
Pentru indicatorii în care valoarea mai mică reprezintă performanță mai bună:
NormalizedScore = ((max - x) / (max - min)) × 100
Valorile sunt apoi limitate la intervalul:
0 ≤ Score ≤ 100
============================================================
17. GESTIONAREA DATELOR LIPSĂ
Fiecare calcul trebuie să stabilească explicit dacă inputul este:
   * disponibil;
   * incomplet;
   * temporar indisponibil;
   * neaplicabil.
Regula standard:
Un input lipsă nu primește automat valoarea 0.
Sistemul marchează inputul ca:
MISSING
sau:
NOT_APPLICABLE
și aplică politica definită în KPI-ARCH-001 / KPI-REG-001.
============================================================
18. VERSIONAREA CALCULULUI
Fiecare rezultat KPI trebuie să păstreze:
   * metric_code
   * formula_version
   * calculation_version
   * calculation_date
   * engine_source
   * input_snapshot
   * score_value
   * metadata
Schimbarea formulei generează o versiune nouă.
Rezultatele istorice rămân asociate formulei cu care au fost calculate.
============================================================
19. EVENT-DRIVEN RECALCULATION
Evenimentele pot declanșa recalcularea KPI-urilor.
Exemple confirmate în Event Catalog:
FirstInteractionOccurred
→ CRH / DIS
QualificationCompleted
→ PDI / CRH
ConvertedToClient
→ CRH
ConvertedToPartner
→ PDI / PIP
NoInteractionTimeout
→ CRH / continuitate
PartnerActivated
→ PDI / PIP / OAS
OnboardingTimeout
→ PIP
PerformanceReviewTriggered
→ OPI / AMS / PDI
PartnerReactivated
→ PDI / DIS
Exemplele de mai sus sunt deja documentate în Event Catalogs.
============================================================
20. PERSISTENȚA KPI
Rezultatul final este persistat în:
kpi_scores
Structură:
metric_id UUID PRIMARY KEY
metric_code VARCHAR
entity_type VARCHAR
entity_id UUID
score_value NUMERIC
calculation_date TIMESTAMPTZ
engine_source VARCHAR
metadata JSONB
Această structură este deja stabilită în Database Architecture.
============================================================
21. AUDIT ȘI TRASABILITATE
Fiecare calcul KPI trebuie să poată răspunde la:
   * Cine a declanșat calculul?
   * Ce eveniment l-a declanșat?
   * Ce date au fost utilizate?
   * Ce versiune de formulă a fost utilizată?
   * Ce motor a efectuat calculul?
   * Ce rezultat a fost obținut?
   * Ce acțiuni au fost declanșate ulterior?
Lanțul complet:
Event → KPI Calculation → Score → AuditLog → Decision / Workflow / Mission
AuditLog păstrează actorul, obiectul, evenimentul, timestamp-ul și diferențele relevante.
============================================================
22. RELAȚIA CU PERFORMANCEEVALUATIONENGINE
PerformanceEvaluationEngine este orchestratorul central al stratului de performanță.
Flux:
KPI Scores
↓
PerformanceEvaluationEngine
↓
Analiză comparativă
↓
Analiză temporală
↓
Detectare tendințe
↓
OPI
↓
Recomandare
↓
PriorityEngine / MissionEngine / Dashboard
Outputurile documentate pentru PerformanceEvaluationEngine includ:
   * Dashboard de performanță;
   * OPI;
   * recomandări;
   * priorități;
   * actualizarea Missions.
============================================================
23. RELAȚIA CU RULE ENGINE
KPI-urile furnizează date pentru decizii.
Flux:
KPI
↓
Threshold
↓
Rule Engine
↓
Decision Outcome
↓
Workflow / Event / State Change / Mission
Exemplu:
PDI >= threshold
→ Rule Evaluation
→ Autonomy / Development Decision
→ Workflow sau Mission.
============================================================
24. RELAȚIA CU DASHBOARD
Dashboard-ul consumă KPI-urile prin DashboardEngine.
Afișarea standard include:
   * scor curent;
   * evoluție temporală;
   * trend;
   * nivel;
   * variație;
   * indicator de atenție;
   * recomandarea generată de PerformanceEvaluationEngine.
OPI reprezintă indicatorul strategic central al tabloului de performanță.
============================================================
25. REGULA DE CONSISTENȚĂ
Aceeași versiune de KPI trebuie să producă același rezultat pentru același set de inputuri.
Principiu:
Same Inputs + Same Formula Version = Same KPI Result
Orice modificare a:
   * formulei;
   * ponderilor;
   * pragurilor;
   * surselor;
   * regulilor de normalizare
generează o nouă versiune.
============================================================
26. FORMULE ȘI PONDERI — STADIUL SSOT
În sursele arhitecturale existente sunt definite:
   * scopurile KPI;
   * componentele principale;
   * inputurile;
   * motoarele responsabile;
   * evenimentele care îi influențează;
   * relația cu OPI;
   * modelul de agregare ponderată.
Sursele existente nu fixează încă numeric:
   * ponderile finale wᵢ;
   * pragurile numerice pentru fiecare KPI;
   * valorile min/max pentru fiecare componentă;
   * formula matematică detaliată pentru fiecare componentă.
Prin urmare, aceste valori rămân câmpuri de configurare care trebuie aprobate înainte de înghețarea finală a KPI-MODEL-001.
Această delimitare păstrează integritatea SSOT și evită introducerea unor valori arbitrare.
============================================================
27. CRITERII DE VALIDARE
KPI-MODEL-001 poate fi validat după confirmarea următoarelor elemente:
[ ] Registrul KPI este identic cu KPI-REG-001.
[ ] Fiecare KPI are o definiție unică.
[ ] Fiecare KPI are obiect evaluat.
[ ] Fiecare KPI are inputuri definite.
[ ] Fiecare KPI are surse de date.
[ ] Fiecare KPI are motor responsabil.
[ ] Fiecare KPI are trigger.
[ ] Fiecare KPI are frecvență de calcul.
[ ] Fiecare KPI are model de normalizare.
[ ] Fiecare KPI are model de agregare.
[ ] OPI are toate componentele aprobate.
[ ] Ponderile sunt versionate.
[ ] Pragurile sunt versionate.
[ ] Rezultatele sunt persistate în kpi_scores.
[ ] Fiecare calcul este auditabil.
[ ] Fiecare versiune de formulă este identificabilă.
[ ] Calculul este determinist.
[ ] KPI-urile pot alimenta Rules, Engines, Workflows, Missions și Dashboard.
============================================================
28. STATUS OFICIAL
Document:
NicMar OS — Core Architecture — Document 08.3
Identificator:
KPI-MODEL-001
Business Domain:
Core Architecture / KPI & Performance Architecture
Nivel:
Nivelul 6 — KPI & Performance Architecture
Versiune:
1.0
Status:
🟡 PROPUNERE PENTRU VALIDARE
Documente sursă:
KPI-ARCH-001
KPI-REG-001
Document 01 — Business Objects
DB-KPI-001
ENG-ARCH-001
RULE-ARCH-001
EVT-CAT-*
============================================================
29. URMĂTORUL DOCUMENT
După validarea KPI-MODEL-001, următorul document este:
KPI-CALC-001 — KPI Calculation & Aggregation Engine
Acesta va transforma modelele definite aici în mecanismul tehnic executabil:
KPI Definition
↓
Input Resolver
↓
Data Aggregator
↓
Normalizer
↓
Formula Evaluator
↓
Weighted Aggregator
↓
Score Validator
↓
KPI Store
↓
PerformanceEvaluationEngine
============================================================
END OF DOCUMENT
Important: am păstrat intenționat formulele la nivel structural acolo unde materialele tale nu conțin încă ponderile și pragurile aprobate. Asta păstrează KPI-MODEL-001 coerent cu SSOT-ul existent, în loc să introducem valori inventate. Sursele confirmă explicit că PerformanceEvaluationEngine centralizează cele 11 KPI-uri majore și că OPI este indicatorul strategic compozit.
Înainte de înghețare, singurul lucru pe care trebuie să-l rezolvăm este reconcilierea registrului KPI, deoarece documentele mai vechi folosesc și PES/ORE, iar registrul actual folosit în Master Architecture are altă componență.