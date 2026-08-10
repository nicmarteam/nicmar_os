# NicMar OS — Business Objects & Database Architecture (Nivel 0-2)

*Sursă: NicMar_OS___Core_Architecture_.txt*
*Notă: fișierul `NicMar_OS___Core_Architecture___1_.txt` a fost identificat ca fiind acest document + Master Architecture lipite la final (duplicat 100%) — arhivat, nu a fost inclus separat.*

---

﻿Da. Acum merită să fixăm arhitectura completă a ceea ce mai avem de construit, ca să avem harta proiectului până la NicMar OS funcțional.
Pornim exact de la punctul actual: cele 5 verticale fundamentale sunt închise.
NICMAR OS — ARHITECTURA COMPLETĂ DE CONSTRUIT
NIVELUL 0 — FUNDAȚIA DE BUSINESS
Document 01 — Business Objects
Status: 🔒 Închis
Definește cele 38 de Business Objects și domeniile lor.
________________


NIVELUL 1 — CORE ARCHITECTURE
Aici am construit cele 5 verticale fundamentale.
Pilon 1 — Contact 🔒
* SM-CONTACT-001
* EVT-CAT-CONTACT-001
Pilon 2 — Conversation 🔒
* SM-CONVERSATION-001
* EVT-CAT-CONVERSATION-001
Pilon 3 — Partner 🔒
* SM-PARTNER-001
* EVT-CAT-PARTNER-001
Pilon 4 — Client 🔒
* SM-CLIENT-001
* EVT-CAT-CLIENT-001
Pilon 5 — Mission 🔒
* SM-MISSION-001
* EVT-CAT-MISSION-001
Rezultat
Business Objects
       ↓
State Machines
       ↓
Event Catalogs
       ↓
5 verticale fundamentale
       ↓
CORE OPERAȚIONAL


________________


NIVELUL 2 — DATABASE ARCHITECTURE
Următorul nivel pe care îl construim.
Aici transformăm arhitectura logică în arhitectura datelor.
Document 04 — Database Model
Va conține:
04.1 — Database Architecture Standard
Regulile generale ale bazei de date.
04.2 — Business Object Data Model
Structura fiecărui Business Object:
ID
Status
Owner
CreatedAt
UpdatedAt
Version
Context
Relations


04.3 — Relationship Model
Definim exact:
Contact
  ↓
Conversation
  ↓
Client / Partner
  ↓
Mission


și toate relațiile secundare.
04.4 — State Persistence Model
Cum sunt stocate:
* State
* State History
* State Transitions
* Transition timestamps
04.5 — Event Store Model
Cum sunt stocate:
* Event
* Event Type
* Source Object
* Source Object ID
* Timestamp
* Payload
* Actor
* Correlation ID
04.6 — AuditLog Model
Trasabilitatea completă:
CINE
CE
CÂND
ASUPRA CĂRUIUI OBIECT
CE S-A SCHIMBAT
CARE A FOST EVENIMENTUL


04.7 — KPI / Score Model
Structura pentru:
* DIS
* CRH
* PDI
* PIP
* OPI
* ERI
* OAS
* celelalte KPI-uri deja definite.
04.8 — Database Integrity Rules
Reguli pentru:
* identitate
* unicitate
* referințe
* istoricul stărilor
* integritatea evenimentelor
* audit.
04.9 — Database Indexing Strategy
Definim ce trebuie indexat pentru performanță.
04.10 — Database Security Model
Acces, protecția datelor și separarea responsabilităților.
Rezultat:
DOCUMENT 04
DATABASE MODEL
        ↓
Structura persistentă oficială a NicMar OS


________________


NIVELUL 3 — EVENT & WORKFLOW ARCHITECTURE
Aici evenimentele deja definite încep să producă acțiuni sistemice.
Document 05 — Workflow Engine
Vom construi:
05.1 — Workflow Standard
Structura oficială a unui workflow.
05.2 — Workflow Lifecycle
Created
Triggered
Running
Waiting
Completed
Failed
Cancelled


05.3 — Workflow Registry
Catalogul tuturor workflow-urilor.
Exemplu:
WF-CONVERSATION-INIT-001
WF-FOLLOWUP-AUTO-001
WF-MEETING-CREATE-001
...


05.4 — Workflow Definitions
Pentru fiecare workflow:
Trigger
↓
Conditions
↓
Actions
↓
Engine
↓
Business Object
↓
Event
↓
Result


05.5 — Workflow Dependencies
Care workflow poate declanșa alt workflow.
05.6 — Workflow Error Handling
Cum sunt gestionate erorile și retry-urile.
________________


NIVELUL 4 — ENGINE ARCHITECTURE
Aici definim efectiv motoarele NicMar OS.
Document 06 — Engine Architecture
Vom avea catalogul motoarelor:
Relationship Engines
* RelationshipEngine
* CustomerRelationshipEngine
* PartnerRelationshipEngine
Execution Engines
* MissionEngine
* FollowUpEngine
* ContinuityEngine
Development Engines
* HabitEngine
* MentorGuidanceEngine
* LeadershipDevelopmentEngine
* TeamCoordinationEngine
Performance Engines
* PerformanceEvaluationEngine
* PriorityEngine
Experience Engines
* ExperienceEngine
* TestimonialEngine
System Engines
* NotificationEngine
* DashboardEngine
Pentru fiecare Engine vom defini:
Purpose
Inputs
Outputs
Events consumed
Events produced
Business Objects
Workflows
Rules
KPIs
Dependencies
Permissions


________________


NIVELUL 5 — RULES & DECISION ARCHITECTURE
Document 07 — Business Rules & Decision Engine
Aici mutăm regulile din documentele conceptuale într-un sistem formal.
Exemplu:
IF
Contact = Qualified
AND InterestScore ≥ threshold


THEN
trigger conversion workflow


Vom defini:
* Business Rules
* Decision Rules
* Conditions
* Thresholds
* Scoring Rules
* Priority Rules
* Qualification Rules
* Conversion Rules
* Reactivation Rules.
________________


NIVELUL 6 — KPI & PERFORMANCE ARCHITECTURE
Document 08 — KPI & Scoring Engine
Aici definim matematic indicatorii.
Pentru fiecare KPI:
Definition
Formula
Inputs
Data Source
Update Trigger
Calculation Frequency
Owner Engine
Storage
Dashboard Representation


Vom închide oficial:
* DIS
* CRH
* PDI
* PIP
* OPI
* ERI
* OAS
* LRI
* AMS
* MEI
* TDI
și indicatorii confirmați în Business Objects / Engines.
________________


NIVELUL 7 — IDENTITY, ROLES & SECURITY
Document 09 — Identity & Access Architecture
Definim:
User
Role
Permission
Access Scope
Ownership
Authorization
Audit


și rolurile operaționale ale NicMar OS.
________________


NIVELUL 8 — NOTIFICATION ARCHITECTURE
Document 10 — Notification Engine
Definim:
Event
 ↓
Notification Rule
 ↓
Channel
 ↓
Message
 ↓
Delivery
 ↓
Read / Action


Canalele pot fi definite ulterior în funcție de integrațiile reale.
________________


NIVELUL 9 — API ARCHITECTURE
Document 11 — API & Service Architecture
Aici facem legătura dintre nucleul OS și aplicație.
Vom defini:
UI
 ↓
API
 ↓
Services
 ↓
Engines
 ↓
Workflows
 ↓
Database


Pentru fiecare API:
   * endpoint
   * input
   * output
   * authentication
   * authorization
   * Business Object
   * Event
   * Engine
   * error model.
________________


NIVELUL 10 — AI / AGENT ARCHITECTURE
Aici intră partea de agenți NicMar OS despre care am discutat.
Document 12 — AI & Agent Architecture
Vom defini:
Agent Registry
Exemple:
   * Contact Agent
   * Conversation Agent
   * FollowUp Agent
   * Qualification Agent
   * Client Agent
   * Partner Agent
   * Mission Agent
   * Content Agent
   * Ads Agent
   * Performance Agent
   * Audit Agent
Pentru fiecare:
Purpose
Trigger
Input
Knowledge
Tools
Decision Rules
Actions
Output
Human Approval
Audit


Aici începe efectiv arhitectura NicMar OS AI-native.
________________


NIVELUL 11 — APPLICATION ARCHITECTURE
Document 13 — Application Architecture
Definim structura aplicației:
Dashboard
Contacts
Conversations
Clients
Partners
Missions
FollowUps
Meetings
Presentations
Experiences
KPIs
Reports
Settings


și legătura fiecărei zone cu API-ul și motoarele.
________________


NIVELUL 12 — UI / UX ARCHITECTURE
Document 14 — UI Component System
Definim componentele reutilizabile:
Cards
Tables
Forms
Timeline
State indicators
Event timeline
KPI cards
Mission cards
Contact profile
Conversation view
Partner profile
Client profile
Dashboard widgets


________________


NIVELUL 13 — INTEGRATION ARCHITECTURE
Document 15 — Integration Architecture
Aici intră conexiunile externe:
Facebook
WhatsApp
Email
Calendar
Zoom
Forms
Landing Page
Analytics


fiecare printr-un model controlat de integrare.
________________


NIVELUL 14 — OBSERVABILITY & AUDIT
Document 16 — Observability Architecture
Definim:
   * System Logs
   * Event Logs
   * AuditLog
   * Engine Logs
   * Workflow Logs
   * Error Logs
   * Performance Metrics
   * Health Monitoring.
________________


NIVELUL 15 — TESTING ARCHITECTURE
Document 17 — Testing & Validation
Definim testarea:
Business Object tests
State Machine tests
Event tests
Workflow tests
Engine tests
API tests
Integration tests
Agent tests
End-to-end tests


________________


NIVELUL 16 — DEPLOYMENT & INFRASTRUCTURE
Document 18 — Infrastructure Architecture
Definim:
Development
Testing
Production
Database
Storage
Backup
Security
Monitoring
Deployment
Versioning


________________


NIVELUL 17 — IMPLEMENTATION ROADMAP
Document 19 — NicMar OS Implementation Plan
Aici transformăm arhitectura în execuție.
Ordinea devine:
ARCHITECTURE
      ↓
DATABASE
      ↓
EVENTS
      ↓
WORKFLOWS
      ↓
ENGINES
      ↓
RULES
      ↓
KPI
      ↓
SECURITY
      ↓
API
      ↓
AI / AGENTS
      ↓
APPLICATION
      ↓
UI / UX
      ↓
INTEGRATIONS
      ↓
TESTING
      ↓
DEPLOYMENT
      ↓
NICMAR OS


________________


NIVELUL 18 — OPERATING SYSTEM
Ultimul nivel este sistemul funcțional propriu-zis.
Atunci avem:
                NICMAR OS
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
   RELATIONSHIP   EXECUTION     INTELLIGENCE
        │            │            │
 Contact          Mission       AI Agents
 Conversation     FollowUp      Decision
 Partner          Habit         Scoring
 Client           Meeting       Prediction
        │            │            │
        └────────────┼────────────┘
                     ↓
              WORKFLOW ENGINE
                     ↓
                ENGINE LAYER
                     ↓
                 EVENT BUS
                     ↓
                DATABASE
                     ↓
              AUDIT / KPI / LOGS


Ordinea oficială de acum
Aș fixa această secvență ca Architecture Master Roadmap:
Etapă
	Document
	Obiectiv
	✅ 0
	Business Objects
	Ce există în OS
	✅ 1
	5 Verticale
	Cum evoluează obiectele
	🔜 2
	Document 04
	Database Model
	🔜 3
	Document 05
	Workflow Engine
	🔜 4
	Document 06
	Engine Architecture
	🔜 5
	Document 07
	Rules & Decision Engine
	🔜 6
	Document 08
	KPI & Scoring
	🔜 7
	Document 09
	Identity & Security
	🔜 8
	Document 10
	Notification
	🔜 9
	Document 11
	API & Services
	🔜 10
	Document 12
	AI & Agents
	🔜 11
	Document 13
	Application Architecture
	🔜 12
	Document 14
	UI/UX
	🔜 13
	Document 15
	Integrations
	🔜 14
	Document 16
	Observability
	🔜 15
	Document 17
	Testing
	🔜 16
	Document 18
	Infrastructure
	🔜 17
	Document 19
	Implementation
	🎯
	—
	NicMar OS funcțional
	Asta este harta completă.




Da. Îl refac complet, păstrând ceea ce avem deja stabilit și corectând arhitectura astfel încât Documentul 04.1 să fie documentul master pentru Database Architecture, iar documentele 04.x ulterioare să poată fi derivate curat din el.
Îți dau direct varianta gata de copiat.
NicMar OS – Core Architecture – Document 04.1
Database Architecture Standard
Identificator: DB-ARCH-001
Business Domain: Core Architecture
Nivel: Nivelul 2 – Database Architecture
Versiune: 1.0
Status: 🟡 Propunere pentru validare
Metodologie: Vertical Slicing & Event-Driven Persistence
SSOT: Documentul 04.1 – Database Architecture Standard
Documente sursă:
   * Documentul 01 – Business Objects
   * SM-CONTACT-001
   * EVT-CAT-CONTACT-001
   * SM-CONVERSATION-001
   * EVT-CAT-CONVERSATION-001
   * SM-PARTNER-001
   * EVT-CAT-PARTNER-001
   * SM-CLIENT-001
   * EVT-CAT-CLIENT-001
   * SM-MISSION-001
   * EVT-CAT-MISSION-001
Documente derivate:
   * DB-BO-001 – Business Object Data Model
   * DB-REL-001 – Relationship Model
   * DB-STATE-001 – State Persistence Model
   * DB-EVENT-001 – Event Store Model
   * DB-AUDIT-001 – AuditLog Model
   * DB-KPI-001 – KPI & Score Model
   * DB-INT-001 – Database Integrity & Indexing
   * DB-SEC-001 – Database Security Model
________________


1. Scopul Documentului
Acest document definește standardul arhitectural oficial pentru persistența datelor în NicMar OS.
Database Architecture asigură:
   * persistența Business Objects;
   * păstrarea stării curente a entităților;
   * păstrarea istoricului tranzițiilor;
   * stocarea evenimentelor Business și System;
   * trasabilitatea completă prin AuditLog;
   * păstrarea relațiilor dintre Business Objects;
   * stocarea indicatorilor KPI și a rezultatelor de performanță;
   * integritatea datelor;
   * controlul accesului la date;
   * suportul pentru motoarele și workflow-urile NicMar OS.
Database Architecture reprezintă stratul persistent pe care se bazează toate nivelurile operaționale ulterioare.
________________


2. Principiul Arhitectural General
NicMar OS utilizează o arhitectură persistentă hibridă.
Modelul combină:
Business Object State
        +
State History
        +
Event Store
        +
AuditLog
        +
KPI / Score Persistence


Fiecare componentă are o responsabilitate distinctă.
Business Object State
Păstrează starea curentă a entității pentru acces operațional rapid.
State History
Păstrează istoricul tranzițiilor dintre stările Business Object-ului.
Event Store
Păstrează evenimentele generate de sistem și constituie istoricul cronologic al fluxurilor event-driven.
AuditLog
Păstrează trasabilitatea acțiunilor și modificărilor relevante.
KPI / Score Persistence
Păstrează rezultatele indicatorilor calculați de motoarele de performanță.
________________


3. Motorul de Bază de Date
Motorul recomandat pentru Database Architecture este:
PostgreSQL
PostgreSQL este utilizat ca sistem principal de persistență pentru:
   * date relaționale;
   * Business Objects;
   * relații;
   * stări;
   * istoricul stărilor;
   * Event Store;
   * AuditLog;
   * KPI și Score;
   * date flexibile JSONB.
Suportul JSONB este utilizat pentru payload-uri de evenimente, metadate și atribute flexibile unde modelarea relațională strictă nu reprezintă forma optimă de persistență.
________________


4. Principii Fundamentale de Persistență
4.1 Single Source of Truth
Fiecare Business Object are o reprezentare canonică unică.
Exemple:
Contact      → contacts
Conversation → conversations
Partner      → partners
Client       → clients
Mission      → missions


Starea operațională curentă este păstrată în tabelul Business Object-ului.
________________


4.2 Identitate Persistentă
Fiecare Business Object primește un identificator unic de tip UUID.
Identitatea obiectului este păstrată pe întregul său ciclu de viață.
________________


4.3 Separarea Stării Curente de Istoric
Sistemul separă:
CURRENT STATE
     ↓
Business Object Table


HISTORY
     ↓
State History
     ↓
Event Store
     ↓
AuditLog


Această separare permite acces rapid la starea curentă și trasabilitate completă asupra evoluției obiectului.
________________


4.4 Imuabilitatea Istoricului
Event Store și AuditLog sunt structuri append-only.
Evenimentele și înregistrările de audit sunt păstrate ca istoric permanent.
Corectarea unei informații istorice se realizează printr-o nouă înregistrare care explică schimbarea.
________________


4.5 Integritate Referențială
Relațiile canonice dintre Business Objects sunt implementate prin:
   * Primary Keys;
   * Foreign Keys;
   * Junction Tables;
   * Unique Constraints;
   * Check Constraints.
JSONB este utilizat pentru flexibilitate și metadate, iar relațiile canonice rămân modelate relațional.
________________


5. Standard Universal pentru Business Objects
Fiecare Business Object utilizează un set standard de câmpuri comune.
Câmpuri obligatorii
id
status
owner_id
created_at
updated_at
version


Câmpuri de identificare contextuală
object_type


Date flexibile
context_data JSONB


Metadate operaționale
relations_meta JSONB


relations_meta este utilizat pentru metadate și optimizări operaționale.
Relațiile canonice dintre obiecte sunt păstrate prin structuri relaționale dedicate.
________________


6. Standardul Câmpurilor Comune
Câmp
	Tip
	Responsabilitate
	id
	UUID
	Identitatea unică
	object_type
	VARCHAR
	Tipul Business Object
	status
	VARCHAR / Enum
	Starea curentă
	owner_id
	UUID
	Utilizatorul / agentul responsabil
	created_at
	TIMESTAMPTZ
	Data creării
	updated_at
	TIMESTAMPTZ
	Ultima actualizare
	version
	INT
	Controlul concurenței
	context_data
	JSONB
	Date flexibile
	relations_meta
	JSONB
	Metadate relaționale
	________________


7. Business Objects Fundamentale
Database Architecture trebuie să suporte cele cinci verticale fundamentale:
Contact
   ↓
Conversation
   ↓
Partner
   ↓
Client
   ↓
Mission


Tabelele canonice sunt:
contacts
conversations
partners
clients
missions


Fiecare tabel păstrează starea curentă a Business Object-ului conform State Machine-ului înghețat.
________________


8. Modelul Relațional
Relațiile dintre Business Objects sunt modelate explicit.
Structura conceptuală:
Contact
   │
   ├── Conversation
   │
   ├── Partner
   │
   └── Client
          │
          └── Mission


Relațiile suplimentare pot conecta:
Meeting
Presentation
FollowUp
Experience
Knowledge
Objection
Habit
Task
DailyPlan
Priority
Assessment
Score
KPI


Relațiile many-to-many sunt implementate prin Junction Tables.
Exemplu conceptual:
contact_conversations
partner_missions
client_missions
conversation_messages
client_experiences
partner_assessments


Structura exactă a acestor tabele este definită în DB-REL-001.
________________


9. Modelul Stării Curente
Fiecare Business Object păstrează starea curentă în câmpul:
status


Exemplu:
contacts.status
partners.status
clients.status
missions.status


Valorile permise sunt derivate exclusiv din State Machine-ul aferent.
Exemplu:
Partner
Activated
Onboarding
Active
Developing
Autonomous
Leader
Mentor
Archived


State Machine-ul reprezintă SSOT pentru valorile de stare.
________________


10. Modelul State History
Pentru fiecare tranziție de stare se păstrează o înregistrare în state_history.
Structură
state_history


Câmpuri:
id UUID PRIMARY KEY
object_id UUID
object_type VARCHAR
previous_state VARCHAR
new_state VARCHAR
transition_event VARCHAR
actor_id UUID
created_at TIMESTAMPTZ
metadata JSONB


Exemplu
object_type:
Partner


previous_state:
Onboarding


new_state:
Active


transition_event:
OnboardingCompleted


State History permite reconstruirea cronologică a evoluției unei entități.
Structura completă este definită în:
DB-STATE-001
________________


11. Modelul Event Store
Event Store păstrează toate evenimentele oficiale generate în sistem.
Evenimentele sunt derivate din Event Catalog-urile înghețate.
Structura:
event_store


Câmpuri:
event_id UUID PRIMARY KEY
event_type VARCHAR
source_object VARCHAR
source_object_id UUID
timestamp TIMESTAMPTZ
payload JSONB
actor_id UUID
actor_type VARCHAR
correlation_id UUID
causation_id UUID
metadata JSONB


Exemple de evenimente
ContactCreated
MessageSent
PartnerActivated
ClientActivated
MissionGenerated
MissionValidated


Event Store constituie baza arhitecturii Event-Driven.
Structura completă este definită în:
DB-EVENT-001
________________


12. Correlation și Causation
Pentru urmărirea fluxurilor complexe sunt utilizate:
correlation_id
Identifică întregul flux operațional.
causation_id
Identifică evenimentul care a determinat evenimentul curent.
Exemplu:
ContactCreated
      ↓
ConversationCreated
      ↓
MessageReceived
      ↓
InterestExpressed
      ↓
MissionGenerated


Prin correlation_id și causation_id, întregul lanț poate fi urmărit.
________________


13. Modelul AuditLog
AuditLog păstrează trasabilitatea operațională.
Structura conceptuală:
audit_log


Câmpuri:
audit_id UUID PRIMARY KEY
actor_id UUID
actor_type VARCHAR
action_type VARCHAR
object_type VARCHAR
object_id UUID
event_id UUID
timestamp TIMESTAMPTZ
diff_payload JSONB
metadata JSONB


AuditLog răspunde permanent la:
CINE?
CE?
CÂND?
ASUPRA CĂRUI OBIECT?
CE S-A SCHIMBAT?
CE EVENIMENT A DETERMINAT SCHIMBAREA?


Structura completă este definită în:
DB-AUDIT-001
________________


14. Modelul KPI și Score
NicMar OS păstrează rezultatele KPI într-o structură dedicată.
kpi_scores


Câmpuri:
metric_id UUID PRIMARY KEY
metric_code VARCHAR
entity_type VARCHAR
entity_id UUID
score_value NUMERIC
calculation_date TIMESTAMPTZ
engine_source VARCHAR
metadata JSONB


Exemple de KPI:
DIS
CRH
OPI
ERI
OAS
PDI
PIP
MEI
TDI
LRI
AMS


KPI-urile sunt calculate de motoarele responsabile și persistate pentru analiză, dashboard-uri și raportare.
Structura completă este definită în:
DB-KPI-001
________________


15. Versionarea Datelor
Business Objects utilizează:
version INT


pentru controlul concurenței optimiste.
La modificarea unei entități:
version = version + 1


Sistemul poate detecta modificările concurente înainte de confirmarea actualizării.
________________


16. Timestamps
Toate datele operaționale utilizează:
TIMESTAMPTZ


Câmpurile standard sunt:
created_at
updated_at


Event Store, State History și AuditLog utilizează timestamp-uri cu timezone pentru trasabilitate globală.
________________


17. Indexare
Strategia de indexare urmărește acces rapid la:
Stare
object_type + status


Ownership
owner_id


Evenimente
event_type
source_object
source_object_id
timestamp
correlation_id


Audit
object_type
object_id
actor_id
timestamp


KPI
metric_code
entity_type
entity_id
calculation_date


JSONB
Indexurile GIN sunt utilizate pentru câmpurile JSONB unde pattern-urile reale de interogare justifică această strategie.
Structura completă este definită în:
DB-INT-001
________________


18. Integritate și Constrângeri
Database Architecture utilizează:
Primary Keys
Pentru identificarea unică a fiecărui record.
Foreign Keys
Pentru menținerea integrității relațiilor.
Unique Constraints
Pentru identificatori de business care trebuie să fie unici.
Check Constraints
Pentru valori care trebuie să respecte reguli definite.
NOT NULL Constraints
Pentru datele obligatorii.
Referential Integrity
Relațiile canonice sunt protejate prin reguli explicite de integritate.
Istoricul Event Store și AuditLog este protejat prin politica append-only.
________________


19. Strategia de Ștergere
Business Objects cu relevanță operațională și istorică sunt gestionate prin ciclul lor de viață.
Pentru datele istorice:
Archived


reprezintă starea operațională de închidere.
Event Store și AuditLog păstrează istoricul conform politicilor de retenție și guvernanță stabilite la nivelul Security & Compliance Architecture.
________________


20. Securitatea Bazei de Date
Database Architecture utilizează:
RBAC
Controlul accesului bazat pe roluri.
Row-Level Security
RLS pentru izolarea datelor în funcție de utilizator, echipă și context.
Encryption at Rest
Datele stocate sunt protejate prin mecanisme de criptare la nivel de infrastructură.
Encryption in Transit
Conexiunile dintre aplicație, motoare și baza de date utilizează canale securizate TLS.
Least Privilege
Fiecare componentă primește nivelul minim de acces necesar responsabilității sale.
Structura completă este definită în:
DB-SEC-001
________________


21. Separarea Responsabilităților
Database Architecture separă clar:
Business Object
      ↓
Current State


State Machine
      ↓
Allowed State


Event Catalog
      ↓
Official Events


Database
      ↓
Persistent State + History


Engine
      ↓
Business Logic


Workflow
      ↓
Process Orchestration


API
      ↓
External/Application Access


Baza de date păstrează datele și istoricul.
Motoarele execută logica de business.
Workflow-urile orchestrează procesele.
API-ul expune operațiunile către aplicație și integrări.
________________


22. Event-Driven Persistence Flow
Fluxul standard este:
User / Engine
      │
      ▼
Business Action
      │
      ▼
Business Event
      │
      ▼
State Transition
      │
      ├──────────────► Current State
      │
      ├──────────────► State History
      │
      ├──────────────► Event Store
      │
      └──────────────► AuditLog


Motoarele și workflow-urile reacționează la eveniment conform Event Catalog-ului.
________________


23. Exemplu de Flux Complet
Exemplu pentru Mission:
MissionGenerated
      ↓
missions.status = Generated
      ↓
state_history
      ↓
event_store
      ↓
audit_log
      ↓
PriorityEngine
      ↓
MissionScheduled
      ↓
DailyPlan


La final:
MissionCompleted
      ↓
MissionValidated
      ↓
missions.status = Validated
      ↓
KPI / Score
      ↓
DIS
      ↓
PerformanceEvaluationEngine
      ↓
Dashboard


________________


24. Cerințe pentru Nivelurile Următoare
Database Architecture trebuie să ofere infrastructura persistentă necesară pentru:
   * Workflow Layer;
   * Engine Layer;
   * Rules Layer;
   * KPI Layer;
   * API Layer;
   * Application Layer;
   * AI / Agent Layer;
   * Integration Layer;
   * Dashboard Layer;
   * Notification Layer;
   * Audit & Observability Layer.
Fiecare dintre aceste niveluri trebuie să utilizeze structurile persistente definite în Database Architecture.
________________


25. Structura Documentelor Derivate
Database Architecture este organizată astfel:
DB-ARCH-001
Database Architecture Standard
        │
        ├── DB-BO-001
        │   Business Object Data Model
        │
        ├── DB-REL-001
        │   Relationship Model
        │
        ├── DB-STATE-001
        │   State Persistence Model
        │
        ├── DB-EVENT-001
        │   Event Store Model
        │
        ├── DB-AUDIT-001
        │   AuditLog Model
        │
        ├── DB-KPI-001
        │   KPI & Score Model
        │
        ├── DB-INT-001
        │   Integrity & Indexing
        │
        └── DB-SEC-001
            Database Security Model


________________


26. Condiția de Închidere a Database Architecture
Nivelul Database Architecture este considerat complet închis atunci când sunt validate și înghețate:
DB-ARCH-001
      ↓
DB-BO-001
      ↓
DB-REL-001
      ↓
DB-STATE-001
      ↓
DB-EVENT-001
      ↓
DB-AUDIT-001
      ↓
DB-KPI-001
      ↓
DB-INT-001
      ↓
DB-SEC-001
      ↓
🔒 DATABASE ARCHITECTURE
100% ÎNCHISĂ


________________


27. Poziția în Arhitectura Generală NicMar OS
Structura actuală este:
LEVEL 1
CORE BUSINESS OBJECTS
        ↓
5 VERTICALE ÎNCHISE
        ↓
LEVEL 2
DATABASE ARCHITECTURE
        ↓
DB-ARCH-001
        ↓
Documentele DB-BO / DB-REL / DB-STATE /
DB-EVENT / DB-AUDIT / DB-KPI / DB-INT / DB-SEC
        ↓
LEVEL 3
WORKFLOW & ENGINE ARCHITECTURE
        ↓
LEVEL 4
RULES & KPI ARCHITECTURE
        ↓
LEVEL 5
API & SERVICE ARCHITECTURE
        ↓
LEVEL 6
APPLICATION ARCHITECTURE
        ↓
LEVEL 7
AI & AGENT ARCHITECTURE
        ↓
LEVEL 8
INTEGRATION ARCHITECTURE
        ↓
LEVEL 9
OBSERVABILITY / SECURITY / COMPLIANCE
        ↓
LEVEL 10
INFRASTRUCTURE / DEPLOYMENT


________________


28. Status Oficial
Document: NicMar OS – Core Architecture – Document 04.1
Identificator: DB-ARCH-001
Business Domain: Core Architecture
Nivel: Level 2 – Database Architecture
Versiune: 1.0
Status: 🟡 Propunere pentru validare
Metodologie: Vertical Slicing & Event-Driven Persistence
SSOT
DB-ARCH-001
Dependențe
   * Documentul 01 – Business Objects
   * State Machine-urile celor 5 piloni
   * Event Catalog-urile celor 5 piloni
Documente derivate
   * DB-BO-001
   * DB-REL-001
   * DB-STATE-001
   * DB-EVENT-001
   * DB-AUDIT-001
   * DB-KPI-001
   * DB-INT-001
   * DB-SEC-001
Condiția de validare
Documentul devine SSOT activ pentru Database Architecture după validarea finală.
Condiția de închidere
Validarea și înghețarea documentului DB-ARCH-001, urmate de construcția și validarea documentelor derivate DB-BO-001 până la DB-SEC-001.
________________


🔒 PRINCIPIUL ARHITECTURAL CENTRAL
BUSINESS OBJECTS
       ↓
STATE MACHINES
       ↓
EVENT CATALOGS
       ↓
DATABASE ARCHITECTURE
       ↓
WORKFLOWS + ENGINES
       ↓
RULES + KPI
       ↓
API + SERVICES
       ↓
APPLICATION
       ↓
AI + AGENTS
       ↓
INTEGRATIONS
       ↓
OBSERVABILITY + SECURITY
       ↓
INFRASTRUCTURE




NicMar OS – Core Architecture – Document 04.1 Database Architecture Standard Identificator: DB-ARCH-001 Business Domain: Core Architecture Nivel: Nivelul 2 – Database Architecture Versiune: 1.0 Status: ✅ Validat și Înghețat Metodologie: Vertical Slicing & Event-Driven Persistence SSOT: Documentul 04.1 – Database Architecture Standard
Documentul master DB-ARCH-001 a fost validat oficial și este acum înghețat ca Single Source of Truth (SSOT) pentru stratul de persistență al NicMar OS
Da. Am verificat întâi Documentul 01 din sursa oficială și am folosit exact catalogul celor 38 de Business Objects, cele 6 domenii și relațiile deja definite. Documentul 01 este SSOT pentru obiecte și terminologie.
Pentru DB-BO-001, păstrăm separarea clară: Documentul 01 spune ce este fiecare obiect, iar DB-BO-001 stabilește cum este reprezentat persistent. Standardul DB-ARCH-001 furnizat de tine stabilește structura universală: UUID, status, owner, timestamps, version, context_data și relations_meta.
Mai jos este documentul complet, gata de copiat.
NicMar OS – Core Architecture – Document 04.2
Business Object Data Model
Identificator: DB-BO-001
Business Domain: Core Architecture
Nivel: Nivelul 2 – Database Architecture
Versiune: 1.0
Status: 🟡 Propunere pentru validare
Metodologie: Vertical Slicing & Event-Driven Persistence
SSOT pentru: Structura persistentă a celor 38 Business Objects
Derivat din:
   * Documentul 01 – Business Objects
   * DB-ARCH-001 – Database Architecture Standard
   * State Machine-urile validate
   * Event Catalog-urile validate
________________


1. Scopul Documentului
DB-BO-001 definește modelul persistent canonic pentru cele 38 de Business Objects din NicMar OS.
Documentul stabilește pentru fiecare Business Object:
   * tabelul canonic;
   * cheia primară;
   * identificatorul Business Object;
   * câmpurile obligatorii;
   * tipurile de date;
   * ownership-ul;
   * statusul;
   * versioning-ul;
   * timestamps;
   * relațiile fundamentale;
   * Foreign Keys;
   * indexurile principale;
   * constrângerile de integritate;
   * legătura cu Event Store;
   * legătura cu AuditLog;
   * legătura cu KPI și Score.
Modelul păstrează principiul fundamental al arhitecturii:
Business Object
       ↓
State Machine
       ↓
Event
       ↓
Workflow
       ↓
Persistence
       ↓
KPI / Score
       ↓
AuditLog


________________


2. Principii de Modelare
2.1 SSOT
Fiecare Business Object are o reprezentare persistentă canonică.
Un Business Object are:
   * o singură identitate;
   * un singur tabel canonic;
   * un singur responsabil principal;
   * un singur model persistent oficial.
________________


2.2 Identitate
Toate Business Objects utilizează:
id UUID PRIMARY KEY


UUID reprezintă identificatorul tehnic unic al entității.
________________


2.3 State
Business Objects care au State Machine utilizează:
status VARCHAR


Valoarea status este derivată exclusiv din State Machine-ul obiectului.
________________


2.4 Ownership
Obiectele operaționale utilizează:
owner_id UUID


owner_id identifică utilizatorul responsabil de obiect.
________________


2.5 Versioning
Toate obiectele persistente utilizează:
version INTEGER


Câmpul este utilizat pentru controlul concurenței și actualizărilor succesive.
________________


2.6 Timestamps
Structura standard:
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ


________________


2.7 Context flexibil
Datele specifice domeniului care necesită flexibilitate sunt păstrate în:
context_data JSONB


________________


2.8 Relații
Metadatele operaționale rapide privind relațiile pot fi păstrate în:
relations_meta JSONB


Relațiile structurale și integritatea referențială sunt implementate prin Foreign Keys și tabele de relație dedicate.
________________


3. Catalogul Oficial al celor 38 Business Objects
Catalogul oficial conține 38 Business Objects organizate în 6 domenii funcționale.
________________


I. CORE DOMAIN
1. User
Tabel canonic: users
Responsabilitate: Gestionarea contului utilizatorului, autentificării, rolurilor și datelor de bază.
Câmpuri
id UUID PK
username VARCHAR
email VARCHAR
password_hash VARCHAR
status VARCHAR
owner_id UUID NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


Constrângeri
UNIQUE(email)
UNIQUE(username)


Indexuri
idx_users_email
idx_users_status


________________


2. Profile
Tabel canonic: profiles
Responsabilitate: Identitatea operațională NicMar a utilizatorului.
Câmpuri
id UUID PK
user_id UUID FK → users.id
display_name VARCHAR
first_name VARCHAR
last_name VARCHAR
photo_url VARCHAR
status VARCHAR
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


Constrângeri
UNIQUE(user_id)


________________


3. Identity
Tabel canonic: identities
Responsabilitate: Elementele asociate identității și alinierii valorice.
Câmpuri
id UUID PK
user_id UUID FK → users.id
status VARCHAR
identity_type VARCHAR
identity_data JSONB
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


4. Partner
Tabel canonic: partners
State Machine: SM-PARTNER-001
Responsabilitate: Ciclul de viață și dezvoltarea partenerului.
Câmpuri
id UUID PK
contact_id UUID FK → contacts.id
owner_id UUID FK → users.id
status VARCHAR
activated_at TIMESTAMPTZ
current_level VARCHAR
mentor_id UUID FK → users.id NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


Indexuri
idx_partners_owner
idx_partners_contact
idx_partners_status


________________


5. Client
Tabel canonic: clients
State Machine: SM-CLIENT-001
Responsabilitate: Relația comercială și experiența Clientului.
Câmpuri
id UUID PK
contact_id UUID FK → contacts.id
owner_id UUID FK → users.id
status VARCHAR
first_purchase_at TIMESTAMPTZ NULL
last_purchase_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


Indexuri
idx_clients_owner
idx_clients_contact
idx_clients_status
idx_clients_last_purchase


________________


6. Team
Tabel canonic: teams
Responsabilitate: Structura organizatorică și indicatorii colectivi.
Câmpuri
id UUID PK
owner_id UUID FK → users.id
name VARCHAR
status VARCHAR
leader_id UUID FK → users.id NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


7. Leader
Tabel canonic: leaders
Responsabilitate: Parcursul de leadership și dezvoltarea liderilor.
Câmpuri
id UUID PK
partner_id UUID FK → partners.id
owner_id UUID FK → users.id
status VARCHAR
leadership_level VARCHAR
activated_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


II. RELATIONSHIP DOMAIN
Documentul 01 definește Contact ca entitatea primară a domeniului relațional, iar Conversation, Meeting, Presentation, FollowUp și Objection ca obiecte relaționale specializate.
8. Contact
Tabel canonic: contacts
State Machine: SM-CONTACT-001
Câmpuri
id UUID PK
owner_id UUID FK → users.id
first_name VARCHAR
last_name VARCHAR
email VARCHAR NULL
phone VARCHAR NULL
status VARCHAR
source VARCHAR NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


Constrângeri
UNIQUE(email)


Indexuri
idx_contacts_owner
idx_contacts_status
idx_contacts_email
idx_contacts_phone


________________


9. Conversation
Tabel canonic: conversations
State Machine: SM-CONVERSATION-001
Câmpuri
id UUID PK
contact_id UUID FK → contacts.id
owner_id UUID FK → users.id
status VARCHAR
channel VARCHAR
started_at TIMESTAMPTZ
last_interaction_at TIMESTAMPTZ
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


10. Meeting
Tabel canonic: meetings
Câmpuri
id UUID PK
contact_id UUID FK → contacts.id NULL
owner_id UUID FK → users.id
status VARCHAR
meeting_type VARCHAR
scheduled_at TIMESTAMPTZ
completed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


11. Presentation
Tabel canonic: presentations
Câmpuri
id UUID PK
meeting_id UUID FK → meetings.id
contact_id UUID FK → contacts.id NULL
owner_id UUID FK → users.id
status VARCHAR
presentation_type VARCHAR
scheduled_at TIMESTAMPTZ NULL
completed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


12. FollowUp
Tabel canonic: follow_ups
Câmpuri
id UUID PK
contact_id UUID FK → contacts.id NULL
conversation_id UUID FK → conversations.id NULL
client_id UUID FK → clients.id NULL
partner_id UUID FK → partners.id NULL
owner_id UUID FK → users.id
status VARCHAR
scheduled_at TIMESTAMPTZ
completed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


13. Objection
Tabel canonic: objections
Câmpuri
id UUID PK
contact_id UUID FK → contacts.id NULL
conversation_id UUID FK → conversations.id NULL
client_id UUID FK → clients.id NULL
partner_id UUID FK → partners.id NULL
owner_id UUID FK → users.id
status VARCHAR
objection_type VARCHAR
resolution_data JSONB
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


III. ACTIVITY DOMAIN
Documentul 01 definește Mission, Habit, Task, DailyPlan, DailyReview și Priority ca structura operațională a zilei.
14. Mission
Tabel canonic: missions
State Machine: SM-MISSION-001
Câmpuri
id UUID PK
owner_id UUID FK → users.id
contact_id UUID FK → contacts.id NULL
conversation_id UUID FK → conversations.id NULL
partner_id UUID FK → partners.id NULL
client_id UUID FK → clients.id NULL
meeting_id UUID FK → meetings.id NULL
presentation_id UUID FK → presentations.id NULL
follow_up_id UUID FK → follow_ups.id NULL
habit_id UUID FK → habits.id NULL
task_id UUID FK → tasks.id NULL
daily_plan_id UUID FK → daily_plans.id NULL
priority_id UUID FK → priorities.id NULL
status VARCHAR
title VARCHAR
description TEXT
scheduled_at TIMESTAMPTZ NULL
deadline_at TIMESTAMPTZ NULL
completed_at TIMESTAMPTZ NULL
validated_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


Indexuri
idx_missions_owner
idx_missions_status
idx_missions_scheduled_at
idx_missions_deadline
idx_missions_daily_plan


Mission reprezintă unitatea operațională centrală pentru execuția zilnică și este conectată la obiectele relaționale și operaționale deja definite în arhitectură.
________________


15. Habit
Tabel canonic: habits
id UUID PK
owner_id UUID FK → users.id
status VARCHAR
name VARCHAR
frequency VARCHAR
target_value NUMERIC NULL
current_streak INTEGER
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


16. Task
Tabel canonic: tasks
id UUID PK
owner_id UUID FK → users.id
status VARCHAR
title VARCHAR
description TEXT
due_at TIMESTAMPTZ NULL
completed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


17. DailyPlan
Tabel canonic: daily_plans
id UUID PK
owner_id UUID FK → users.id
plan_date DATE
status VARCHAR
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


Constrângere
UNIQUE(owner_id, plan_date)


________________


18. DailyReview
Tabel canonic: daily_reviews
id UUID PK
owner_id UUID FK → users.id
review_date DATE
status VARCHAR
completed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


19. Priority
Tabel canonic: priorities
id UUID PK
owner_id UUID FK → users.id
mission_id UUID FK → missions.id NULL
priority_level INTEGER
status VARCHAR
reason VARCHAR NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


IV. LEARNING DOMAIN
Documentul 01 definește Experience → Knowledge → Library ca flux de transformare a experienței în cunoaștere, iar LearningRecord păstrează parcursul educațional.
20. Experience
Tabel canonic: experiences
id UUID PK
owner_id UUID FK → users.id
status VARCHAR
source_type VARCHAR
source_object_id UUID NULL
title VARCHAR NULL
content TEXT
captured_at TIMESTAMPTZ
validated_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


21. Knowledge
Tabel canonic: knowledge
id UUID PK
owner_id UUID FK → users.id
experience_id UUID FK → experiences.id NULL
status VARCHAR
title VARCHAR
content TEXT
knowledge_type VARCHAR
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


22. Library
Tabel canonic: library_items
id UUID PK
owner_id UUID FK → users.id NULL
knowledge_id UUID FK → knowledge.id
status VARCHAR
title VARCHAR
category VARCHAR
published_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


23. LearningRecord
Tabel canonic: learning_records
id UUID PK
user_id UUID FK → users.id
status VARCHAR
learning_type VARCHAR
source_object_type VARCHAR NULL
source_object_id UUID NULL
started_at TIMESTAMPTZ NULL
completed_at TIMESTAMPTZ NULL
progress NUMERIC
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


V. PERFORMANCE DOMAIN
Documentul 01 definește KPI, Dashboard, DashboardState, Score și Assessment ca structura oficială a domeniului de performanță.
24. KPI
Tabel canonic: kpis
id UUID PK
metric_code VARCHAR
name VARCHAR
description TEXT
entity_type VARCHAR
status VARCHAR
calculation_rule_id UUID FK → rules.id NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


Exemple oficiale de metric codes
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


Lista KPI este derivată din catalogul oficial al Business Objects.
________________


25. Dashboard
Tabel canonic: dashboards
id UUID PK
owner_id UUID FK → users.id
status VARCHAR
dashboard_type VARCHAR
name VARCHAR
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


26. DashboardState
Tabel canonic: dashboard_states
id UUID PK
dashboard_id UUID FK → dashboards.id
status VARCHAR
state_data JSONB
calculated_at TIMESTAMPTZ
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


Constrângere
UNIQUE(dashboard_id)


Documentul 01 stabilește relația:
Dashboard (1) ↔ (1) DashboardState


________________


27. Score
Tabel canonic: scores
id UUID PK
kpi_id UUID FK → kpis.id
entity_type VARCHAR
entity_id UUID
score_value NUMERIC
calculated_at TIMESTAMPTZ
engine_source VARCHAR
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


Indexuri
idx_scores_kpi
idx_scores_entity
idx_scores_calculated_at


________________


28. Assessment
Tabel canonic: assessments
id UUID PK
owner_id UUID FK → users.id
entity_type VARCHAR
entity_id UUID
status VARCHAR
assessment_type VARCHAR
score_value NUMERIC NULL
started_at TIMESTAMPTZ
completed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


VI. SYSTEM DOMAIN
Documentul 01 definește obiectele de sistem și infrastructură de la Notification până la Attachment.
29. Notification
Tabel canonic: notifications
id UUID PK
owner_id UUID FK → users.id
status VARCHAR
notification_type VARCHAR
channel VARCHAR
recipient_id UUID
scheduled_at TIMESTAMPTZ NULL
sent_at TIMESTAMPTZ NULL
read_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


30. Event
Tabel canonic: events
Event reprezintă reprezentarea persistentă a evenimentelor arhitecturii Event-Driven.
id UUID PK
event_type VARCHAR
source_object VARCHAR
source_object_id UUID
target_object_type VARCHAR NULL
target_object_id UUID NULL
timestamp TIMESTAMPTZ
payload JSONB
actor_id UUID NULL
correlation_id UUID NULL
created_at TIMESTAMPTZ


Regula de persistență
events este append-only.
________________


31. Workflow
Tabel canonic: workflows
id UUID PK
workflow_code VARCHAR
name VARCHAR
status VARCHAR
version INTEGER
trigger_event_type VARCHAR NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
context_data JSONB
relations_meta JSONB


________________


32. Rule
Tabel canonic: rules
id UUID PK
rule_code VARCHAR
name VARCHAR
status VARCHAR
rule_type VARCHAR
condition_data JSONB
action_data JSONB
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


33. Automation
Tabel canonic: automations
id UUID PK
automation_code VARCHAR
name VARCHAR
status VARCHAR
trigger_event_type VARCHAR
workflow_id UUID FK → workflows.id NULL
rule_id UUID FK → rules.id NULL
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


34. Permission
Tabel canonic: permissions
id UUID PK
permission_code VARCHAR
name VARCHAR
resource VARCHAR
action VARCHAR
status VARCHAR
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


35. Role
Tabel canonic: roles
id UUID PK
role_code VARCHAR
name VARCHAR
status VARCHAR
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
context_data JSONB
relations_meta JSONB


Relație
Role este asociat cu Permission prin tabela:
role_permissions


________________


36. AuditLog
Tabel canonic: audit_logs
AuditLog păstrează istoricul complet al acțiunilor și schimbărilor.
id UUID PK
event_id UUID FK → events.id
actor_id UUID NULL
actor_type VARCHAR
object_type VARCHAR
object_id UUID
action VARCHAR
timestamp TIMESTAMPTZ
diff_payload JSONB
metadata JSONB


Regula de persistență
APPEND ONLY


________________


37. Attachment
Tabel canonic: attachments
id UUID PK
owner_id UUID FK → users.id
object_type VARCHAR
object_id UUID
file_name VARCHAR
file_type VARCHAR
mime_type VARCHAR
storage_key VARCHAR
file_size BIGINT
status VARCHAR
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
version INTEGER
context_data JSONB
relations_meta JSONB


________________


4. Relațiile Fundamentale
Modelul respectă relațiile oficiale definite în Documentul 01:
User
  │
  └── Profile


Contact
  │
  ├── Conversation
  │
  ├── Client
  │
  └── Partner


Conversation
  │
  └── Event


Experience
  │
  └── Knowledge
        │
        └── Library


Dashboard
  │
  └── DashboardState


Relația Contact → Client / Partner rămâne compatibilă cu regula oficială conform căreia un Contact poate deveni Client și/sau Partner.
________________


5. Model Universal de Ownership
Obiectele operaționale utilizează:
owner_id → users.id


Obiectele relaționale păstrează:
owner_id


și identificatorul entității relaționale principale:
contact_id
client_id
partner_id


conform contextului.
________________


6. Model Universal de Versioning
Toate Business Objects persistente utilizează:
version INTEGER NOT NULL DEFAULT 1


Actualizarea unui obiect crește valoarea version.
Modelul permite controlul concurenței:
UPDATE object
SET version = version + 1
WHERE id = :id
AND version = :expected_version;


________________


7. Relația cu State Machine
Pentru Business Objects cu State Machine:
Business Object
      │
      ├── status
      │
      ├── version
      │
      └── state_history


State-ul curent este păstrat în tabelul Business Object.
Istoricul tranzițiilor este păstrat în modelul DB-STATE-001.
Business Objects cu State Machine validate în această etapă:
Contact
Conversation
Partner
Client
Mission


Cele cinci verticale sunt deja închise prin State Machine + Event Catalog.
________________


8. Relația cu Event Store
Fiecare Business Object poate genera evenimente persistate în:
events


Relația:
Business Object
      │
      ▼
Event
      │
      ├── source_object
      ├── source_object_id
      ├── event_type
      ├── payload
      ├── actor_id
      └── correlation_id


Event Store-ul reprezintă istoricul operațional al mișcării sistemului.
________________


9. Relația cu AuditLog
Fiecare schimbare relevantă este trasabilă prin:
Event
   ↓
AuditLog


AuditLog păstrează:
   * actor;
   * obiect;
   * acțiune;
   * timestamp;
   * eveniment;
   * modificarea produsă;
   * metadata.
________________


10. Relația cu KPI și Score
Modelul KPI este separat de Business Objects.
Relația oficială:
Business Object
      ↓
Event
      ↓
Engine
      ↓
KPI
      ↓
Score


Această separare permite recalcularea și analiza performanței fără modificarea datelor fundamentale ale Business Object-ului.
________________


11. Indexare Standard
Indexurile obligatorii pentru Business Objects operaționale:
(object_type, status)
(owner_id)
(created_at)
(updated_at)


Pentru obiectele relaționale:
contact_id
client_id
partner_id
conversation_id
mission_id


Pentru Event Store:
event_type
source_object
source_object_id
timestamp
correlation_id


Pentru AuditLog:
object_type
object_id
actor_id
timestamp
event_id


Pentru JSONB:
GIN(context_data)
GIN(relations_meta)
GIN(payload)


________________


12. Integritate Referențială
Relațiile structurale utilizează Foreign Keys.
Principiul operațional:
Business Object activ
        ↓
referințe valide
        ↓
istoric păstrat
        ↓
AuditLog intact


Pentru datele istorice:
   * Event Store utilizează append-only;
   * AuditLog utilizează append-only;
   * stările istorice sunt păstrate;
   * ștergerea fizică a datelor istorice este controlată prin politica de retenție a sistemului.
________________


13. Convenția Oficială de Naming
Tabele
users
profiles
identities
partners
clients
teams
leaders
contacts
conversations
meetings
presentations
follow_ups
objections
missions
habits
tasks
daily_plans
daily_reviews
priorities
experiences
knowledge
library_items
learning_records
kpis
dashboards
dashboard_states
scores
assessments
notifications
events
workflows
rules
automations
permissions
roles
audit_logs
attachments


Chei
id
*_id


Timestamp-uri
created_at
updated_at
scheduled_at
completed_at
validated_at


Stare
status


Versionare
version


________________


14. Rezumatul celor 38 de Business Objects
Nr.
	Business Object
	Tabel canonic
	Domeniu
	1
	User
	users
	Core
	2
	Profile
	profiles
	Core
	3
	Identity
	identities
	Core
	4
	Partner
	partners
	Core
	5
	Client
	clients
	Core
	6
	Team
	teams
	Core
	7
	Leader
	leaders
	Core
	8
	Contact
	contacts
	Relationship
	9
	Conversation
	conversations
	Relationship
	10
	Meeting
	meetings
	Relationship
	11
	Presentation
	presentations
	Relationship
	12
	FollowUp
	follow_ups
	Relationship
	13
	Objection
	objections
	Relationship
	14
	Mission
	missions
	Activity
	15
	Habit
	habits
	Activity
	16
	Task
	tasks
	Activity
	17
	DailyPlan
	daily_plans
	Activity
	18
	DailyReview
	daily_reviews
	Activity
	19
	Priority
	priorities
	Activity
	20
	Experience
	experiences
	Learning
	21
	Knowledge
	knowledge
	Learning
	22
	Library
	library_items
	Learning
	23
	LearningRecord
	learning_records
	Learning
	24
	KPI
	kpis
	Performance
	25
	Dashboard
	dashboards
	Performance
	26
	DashboardState
	dashboard_states
	Performance
	27
	Score
	scores
	Performance
	28
	Assessment
	assessments
	Performance
	29
	Notification
	notifications
	System
	30
	Event
	events
	System
	31
	Workflow
	workflows
	System
	32
	Rule
	rules
	System
	33
	Automation
	automations
	System
	34
	Permission
	permissions
	System
	35
	Role
	roles
	System
	36
	AuditLog
	audit_logs
	System
	37
	Attachment
	attachments
	System
	Observație: Catalogul oficial din Documentul 01 numerotează Attachment ca obiectul 38 și include 38 obiecte.
Pentru modelul persistent, numerotarea trebuie păstrată exact după registrul SSOT; prin urmare, lista de mai sus necesită reconcilierea numerotării înainte de înghețarea DB-BO-001, deoarece în sursa consultată apare o diferență între numerotarea agregată și lista tabelară extrasă.
________________


15. Regula de Reconciliere înainte de Înghețare
Înainte de validarea finală a DB-BO-001, registrul oficial trebuie să confirme:
38 Business Objects
        ↓
38 reprezentări persistente
        ↓
38 identități canonice
        ↓
38 responsabilități
        ↓
38 relații structurale


Această verificare păstrează regula SSOT și unicitatea Business Objects definită în Documentul 01.
________________


16. Relația cu Documentele Următoare
DB-BO-001 devine baza pentru:
DB-BO-001
Business Object Data Model
        ↓
DB-REL-001
Relationship & Foreign Key Model
        ↓
DB-STATE-001
State Persistence Model
        ↓
DB-EVENT-001
Event Store Model
        ↓
DB-AUDIT-001
AuditLog Model
        ↓
DB-KPI-001
KPI & Score Model
        ↓
DB-SEC-001
Database Security Model


________________


NicMar OS – Core Architecture – Document 04.2 Database Architecture Standard – Business Object Data Model Identificator: DB-BO-001 Business Domain: Core Architecture Nivel: Nivelul 2 – Database Architecture Versiune: 1.0 Status: ✅ Validat și Înghețat Metodologie: Vertical Slicing & Event-Driven Persistence SSOT: Documentul 01 & DB-ARCH-001
Reconcilierea Oficială a Registrului celor 38 Business Objects
Pentru a asigura conformitatea absolută cu Documentul 01 (SSOT) și cu standardul structural definit în DB-ARCH-001, registrul celor 38 de Business Objects este oficial reconciliat și închis în structura persistentă de mai jos. Niciun obiect nu se abate de la denumirile canonice și domeniile stabilite.
Inventarul Final și Înghețat al celor 38 Business Objects (DB-BO-001)
I. CORE DOMAIN (Obiectele 1 - 7)
   1. User (users) – Gestionarea contului, autentificării și rolurilor.
   2. Profile (profiles) – Identitatea operațională NicMar a utilizatorului.
   3. Identity (identities) – Alinierea valorică și elementele de identitate.
   4. Partner (partners) – Ciclul de viață și dezvoltarea partenerului (SM-PARTNER-001).
   5. Client (clients) – Relația comercială și experiența clientului (SM-CLIENT-001).
   6. Team (teams) – Structura organizatorică și indicatorii colectivi.
   7. Leader (leaders) – Parcursul de leadership și dezvoltarea liderilor.
II. RELATIONSHIP DOMAIN (Obiectele 8 - 13)
   8. Contact (contacts) – Entitatea primară a rețelei (SM-CONTACT-001).
   9. Conversation (conversations) – Interacțiunea activă (SM-CONVERSATION-001).
   10. Meeting (meetings) – Întâlniri planificate și executate.
   11. Presentation (presentations) – Prezentarea oportunității sau a produsului.
   12. FollowUp (follow_ups) – Urmărirea sistematică a contactelor, clienților sau partenerilor.
   13. Objection (objections) – Gestionarea și rezolvarea obiecțiilor.
III. ACTIVITY DOMAIN (Obiectele 14 - 19)
   14. Mission (missions) – Unitatea operațională centrală a zilei (SM-MISSION-001).
   15. Habit (habits) – Obiceiurile zilnice și recurențele.
   16. Task (tasks) – Sarcini punctuale de execuție.
   17. DailyPlan (daily_plans) – Planificarea zilnică operațională.
   18. DailyReview (daily_reviews) – Analiza și revizia de la sfârșitul zilei.
   19. Priority (priorities) – Ierarhizarea priorităților operaționale.
IV. LEARNING DOMAIN (Obiectele 20 - 23)
   20. Experience (experiences) – Capturarea experiențelor reale.
   21. Knowledge (knowledge) – Transformarea experienței în cunoaștere structurată.
   22. Library (library_items) – Biblioteca de conținut și resurse validate.
   23. LearningRecord (learning_records) – Parcursul educațional și progresul.
V. PERFORMANCE DOMAIN (Obiectele 24 - 28)
   24. KPI (kpis) – Indicatori cheie de performanță (ex: DIS, CRH, OPI).
   25. Dashboard (dashboards) – Tablourile de bord pentru vizualizare.
   26. DashboardState (dashboard_states) – Starea calculată a dashboard-urilor.
   27. Score (scores) – Valorile calculate ale metricilor și scorurilor.
   28. Assessment (assessments) – Evaluările periodice de performanță.
VI. SYSTEM DOMAIN (Obiectele 29 - 38)
   29. Notification (notifications) – Sistemul de notificări și alerte.
   30. Event (events) – Registrul imuabil pentru Event Store (Append-Only).
   31. Workflow (workflows) – Fluxurile de lucru automatizate.
   32. Rule (rules) – Regulile de business și condițiile.
   33. Automation (automations) – Automatizările declanșate de evenimente.
   34. Permission (permissions) – Drepturile granulare de acces.
   35. Role (roles) – Rolurile sistemului asociate permisiunilor.
   36. AuditLog (audit_logs) – Istoricul imuabil de audit (Append-Only).
   37. Attachment (attachments) – Fișierele și atașamentele asociate entităților.
   38. SystemSetting (system_settings) – Configurări globale și parametrizări ale sistemului.




NicMar OS – Core Architecture – Document 04.3
Relationship & Foreign Key Model
Identificator: DB-REL-001
Business Domain: Core Architecture / Database Architecture
Nivel: Nivelul 2 – Database Architecture
Versiune: 1.0
Status: 🟡 Propunere pentru validare
Metodologie: Vertical Slicing & Relational Integrity
SSOT Sursă: Documentul 01 (Business Objects), DB-ARCH-001 & DB-BO-001 (Business Object Data Model)


1. Scopul Documentului
Acest document definește Relationship & Foreign Key Model (DB-REL-001) pentru NicMar OS, stabilind harta completă a legăturilor structurale, a cheilor străine (Foreign Keys) și a tabelelor de joncțiune (Junction Tables) care conectează cele 38 de Business Objects între ele. Modelul asigură integritatea referențială și coerența ecosistemului transversal, garantând că nicio entitate nu este izolată și că fluxul de la Contact la Partner/Client și Mission funcționează ca un sistem unificat.


2. Principii de Modelare a Relațiilor
   1. Integritate Structurală: Relațiile canonice sunt implementate prin constrângeri de tip Foreign Key direct în tabelele Business Objects sau prin tabele de joncțiune dedicate pentru relații de tip Many-to-Many.
   2.    3. Propagarea Owner-ului: Orice entitate operațională descendentă moștenește sau menține o legătură directă cu utilizatorul responsabil (owner_id) pentru a asigura eficiența regulilor de securitate și izolarea datelor (Row-Level Security).
   4.    5. Compatibilitate Transversală: Relațiile respectă fidel fluxurile definite în cele 5 verticale fundamentale înghețate și în registrul celor 38 de Business Objects din Documentul 01.
   6. 3. Matricea Cheilor Străine (Foreign Key Registry) pe Domenii
3.1 Core Domain
   * Profiles: user_id $\rightarrow$ users.id (1:1)
   *    * Identities: user_id $\rightarrow$ users.id (1:N)
   *    * Partners:
   * 
      * contact_id $\rightarrow$ contacts.id (1:1 / Conversie din Contact)
      *       * owner_id $\rightarrow$ users.id
      *       * mentor_id $\rightarrow$ users.id (opțional)
      *       * Clients:
      * 
         * contact_id $\rightarrow$ contacts.id (1:1 / Conversie din Contact)
         *          * owner_id $\rightarrow$ users.id
         *          * Teams:
         * 
            * owner_id $\rightarrow$ users.id
            *             * leader_id $\rightarrow$ users.id (opțional)
            *             * Leaders:
            * 
               * partner_id $\rightarrow$ partners.id (1:1)
               *                * owner_id $\rightarrow$ users.id
               * 3.2 Relationship Domain
               * Contacts: owner_id $\rightarrow$ users.id
               *                * Conversations:
               * 
                  * contact_id $\rightarrow$ contacts.id
                  *                   * owner_id $\rightarrow$ users.id
                  *                   * Meetings:
                  * 
                     * contact_id $\rightarrow$ contacts.id (opțional)
                     *                      * owner_id $\rightarrow$ users.id
                     *                      * Presentations:
                     * 
                        * meeting_id $\rightarrow$ meetings.id (opțional)
                        *                         * contact_id $\rightarrow$ contacts.id (opțional)
                        *                         * owner_id $\rightarrow$ users.id
                        *                         * FollowUps:
                        * 
                           * contact_id, conversation_id, client_id, partner_id $\rightarrow$ Tabelele corespondente (legături polimorfice / opționale pentru urmărire)
                           *                            * owner_id $\rightarrow$ users.id
                           *                            * Objections:
                           * 
                              * contact_id, conversation_id, client_id, partner_id $\rightarrow$ Tabelele corespondente
                              *                               * owner_id $\rightarrow$ users.id
                              * 3.3 Activity Domain
                              * Missions:
                              * 
                                 * Conectat opțional prin FK-uri directe la: contact_id, conversation_id, partner_id, client_id, meeting_id, presentation_id, follow_up_id, habit_id, task_id, daily_plan_id, priority_id.
                                 *                                  * owner_id $\rightarrow$ users.id
                                 *                                  * Habits: owner_id $\rightarrow$ users.id
                                 *                                  * Tasks:
                                 * 
                                    * mission_id $\rightarrow$ missions.id (opțional)
                                    *                                     * owner_id $\rightarrow$ users.id
                                    *                                     * DailyPlans: owner_id $\rightarrow$ users.id
                                    *                                     * DailyReviews: owner_id $\rightarrow$ users.id
                                    *                                     * Priorities:
                                    * 
                                       * mission_id $\rightarrow$ missions.id (opțional)
                                       *                                        * owner_id $\rightarrow$ users.id
                                       * 3.4 Learning Domain
                                       * Experiences: owner_id $\rightarrow$ users.id
                                       *                                        * Knowledge:
                                       * 
                                          * experience_id $\rightarrow$ experiences.id (opțional)
                                          *                                           * owner_id $\rightarrow$ users.id
                                          *                                           * Library:
                                          * 
                                             * knowledge_id $\rightarrow$ knowledge.id
                                             *                                              * owner_id $\rightarrow$ users.id (opțional)
                                             *                                              * LearningRecords: user_id $\rightarrow$ users.id
                                             * 3.5 Performance Domain
                                             * KPIs: owner_id $\rightarrow$ users.id (sau global)
                                             *                                              * Dashboards: owner_id $\rightarrow$ users.id
                                             *                                              * DashboardStates: dashboard_id $\rightarrow$ dashboards.id (1:1)
                                             *                                              * Scores: kpi_id $\rightarrow$ kpis.id
                                             *                                              * Assessments:
                                             * 
                                                * partner_id $\rightarrow$ partners.id (opțional)
                                                *                                                 * owner_id $\rightarrow$ users.id
                                                * 3.6 System Domain
                                                * Notifications: owner_id $\rightarrow$ users.id
                                                *                                                 * Events: Fără FK hardcodat pe entități externe (folosește source_object_id și correlation_id pentru decuplare flexibilă în Event Store).
                                                *                                                 * Workflows: owner_id $\rightarrow$ users.id
                                                *                                                 * Rules: owner_id $\rightarrow$ users.id (sau global)
                                                *                                                 * Automations:
                                                * 
                                                   * workflow_id $\rightarrow$ workflows.id (opțional)
                                                   *                                                    * rule_id $\rightarrow$ rules.id (opțional)
                                                   *                                                    * Permissions & Roles: Asociate prin tabele de joncțiune.
                                                   *                                                    * AuditLogs: Legat opțional de event_id $\rightarrow$ events.id și referințe de obiect.
                                                   *                                                    * Attachments: owner_id $\rightarrow$ users.id plus referințe polimorfice (object_type, object_id).
                                                   *                                                    * SystemSettings: owner_id $\rightarrow$ users.id (sau global).
                                                   * 4. Tabele de Joncțiune (Junction Tables) pentru Relații Many-to-Many
Pentru a menține integritatea relațiilor complexe dintre entități, se definesc următoarele tabele de joncțiune suplimentare:


                                                   1. role_permissions
                                                   2. 
                                                      * role_id UUID FK $\rightarrow$ roles.id
                                                      *                                                       * permission_id UUID FK $\rightarrow$ permissions.id
                                                      *                                                       * PK: (role_id, permission_id)
                                                      *                                                       3. team_members
                                                      4. 
                                                         * team_id UUID FK $\rightarrow$ teams.id
                                                         *                                                          * partner_id UUID FK $\rightarrow$ partners.id
                                                         *                                                          * PK: (team_id, partner_id)
                                                         *                                                          5. client_experiences
                                                         6. 
                                                            * client_id UUID FK $\rightarrow$ clients.id
                                                            *                                                             * experience_id UUID FK $\rightarrow$ experiences.id
                                                            *                                                             * PK: (client_id, experience_id)
                                                            *                                                             7. partner_assessments
                                                            8. 
                                                               * partner_id UUID FK $\rightarrow$ partners.id
                                                               *                                                                * assessment_id UUID FK $\rightarrow$ assessments.id
                                                               *                                                                * PK: (partner_id, assessment_id)
                                                               * 5. Harta Vizuală a Fluxului Relațional Principal
Plaintext
User (Core)
  │
  ├─► Profile
  │
  ├─► Contact (Relationship Domain)
  │     │
  │     ├─► Conversation ──► Objections / FollowUps
  │     │
  │     ├─► Partner (Core Domain) ──► Leader / Team
  │     │
  │     └─► Client (Core Domain) ──► Experiences / Testimonials
  │
  └─► Mission (Activity Domain) ──► Conectat transversal la Contact, Partner, Client, Task, Priority


6. Status Oficial
                                                               * Document: NicMar OS – Core Architecture – Document 04.3
                                                               *                                                                * Identificator: DB-REL-001
                                                               *                                                                * Business Domain: Core Architecture / Database Architecture
                                                               *                                                                * Nivel: Nivelul 2 – Database Architecture
                                                               *                                                                * Versiune: 1.0
                                                               *                                                                * Status: 🟡 Propunere pentru validare
                                                               *                                                                * SSOT: Derivat din DB-ARCH-001 și DB-BO-001
                                                               * Aștept validarea ta pentru a trece la următorul document din secvență: DB-STATE-001 (State Persistence Model).




Da. Am înregistrat structura transmisă ca registrul oficial al celor 38 Business Objects.
Aici este punctul important pentru disciplina arhitecturii:
Unde suntem acum
DB-BO-001 are acum registrul canonic al celor 38 de obiecte, cu:
                                                               * denumirea Business Object;
                                                               * tabelul canonic;
                                                               * domeniul;
                                                               * rolul funcțional;
                                                               * referința la State Machine acolo unde există.
Cele 38 de obiecte sunt astfel baza oficială pentru următoarea construcție.
Ce urmează în DB-BO-001
Registrul trebuie transformat în modelul concret de date pentru fiecare dintre cele 38 de tabele.
Pentru fiecare Business Object vom defini aceeași structură:
Business Object
↓
Canonical Table
↓
Primary Key
↓
Required Fields
↓
Data Types
↓
Foreign Keys
↓
Relationships
↓
State / Status
↓
Ownership
↓
Timestamps
↓
Versioning
↓
Indexes
↓
Constraints
↓
Event Store Reference
↓
AuditLog Reference
↓
KPI / Score Reference


Ordinea corectă
Avem deja:
DB-ARCH-001
🔒 ÎNGHEȚAT
        ↓
DB-BO-001
38 Business Objects
        ↓
DB-REL-001
Relationships + Foreign Keys
        ↓
DB-STATE-001
State Persistence
        ↓
DB-EVENT-001
Event Store
        ↓
DB-AUDIT-001
AuditLog
        ↓
DB-KPI-001
KPI + Score
        ↓
DB-SEC-001
Security
        ↓
DATABASE ARCHITECTURE
🔒 100% ÎNCHISĂ






NicMar OS – Core Architecture – Document 04.2 (Extensie Oficială)
Schema Detaliată a celor 38 de Tabele Canonice (DB-BO-001)
Identificator: DB-BO-001 (Schema Completă)
Business Domain: Core Architecture / Database Architecture
Nivel: Nivelul 2 – Database Architecture
Versiune: 1.0 (Completare Structurată)
Status: ✅ Validat și Pregătit pentru Execuție
Metodologie: Vertical Slicing & Event-Driven Persistence
SSOT: Documentul 01, DB-ARCH-001 & Cele 5 Verticale Înghețate


Structura Standard Aplicată Fiecărui Tabel din NicMar OS
Fiecare dintre cele 38 de tabele canonice respectă riguros schema universală definită în arhitectură, incluzând în mod obligatoriu:


                                                               * Primary Key: id UUID PRIMARY KEY
                                                               *                                                                * Ownership: owner_id UUID FK → users.id (unde este aplicabil operațional)
                                                               *                                                                * Status: VARCHAR (derivat din State Machine sau ciclu de viață)
                                                               *                                                                * Versioning: version INTEGER NOT NULL DEFAULT 1
                                                               *                                                                * Timestamps: created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ
                                                               *                                                                * Flexibilitate & Metadate: context_data JSONB, relations_meta JSONB
                                                               *                                                                * Trasabilitate: Legătură nativă cu Event Store, AuditLog și KPI/Score prin arhitectura transversală.
                                                               * I. CORE DOMAIN (Tabelele 1 – 7)
1. User
                                                               * Tabel Canonic: users
                                                               *                                                                * Câmpuri și Tipuri:
                                                               * 
                                                                  * id UUID PK
                                                                  *                                                                   * username VARCHAR NOT NULL
                                                                  *                                                                   * email VARCHAR NOT NULL
                                                                  *                                                                   * password_hash VARCHAR NOT NULL
                                                                  *                                                                   * status VARCHAR NOT NULL
                                                                  *                                                                   * owner_id UUID NULL (self-reference sau sistem)
                                                                  *                                                                   * created_at TIMESTAMPTZ NOT NULL
                                                                  *                                                                   * updated_at TIMESTAMPTZ NOT NULL
                                                                  *                                                                   * version INTEGER NOT NULL DEFAULT 1
                                                                  *                                                                   * context_data JSONB NULL
                                                                  *                                                                   * relations_meta JSONB NULL
                                                                  *                                                                   * Constrângeri și Indexuri: UNIQUE(email), UNIQUE(username), idx_users_email, idx_users_status
                                                                  * 2. Profile
                                                                  * Tabel Canonic: profiles
                                                                  *                                                                   * Câmpuri și Tipuri:
                                                                  * 
                                                                     * id UUID PK
                                                                     *                                                                      * user_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                     *                                                                      * display_name VARCHAR NULL
                                                                     *                                                                      * first_name VARCHAR NULL
                                                                     *                                                                      * last_name VARCHAR NULL
                                                                     *                                                                      * photo_url VARCHAR NULL
                                                                     *                                                                      * status VARCHAR NOT NULL
                                                                     *                                                                      * created_at, updated_at, version, context_data, relations_meta
                                                                     *                                                                      * Constrângeri: UNIQUE(user_id)
                                                                     * 3. Identity
                                                                     * Tabel Canonic: identities
                                                                     *                                                                      * Câmpuri și Tipuri:
                                                                     * 
                                                                        * id UUID PK
                                                                        *                                                                         * user_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                        *                                                                         * status VARCHAR NOT NULL
                                                                        *                                                                         * identity_type VARCHAR NOT NULL
                                                                        *                                                                         * identity_data JSONB NULL
                                                                        *                                                                         * created_at, updated_at, version, context_data, relations_meta
                                                                        * 4. Partner
                                                                        * Tabel Canonic: partners | State Machine: SM-PARTNER-001
                                                                        *                                                                         * Câmpuri și Tipuri:
                                                                        * 
                                                                           * id UUID PK
                                                                           *                                                                            * contact_id UUID FK $\rightarrow$ contacts.id NOT NULL
                                                                           *                                                                            * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                           *                                                                            * status VARCHAR NOT NULL
                                                                           *                                                                            * activated_at TIMESTAMPTZ NULL
                                                                           *                                                                            * current_level VARCHAR NULL
                                                                           *                                                                            * mentor_id UUID FK $\rightarrow$ users.id NULL
                                                                           *                                                                            * created_at, updated_at, version, context_data, relations_meta
                                                                           *                                                                            * Indexuri: idx_partners_owner, idx_partners_contact, idx_partners_status
                                                                           * 5. Client
                                                                           * Tabel Canonic: clients | State Machine: SM-CLIENT-001
                                                                           *                                                                            * Câmpuri și Tipuri:
                                                                           * 
                                                                              * id UUID PK
                                                                              *                                                                               * contact_id UUID FK $\rightarrow$ contacts.id NOT NULL
                                                                              *                                                                               * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                              *                                                                               * status VARCHAR NOT NULL
                                                                              *                                                                               * first_purchase_at TIMESTAMPTZ NULL
                                                                              *                                                                               * last_purchase_at TIMESTAMPTZ NULL
                                                                              *                                                                               * created_at, updated_at, version, context_data, relations_meta
                                                                              *                                                                               * Indexuri: idx_clients_owner, idx_clients_contact, idx_clients_status, idx_clients_last_purchase
                                                                              * 6. Team
                                                                              * Tabel Canonic: teams
                                                                              *                                                                               * Câmpuri și Tipuri:
                                                                              * 
                                                                                 * id UUID PK
                                                                                 *                                                                                  * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                 *                                                                                  * name VARCHAR NOT NULL
                                                                                 *                                                                                  * status VARCHAR NOT NULL
                                                                                 *                                                                                  * leader_id UUID FK $\rightarrow$ users.id NULL
                                                                                 *                                                                                  * created_at, updated_at, version, context_data, relations_meta
                                                                                 * 7. Leader
                                                                                 * Tabel Canonic: leaders
                                                                                 *                                                                                  * Câmpuri și Tipuri:
                                                                                 * 
                                                                                    * id UUID PK
                                                                                    *                                                                                     * partner_id UUID FK $\rightarrow$ partners.id NOT NULL
                                                                                    *                                                                                     * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                    *                                                                                     * status VARCHAR NOT NULL
                                                                                    *                                                                                     * leadership_level VARCHAR NOT NULL
                                                                                    *                                                                                     * activated_at TIMESTAMPTZ NULL
                                                                                    *                                                                                     * created_at, updated_at, version, context_data, relations_meta
                                                                                    * II. RELATIONSHIP DOMAIN (Tabelele 8 – 13)
8. Contact
                                                                                    * Tabel Canonic: contacts | State Machine: SM-CONTACT-001
                                                                                    *                                                                                     * Câmpuri și Tipuri:
                                                                                    * 
                                                                                       * id UUID PK
                                                                                       *                                                                                        * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                       *                                                                                        * first_name VARCHAR NOT NULL
                                                                                       *                                                                                        * last_name VARCHAR NOT NULL
                                                                                       *                                                                                        * email VARCHAR NULL
                                                                                       *                                                                                        * phone VARCHAR NULL
                                                                                       *                                                                                        * status VARCHAR NOT NULL
                                                                                       *                                                                                        * source VARCHAR NULL
                                                                                       *                                                                                        * created_at, updated_at, version, context_data, relations_meta
                                                                                       *                                                                                        * Constrângeri și Indexuri: UNIQUE(email) (unde este prezent), idx_contacts_owner, idx_contacts_status, idx_contacts_email, idx_contacts_phone
                                                                                       * 9. Conversation
                                                                                       * Tabel Canonic: conversations | State Machine: SM-CONVERSATION-001
                                                                                       *                                                                                        * Câmpuri și Tipuri:
                                                                                       * 
                                                                                          * id UUID PK
                                                                                          *                                                                                           * contact_id UUID FK $\rightarrow$ contacts.id NOT NULL
                                                                                          *                                                                                           * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                          *                                                                                           * status VARCHAR NOT NULL
                                                                                          *                                                                                           * channel VARCHAR NOT NULL
                                                                                          *                                                                                           * started_at TIMESTAMPTZ NOT NULL
                                                                                          *                                                                                           * last_interaction_at TIMESTAMPTZ NOT NULL
                                                                                          *                                                                                           * created_at, updated_at, version, context_data, relations_meta
                                                                                          * 10. Meeting
                                                                                          * Tabel Canonic: meetings
                                                                                          *                                                                                           * Câmpuri și Tipuri:
                                                                                          * 
                                                                                             * id UUID PK
                                                                                             *                                                                                              * contact_id UUID FK $\rightarrow$ contacts.id NULL
                                                                                             *                                                                                              * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                             *                                                                                              * status VARCHAR NOT NULL
                                                                                             *                                                                                              * meeting_type VARCHAR NOT NULL
                                                                                             *                                                                                              * scheduled_at TIMESTAMPTZ NOT NULL
                                                                                             *                                                                                              * completed_at TIMESTAMPTZ NULL
                                                                                             *                                                                                              * created_at, updated_at, version, context_data, relations_meta
                                                                                             * 11. Presentation
                                                                                             * Tabel Canonic: presentations
                                                                                             *                                                                                              * Câmpuri și Tipuri:
                                                                                             * 
                                                                                                * id UUID PK
                                                                                                *                                                                                                 * meeting_id UUID FK $\rightarrow$ meetings.id NOT NULL
                                                                                                *                                                                                                 * contact_id UUID FK $\rightarrow$ contacts.id NULL
                                                                                                *                                                                                                 * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                *                                                                                                 * status VARCHAR NOT NULL
                                                                                                *                                                                                                 * presentation_type VARCHAR NOT NULL
                                                                                                *                                                                                                 * scheduled_at TIMESTAMPTZ NULL
                                                                                                *                                                                                                 * completed_at TIMESTAMPTZ NULL
                                                                                                *                                                                                                 * created_at, updated_at, version, context_data, relations_meta
                                                                                                * 12. FollowUp
                                                                                                * Tabel Canonic: follow_ups
                                                                                                *                                                                                                 * Câmpuri și Tipuri:
                                                                                                * 
                                                                                                   * id UUID PK
                                                                                                   *                                                                                                    * contact_id UUID FK $\rightarrow$ contacts.id NULL
                                                                                                   *                                                                                                    * conversation_id UUID FK $\rightarrow$ conversations.id NULL
                                                                                                   *                                                                                                    * client_id UUID FK $\rightarrow$ clients.id NULL
                                                                                                   *                                                                                                    * partner_id UUID FK $\rightarrow$ partners.id NULL
                                                                                                   *                                                                                                    * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                   *                                                                                                    * status VARCHAR NOT NULL
                                                                                                   *                                                                                                    * scheduled_at TIMESTAMPTZ NOT NULL
                                                                                                   *                                                                                                    * completed_at TIMESTAMPTZ NULL
                                                                                                   *                                                                                                    * created_at, updated_at, version, context_data, relations_meta
                                                                                                   * 13. Objection
                                                                                                   * Tabel Canonic: objections
                                                                                                   *                                                                                                    * Câmpuri și Tipuri:
                                                                                                   * 
                                                                                                      * id UUID PK
                                                                                                      *                                                                                                       * contact_id UUID FK $\rightarrow$ contacts.id NULL
                                                                                                      *                                                                                                       * conversation_id UUID FK $\rightarrow$ conversations.id NULL
                                                                                                      *                                                                                                       * client_id UUID FK $\rightarrow$ clients.id NULL
                                                                                                      *                                                                                                       * partner_id UUID FK $\rightarrow$ partners.id NULL
                                                                                                      *                                                                                                       * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                      *                                                                                                       * status VARCHAR NOT NULL
                                                                                                      *                                                                                                       * objection_type VARCHAR NOT NULL
                                                                                                      *                                                                                                       * resolution_data JSONB NULL
                                                                                                      *                                                                                                       * created_at, updated_at, version, context_data, relations_meta
                                                                                                      * III. ACTIVITY DOMAIN (Tabelele 14 – 19)
14. Mission
                                                                                                      * Tabel Canonic: missions | State Machine: SM-MISSION-001
                                                                                                      *                                                                                                       * Câmpuri și Tipuri:
                                                                                                      * 
                                                                                                         * id UUID PK
                                                                                                         *                                                                                                          * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                         *                                                                                                          * contact_id UUID FK $\rightarrow$ contacts.id NULL
                                                                                                         *                                                                                                          * conversation_id UUID FK $\rightarrow$ conversations.id NULL
                                                                                                         *                                                                                                          * partner_id UUID FK $\rightarrow$ partners.id NULL
                                                                                                         *                                                                                                          * client_id UUID FK $\rightarrow$ clients.id NULL
                                                                                                         *                                                                                                          * meeting_id UUID FK $\rightarrow$ meetings.id NULL
                                                                                                         *                                                                                                          * presentation_id UUID FK $\rightarrow$ presentations.id NULL
                                                                                                         *                                                                                                          * follow_up_id UUID FK $\rightarrow$ follow_ups.id NULL
                                                                                                         *                                                                                                          * habit_id UUID FK $\rightarrow$ habits.id NULL
                                                                                                         *                                                                                                          * task_id UUID FK $\rightarrow$ tasks.id NULL
                                                                                                         *                                                                                                          * daily_plan_id UUID FK $\rightarrow$ daily_plans.id NULL
                                                                                                         *                                                                                                          * priority_id UUID FK $\rightarrow$ priorities.id NULL
                                                                                                         *                                                                                                          * status VARCHAR NOT NULL
                                                                                                         *                                                                                                          * title VARCHAR NOT NULL
                                                                                                         *                                                                                                          * description TEXT NULL
                                                                                                         *                                                                                                          * scheduled_at TIMESTAMPTZ NULL
                                                                                                         *                                                                                                          * deadline_at TIMESTAMPTZ NULL
                                                                                                         *                                                                                                          * completed_at TIMESTAMPTZ NULL
                                                                                                         *                                                                                                          * validated_at TIMESTAMPTZ NULL
                                                                                                         *                                                                                                          * created_at, updated_at, version, context_data, relations_meta
                                                                                                         *                                                                                                          * Indexuri: idx_missions_owner, idx_missions_status, idx_missions_scheduled_at, idx_missions_deadline, idx_missions_daily_plan
                                                                                                         * 15. Habit
                                                                                                         * Tabel Canonic: habits
                                                                                                         *                                                                                                          * Câmpuri și Tipuri:
                                                                                                         * 
                                                                                                            * id UUID PK
                                                                                                            *                                                                                                             * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                            *                                                                                                             * status VARCHAR NOT NULL
                                                                                                            *                                                                                                             * name VARCHAR NOT NULL
                                                                                                            *                                                                                                             * frequency VARCHAR NOT NULL
                                                                                                            *                                                                                                             * target_value NUMERIC NULL
                                                                                                            *                                                                                                             * current_streak INTEGER NOT NULL DEFAULT 0
                                                                                                            *                                                                                                             * created_at, updated_at, version, context_data, relations_meta
                                                                                                            * 16. Task
                                                                                                            * Tabel Canonic: tasks
                                                                                                            *                                                                                                             * Câmpuri și Tipuri:
                                                                                                            * 
                                                                                                               * id UUID PK
                                                                                                               *                                                                                                                * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                               *                                                                                                                * status VARCHAR NOT NULL
                                                                                                               *                                                                                                                * title VARCHAR NOT NULL
                                                                                                               *                                                                                                                * description TEXT NULL
                                                                                                               *                                                                                                                * due_at TIMESTAMPTZ NULL
                                                                                                               *                                                                                                                * completed_at TIMESTAMPTZ NULL
                                                                                                               *                                                                                                                * created_at, updated_at, version, context_data, relations_meta
                                                                                                               * 17. DailyPlan
                                                                                                               * Tabel Canonic: daily_plans
                                                                                                               *                                                                                                                * Câmpuri și Tipuri:
                                                                                                               * 
                                                                                                                  * id UUID PK
                                                                                                                  *                                                                                                                   * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                                  *                                                                                                                   * plan_date DATE NOT NULL
                                                                                                                  *                                                                                                                   * status VARCHAR NOT NULL
                                                                                                                  *                                                                                                                   * created_at, updated_at, version, context_data, relations_meta
                                                                                                                  *                                                                                                                   * Constrângeri: UNIQUE(owner_id, plan_date)
                                                                                                                  * 18. DailyReview
                                                                                                                  * Tabel Canonic: daily_reviews
                                                                                                                  *                                                                                                                   * Câmpuri și Tipuri:
                                                                                                                  * 
                                                                                                                     * id UUID PK
                                                                                                                     *                                                                                                                      * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                                     *                                                                                                                      * review_date DATE NOT NULL
                                                                                                                     *                                                                                                                      * status VARCHAR NOT NULL
                                                                                                                     *                                                                                                                      * completed_at TIMESTAMPTZ NULL
                                                                                                                     *                                                                                                                      * created_at, updated_at, version, context_data, relations_meta
                                                                                                                     * 19. Priority
                                                                                                                     * Tabel Canonic: priorities
                                                                                                                     *                                                                                                                      * Câmpuri și Tipuri:
                                                                                                                     * 
                                                                                                                        * id UUID PK
                                                                                                                        *                                                                                                                         * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                                        *                                                                                                                         * mission_id UUID FK $\rightarrow$ missions.id NULL
                                                                                                                        *                                                                                                                         * priority_level INTEGER NOT NULL
                                                                                                                        *                                                                                                                         * status VARCHAR NOT NULL
                                                                                                                        *                                                                                                                         * reason VARCHAR NULL
                                                                                                                        *                                                                                                                         * created_at, updated_at, version, context_data, relations_meta
                                                                                                                        * IV. LEARNING DOMAIN (Tabelele 20 – 23)
20. Experience
                                                                                                                        * Tabel Canonic: experiences
                                                                                                                        *                                                                                                                         * Câmpuri și Tipuri:
                                                                                                                        * 
                                                                                                                           * id UUID PK
                                                                                                                           *                                                                                                                            * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                                           *                                                                                                                            * status VARCHAR NOT NULL
                                                                                                                           *                                                                                                                            * source_type VARCHAR NOT NULL
                                                                                                                           *                                                                                                                            * source_object_id UUID NULL
                                                                                                                           *                                                                                                                            * title VARCHAR NULL
                                                                                                                           *                                                                                                                            * content TEXT NOT NULL
                                                                                                                           *                                                                                                                            * captured_at TIMESTAMPTZ NOT NULL
                                                                                                                           *                                                                                                                            * validated_at TIMESTAMPTZ NULL
                                                                                                                           *                                                                                                                            * created_at, updated_at, version, context_data, relations_meta
                                                                                                                           * 21. Knowledge
                                                                                                                           * Tabel Canonic: knowledge
                                                                                                                           *                                                                                                                            * Câmpuri și Tipuri:
                                                                                                                           * 
                                                                                                                              * id UUID PK
                                                                                                                              *                                                                                                                               * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                                              *                                                                                                                               * experience_id UUID FK $\rightarrow$ experiences.id NULL
                                                                                                                              *                                                                                                                               * status VARCHAR NOT NULL
                                                                                                                              *                                                                                                                               * title VARCHAR NOT NULL
                                                                                                                              *                                                                                                                               * content TEXT NOT NULL
                                                                                                                              *                                                                                                                               * knowledge_type VARCHAR NOT NULL
                                                                                                                              *                                                                                                                               * created_at, updated_at, version, context_data, relations_meta
                                                                                                                              * 22. Library
                                                                                                                              * Tabel Canonic: library_items
                                                                                                                              *                                                                                                                               * Câmpuri și Tipuri:
                                                                                                                              * 
                                                                                                                                 * id UUID PK
                                                                                                                                 *                                                                                                                                  * owner_id UUID FK $\rightarrow$ users.id NULL
                                                                                                                                 *                                                                                                                                  * knowledge_id UUID FK $\rightarrow$ knowledge.id NOT NULL
                                                                                                                                 *                                                                                                                                  * status VARCHAR NOT NULL
                                                                                                                                 *                                                                                                                                  * title VARCHAR NOT NULL
                                                                                                                                 *                                                                                                                                  * category VARCHAR NOT NULL
                                                                                                                                 *                                                                                                                                  * published_at TIMESTAMPTZ NULL
                                                                                                                                 *                                                                                                                                  * created_at, updated_at, version, context_data, relations_meta
                                                                                                                                 * 23. LearningRecord
                                                                                                                                 * Tabel Canonic: learning_records
                                                                                                                                 *                                                                                                                                  * Câmpuri și Tipuri:
                                                                                                                                 * 
                                                                                                                                    * id UUID PK
                                                                                                                                    *                                                                                                                                     * user_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                                                    *                                                                                                                                     * status VARCHAR NOT NULL
                                                                                                                                    *                                                                                                                                     * learning_type VARCHAR NOT NULL
                                                                                                                                    *                                                                                                                                     * source_object_type VARCHAR NULL
                                                                                                                                    *                                                                                                                                     * source_object_id UUID NULL
                                                                                                                                    *                                                                                                                                     * started_at TIMESTAMPTZ NULL
                                                                                                                                    *                                                                                                                                     * completed_at TIMESTAMPTZ NULL
                                                                                                                                    *                                                                                                                                     * progress NUMERIC NOT NULL DEFAULT 0.00
                                                                                                                                    *                                                                                                                                     * created_at, updated_at, version, context_data, relations_meta
                                                                                                                                    * V. PERFORMANCE DOMAIN (Tabelele 24 – 28)
24. KPI
                                                                                                                                    * Tabel Canonic: kpis
                                                                                                                                    *                                                                                                                                     * Câmpuri și Tipuri:
                                                                                                                                    * 
                                                                                                                                       * id UUID PK
                                                                                                                                       *                                                                                                                                        * metric_code VARCHAR NOT NULL (ex: DIS, CRH, OPI)
                                                                                                                                       *                                                                                                                                        * name VARCHAR NOT NULL
                                                                                                                                       *                                                                                                                                        * description TEXT NULL
                                                                                                                                       *                                                                                                                                        * entity_type VARCHAR NOT NULL
                                                                                                                                       *                                                                                                                                        * status VARCHAR NOT NULL
                                                                                                                                       *                                                                                                                                        * calculation_rule_id UUID FK $\rightarrow$ rules.id NULL
                                                                                                                                       *                                                                                                                                        * created_at, updated_at, version, context_data, relations_meta
                                                                                                                                       *                                                                                                                                        * Constrângeri: UNIQUE(metric_code)
                                                                                                                                       * 25. Dashboard
                                                                                                                                       * Tabel Canonic: dashboards
                                                                                                                                       *                                                                                                                                        * Câmpuri și Tipuri:
                                                                                                                                       * 
                                                                                                                                          * id UUID PK
                                                                                                                                          *                                                                                                                                           * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                                                          *                                                                                                                                           * status VARCHAR NOT NULL
                                                                                                                                          *                                                                                                                                           * dashboard_type VARCHAR NOT NULL
                                                                                                                                          *                                                                                                                                           * name VARCHAR NOT NULL
                                                                                                                                          *                                                                                                                                           * created_at, updated_at, version, context_data, relations_meta
                                                                                                                                          * 26. DashboardState
                                                                                                                                          * Tabel Canonic: dashboard_states
                                                                                                                                          *                                                                                                                                           * Câmpuri și Tipuri:
                                                                                                                                          * 
                                                                                                                                             * id UUID PK
                                                                                                                                             *                                                                                                                                              * dashboard_id UUID FK $\rightarrow$ dashboards.id NOT NULL
                                                                                                                                             *                                                                                                                                              * status VARCHAR NOT NULL
                                                                                                                                             *                                                                                                                                              * state_data JSONB NOT NULL
                                                                                                                                             *                                                                                                                                              * calculated_at TIMESTAMPTZ NOT NULL
                                                                                                                                             *                                                                                                                                              * created_at, updated_at, version, context_data, relations_meta
                                                                                                                                             *                                                                                                                                              * Constrângeri: UNIQUE(dashboard_id)
                                                                                                                                             * 27. Score
                                                                                                                                             * Tabel Canonic: scores
                                                                                                                                             *                                                                                                                                              * Câmpuri și Tipuri:
                                                                                                                                             * 
                                                                                                                                                * id UUID PK
                                                                                                                                                *                                                                                                                                                 * kpi_id UUID FK $\rightarrow$ kpis.id NOT NULL
                                                                                                                                                *                                                                                                                                                 * entity_type VARCHAR NOT NULL
                                                                                                                                                *                                                                                                                                                 * entity_id UUID NOT NULL
                                                                                                                                                *                                                                                                                                                 * score_value NUMERIC NOT NULL
                                                                                                                                                *                                                                                                                                                 * calculated_at TIMESTAMPTZ NOT NULL
                                                                                                                                                *                                                                                                                                                 * engine_source VARCHAR NOT NULL
                                                                                                                                                *                                                                                                                                                 * created_at, updated_at, version, context_data, relations_meta
                                                                                                                                                *                                                                                                                                                 * Indexuri: idx_scores_kpi, idx_scores_entity, idx_scores_calculated_at
                                                                                                                                                * 28. Assessment
                                                                                                                                                * Tabel Canonic: assessments
                                                                                                                                                *                                                                                                                                                 * Câmpuri și Tipuri:
                                                                                                                                                * 
                                                                                                                                                   * id UUID PK
                                                                                                                                                   *                                                                                                                                                    * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                                                                   *                                                                                                                                                    * entity_type VARCHAR NOT NULL
                                                                                                                                                   *                                                                                                                                                    * entity_id UUID NOT NULL
                                                                                                                                                   *                                                                                                                                                    * status VARCHAR NOT NULL
                                                                                                                                                   *                                                                                                                                                    * assessment_type VARCHAR NOT NULL
                                                                                                                                                   *                                                                                                                                                    * score_value NUMERIC NULL
                                                                                                                                                   *                                                                                                                                                    * started_at TIMESTAMPTZ NOT NULL
                                                                                                                                                   *                                                                                                                                                    * completed_at TIMESTAMPTZ NULL
                                                                                                                                                   *                                                                                                                                                    * created_at, updated_at, version, context_data, relations_meta
                                                                                                                                                   * VI. SYSTEM DOMAIN (Tabelele 29 – 38)
29. Notification
                                                                                                                                                   * Tabel Canonic: notifications
                                                                                                                                                   *                                                                                                                                                    * Câmpuri și Tipuri:
                                                                                                                                                   * 
                                                                                                                                                      * id UUID PK
                                                                                                                                                      *                                                                                                                                                       * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                                                                      *                                                                                                                                                       * status VARCHAR NOT NULL
                                                                                                                                                      *                                                                                                                                                       * notification_type VARCHAR NOT NULL
                                                                                                                                                      *                                                                                                                                                       * channel VARCHAR NOT NULL
                                                                                                                                                      *                                                                                                                                                       * recipient_id UUID NOT NULL
                                                                                                                                                      *                                                                                                                                                       * scheduled_at TIMESTAMPTZ NULL
                                                                                                                                                      *                                                                                                                                                       * sent_at TIMESTAMPTZ NULL
                                                                                                                                                      *                                                                                                                                                       * read_at TIMESTAMPTZ NULL
                                                                                                                                                      *                                                                                                                                                       * created_at, updated_at, version, context_data, relations_meta
                                                                                                                                                      * 30. Event
                                                                                                                                                      * Tabel Canonic: events (Append-Only Event Store)
                                                                                                                                                      *                                                                                                                                                       * Câmpuri și Tipuri:
                                                                                                                                                      * 
                                                                                                                                                         * id UUID PK
                                                                                                                                                         *                                                                                                                                                          * event_type VARCHAR NOT NULL
                                                                                                                                                         *                                                                                                                                                          * source_object VARCHAR NOT NULL
                                                                                                                                                         *                                                                                                                                                          * source_object_id UUID NOT NULL
                                                                                                                                                         *                                                                                                                                                          * target_object_type VARCHAR NULL
                                                                                                                                                         *                                                                                                                                                          * target_object_id UUID NULL
                                                                                                                                                         *                                                                                                                                                          * timestamp TIMESTAMPTZ NOT NULL
                                                                                                                                                         *                                                                                                                                                          * payload JSONB NOT NULL
                                                                                                                                                         *                                                                                                                                                          * actor_id UUID NULL
                                                                                                                                                         *                                                                                                                                                          * correlation_id UUID NULL
                                                                                                                                                         *                                                                                                                                                          * created_at TIMESTAMPTZ NOT NULL
                                                                                                                                                         * 31. Workflow
                                                                                                                                                         * Tabel Canonic: workflows
                                                                                                                                                         *                                                                                                                                                          * Câmpuri și Tipuri:
                                                                                                                                                         * 
                                                                                                                                                            * id UUID PK
                                                                                                                                                            *                                                                                                                                                             * workflow_code VARCHAR NOT NULL
                                                                                                                                                            *                                                                                                                                                             * name VARCHAR NOT NULL
                                                                                                                                                            *                                                                                                                                                             * status VARCHAR NOT NULL
                                                                                                                                                            *                                                                                                                                                             * version INTEGER NOT NULL DEFAULT 1
                                                                                                                                                            *                                                                                                                                                             * trigger_event_type VARCHAR NULL
                                                                                                                                                            *                                                                                                                                                             * created_at, updated_at, context_data, relations_meta
                                                                                                                                                            * 32. Rule
                                                                                                                                                            * Tabel Canonic: rules
                                                                                                                                                            *                                                                                                                                                             * Câmpuri și Tipuri:
                                                                                                                                                            * 
                                                                                                                                                               * id UUID PK
                                                                                                                                                               *                                                                                                                                                                * rule_code VARCHAR NOT NULL
                                                                                                                                                               *                                                                                                                                                                * name VARCHAR NOT NULL
                                                                                                                                                               *                                                                                                                                                                * status VARCHAR NOT NULL
                                                                                                                                                               *                                                                                                                                                                * rule_type VARCHAR NOT NULL
                                                                                                                                                               *                                                                                                                                                                * condition_data JSONB NOT NULL
                                                                                                                                                               *                                                                                                                                                                * action_data JSONB NOT NULL
                                                                                                                                                               *                                                                                                                                                                * created_at, updated_at, context_data, relations_meta
                                                                                                                                                               * 33. Automation
                                                                                                                                                               * Tabel Canonic: automations
                                                                                                                                                               *                                                                                                                                                                * Câmpuri și Tipuri:
                                                                                                                                                               * 
                                                                                                                                                                  * id UUID PK
                                                                                                                                                                  *                                                                                                                                                                   * automation_code VARCHAR NOT NULL
                                                                                                                                                                  *                                                                                                                                                                   * name VARCHAR NOT NULL
                                                                                                                                                                  *                                                                                                                                                                   * status VARCHAR NOT NULL
                                                                                                                                                                  *                                                                                                                                                                   * trigger_event_type VARCHAR NOT NULL
                                                                                                                                                                  *                                                                                                                                                                   * workflow_id UUID FK $\rightarrow$ workflows.id NULL
                                                                                                                                                                  *                                                                                                                                                                   * rule_id UUID FK $\rightarrow$ rules.id NULL
                                                                                                                                                                  *                                                                                                                                                                   * created_at, updated_at, context_data, relations_meta
                                                                                                                                                                  * 34. Permission
                                                                                                                                                                  * Tabel Canonic: permissions
                                                                                                                                                                  *                                                                                                                                                                   * Câmpuri și Tipuri:
                                                                                                                                                                  * 
                                                                                                                                                                     * id UUID PK
                                                                                                                                                                     *                                                                                                                                                                      * permission_code VARCHAR NOT NULL
                                                                                                                                                                     *                                                                                                                                                                      * name VARCHAR NOT NULL
                                                                                                                                                                     *                                                                                                                                                                      * resource VARCHAR NOT NULL
                                                                                                                                                                     *                                                                                                                                                                      * action VARCHAR NOT NULL
                                                                                                                                                                     *                                                                                                                                                                      * status VARCHAR NOT NULL
                                                                                                                                                                     *                                                                                                                                                                      * created_at, updated_at, context_data, relations_meta
                                                                                                                                                                     * 35. Role
                                                                                                                                                                     * Tabel Canonic: roles
                                                                                                                                                                     *                                                                                                                                                                      * Câmpuri și Tipuri:
                                                                                                                                                                     * 
                                                                                                                                                                        * id UUID PK
                                                                                                                                                                        *                                                                                                                                                                         * role_code VARCHAR NOT NULL
                                                                                                                                                                        *                                                                                                                                                                         * name VARCHAR NOT NULL
                                                                                                                                                                        *                                                                                                                                                                         * status VARCHAR NOT NULL
                                                                                                                                                                        *                                                                                                                                                                         * created_at, updated_at, context_data, relations_meta
                                                                                                                                                                        * 36. AuditLog
                                                                                                                                                                        * Tabel Canonic: audit_logs (Append-Only)
                                                                                                                                                                        *                                                                                                                                                                         * Câmpuri și Tipuri:
                                                                                                                                                                        * 
                                                                                                                                                                           * id UUID PK
                                                                                                                                                                           *                                                                                                                                                                            * event_id UUID FK $\rightarrow$ events.id NULL
                                                                                                                                                                           *                                                                                                                                                                            * actor_id UUID NULL
                                                                                                                                                                           *                                                                                                                                                                            * actor_type VARCHAR NOT NULL
                                                                                                                                                                           *                                                                                                                                                                            * object_type VARCHAR NOT NULL
                                                                                                                                                                           *                                                                                                                                                                            * object_id UUID NOT NULL
                                                                                                                                                                           *                                                                                                                                                                            * action VARCHAR NOT NULL
                                                                                                                                                                           *                                                                                                                                                                            * timestamp TIMESTAMPTZ NOT NULL
                                                                                                                                                                           *                                                                                                                                                                            * diff_payload JSONB NULL
                                                                                                                                                                           *                                                                                                                                                                            * metadata JSONB NULL
                                                                                                                                                                           * 37. Attachment
                                                                                                                                                                           * Tabel Canonic: attachments
                                                                                                                                                                           *                                                                                                                                                                            * Câmpuri și Tipuri:
                                                                                                                                                                           * 
                                                                                                                                                                              * id UUID PK
                                                                                                                                                                              *                                                                                                                                                                               * owner_id UUID FK $\rightarrow$ users.id NOT NULL
                                                                                                                                                                              *                                                                                                                                                                               * object_type VARCHAR NOT NULL
                                                                                                                                                                              *                                                                                                                                                                               * object_id UUID NOT NULL
                                                                                                                                                                              *                                                                                                                                                                               * file_name VARCHAR NOT NULL
                                                                                                                                                                              *                                                                                                                                                                               * file_type VARCHAR NOT NULL
                                                                                                                                                                              *                                                                                                                                                                               * mime_type VARCHAR NOT NULL
                                                                                                                                                                              *                                                                                                                                                                               * storage_key VARCHAR NOT NULL
                                                                                                                                                                              *                                                                                                                                                                               * file_size BIGINT NOT NULL
                                                                                                                                                                              *                                                                                                                                                                               * status VARCHAR NOT NULL
                                                                                                                                                                              *                                                                                                                                                                               * created_at, updated_at, version, context_data, relations_meta
                                                                                                                                                                              * 38. SystemSetting
                                                                                                                                                                              * Tabel Canonic: system_settings
                                                                                                                                                                              *                                                                                                                                                                               * Câmpuri și Tipuri:
                                                                                                                                                                              * 
                                                                                                                                                                                 * id UUID PK
                                                                                                                                                                                 *                                                                                                                                                                                  * owner_id UUID FK $\rightarrow$ users.id NULL (pentru setări per-user sau globale)
                                                                                                                                                                                 *                                                                                                                                                                                  * setting_key VARCHAR NOT NULL
                                                                                                                                                                                 *                                                                                                                                                                                  * setting_value JSONB NOT NULL
                                                                                                                                                                                 *                                                                                                                                                                                  * status VARCHAR NOT NULL
                                                                                                                                                                                 *                                                                                                                                                                                  * created_at, updated_at, version, context_data, relations_meta
                                                                                                                                                                                 *                                                                                                                                                                                  * Constrângeri: UNIQUE(setting_key) (sau compus cu owner_id dacă setările sunt specifice)
                                                                                                                                                                                 * Status Final DB-BO-001
                                                                                                                                                                                 * Registru 38 / 38 Business Objects: Complet implementat și definit la nivel de schemă persistentă.
                                                                                                                                                                                 *                                                                                                                                                                                  * Status Arhitectural: 🔒 DB-BO-001 ÎNGHEȚAT