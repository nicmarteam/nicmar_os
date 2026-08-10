# NicMar OS — Master Architecture Document

*Document Type: Core Architecture Master*
*Sursă: NicMar_OS_Core_Architecture_Master.txt (fișier original, fără duplicat)*

---

NICMAR OS – CORE ARCHITECTURE
MASTER ARCHITECTURE DOCUMENT

Document Type: Core Architecture Master
Business Domain: NicMar OS
Architecture Version: 1.0
Status: Master Architecture – Reconstructed and Consolidated
Methodology: Vertical Slicing + Event-Driven Architecture
SSOT Foundations:
- Document 01 – Business Objects
- 5 Fundamental Vertical Slices
- Database Architecture
- Subsequent architecture levels derived sequentially

============================================================
1. PURPOSE
============================================================

Acest document reprezintă harta master a arhitecturii NicMar OS.

Scopul este să păstreze într-un singur document:
- fundația Business Objects;
- cele 5 verticale fundamentale;
- nivelurile de arhitectură construite și planificate;
- ordinea oficială de construcție;
- dependențele dintre niveluri;
- starea actuală a proiectului;
- condiția de închidere a fiecărui nivel.

Principiul central:

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


============================================================
2. NIVELUL 0 – BUSINESS FOUNDATION
============================================================

Document 01 – Business Objects

Status: ÎNCHIS

Definește registrul oficial al celor 38 Business Objects, organizate în 6 domenii:

I. CORE DOMAIN
1. User
2. Profile
3. Identity
4. Partner
5. Client
6. Team
7. Leader

II. RELATIONSHIP DOMAIN
8. Contact
9. Conversation
10. Meeting
11. Presentation
12. FollowUp
13. Objection

III. ACTIVITY DOMAIN
14. Mission
15. Habit
16. Task
17. DailyPlan
18. DailyReview
19. Priority

IV. LEARNING DOMAIN
20. Experience
21. Knowledge
22. Library
23. LearningRecord

V. PERFORMANCE DOMAIN
24. KPI
25. Dashboard
26. DashboardState
27. Score
28. Assessment

VI. SYSTEM DOMAIN
29. Notification
30. Event
31. Workflow
32. Rule
33. Automation
34. Permission
35. Role
36. AuditLog
37. Attachment
38. SystemSetting


============================================================
3. NIVELUL 1 – CORE ARCHITECTURE
============================================================

Cele 5 verticale fundamentale sunt închise.

PILON 1 – CONTACT
SM-CONTACT-001
EVT-CAT-CONTACT-001
Status: ÎNGHEȚAT

PILON 2 – CONVERSATION
SM-CONVERSATION-001
EVT-CAT-CONVERSATION-001
Status: ÎNGHEȚAT

PILON 3 – PARTNER
SM-PARTNER-001
EVT-CAT-PARTNER-001
Status: ÎNGHEȚAT

PILON 4 – CLIENT
SM-CLIENT-001
EVT-CAT-CLIENT-001
Status: ÎNGHEȚAT

PILON 5 – MISSION
SM-MISSION-001
EVT-CAT-MISSION-001
Status: ÎNGHEȚAT

Rezultat:

Business Objects
        ↓
State Machines
        ↓
Event Catalogs
        ↓
5 verticale fundamentale
        ↓
CORE OPERAȚIONAL


============================================================
4. NIVELUL 2 – DATABASE ARCHITECTURE
============================================================

Scop:
Transformarea arhitecturii logice în arhitectura persistentă a datelor.

Motor recomandat:
PostgreSQL

Principiul persistent:

Business Object State
        +
State History
        +
Event Store
        +
AuditLog
        +
KPI / Score Persistence

Documente:

04.1 – DB-ARCH-001
Database Architecture Standard
Status: ÎNGHEȚAT

04.2 – DB-BO-001
Business Object Data Model
Status: ÎNGHEȚAT

04.3 – DB-REL-001
Relationship & Foreign Key Model
Status: definit / în proces de validare

04.4 – DB-STATE-001
State Persistence Model
Status: document derivat

04.5 – DB-EVENT-001
Event Store Model

04.6 – DB-AUDIT-001
AuditLog Model

04.7 – DB-KPI-001
KPI / Score Model

04.8 – Database Integrity Rules

04.9 – Database Indexing Strategy

04.10 – DB-SEC-001
Database Security Model

Condiția de închidere:

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
Database Integrity / Indexing
        ↓
DB-SEC-001
        ↓
DATABASE ARCHITECTURE
100% ÎNCHISĂ


============================================================
5. NIVELUL 3 – EVENT & WORKFLOW ARCHITECTURE
============================================================

Document 05 – Workflow Engine

Documente:
05.1 Workflow Standard
05.2 Workflow Lifecycle
05.3 Workflow Registry
05.4 Workflow Definitions
05.5 Workflow Dependencies
05.6 Workflow Error Handling

Lifecycle standard:
Created
Triggered
Running
Waiting
Completed
Failed
Cancelled

Workflow definition:

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


============================================================
6. NIVELUL 4 – ENGINE ARCHITECTURE
============================================================

Document 06 – Engine Architecture

Relationship Engines:
- RelationshipEngine
- CustomerRelationshipEngine
- PartnerRelationshipEngine

Execution Engines:
- MissionEngine
- FollowUpEngine
- ContinuityEngine

Development Engines:
- HabitEngine
- MentorGuidanceEngine
- LeadershipDevelopmentEngine
- TeamCoordinationEngine

Performance Engines:
- PerformanceEvaluationEngine
- PriorityEngine

Experience Engines:
- ExperienceEngine
- TestimonialEngine

System Engines:
- NotificationEngine
- DashboardEngine

Pentru fiecare Engine se definesc:
- Purpose
- Inputs
- Outputs
- Events consumed
- Events produced
- Business Objects
- Workflows
- Rules
- KPIs
- Dependencies
- Permissions


============================================================
7. NIVELUL 5 – RULES & DECISION ARCHITECTURE
============================================================

Document 07 – Business Rules & Decision Engine

Se definesc:
- Business Rules
- Decision Rules
- Conditions
- Thresholds
- Scoring Rules
- Priority Rules
- Qualification Rules
- Conversion Rules
- Reactivation Rules

Model:

IF
    condiții
THEN
    acțiune / workflow / event


============================================================
8. NIVELUL 6 – KPI & PERFORMANCE ARCHITECTURE
============================================================

Document 08 – KPI & Scoring Engine

Pentru fiecare KPI:
- Definition
- Formula
- Inputs
- Data Source
- Update Trigger
- Calculation Frequency
- Owner Engine
- Storage
- Dashboard Representation

KPI-uri de arhitectură:
- DIS
- CRH
- PDI
- PIP
- OPI
- ERI
- OAS
- LRI
- AMS
- MEI
- TDI
- și ceilalți indicatori confirmați în Business Objects și Engines.


============================================================
9. NIVELUL 7 – IDENTITY, ROLES & SECURITY
============================================================

Document 09 – Identity & Access Architecture

Definește:
- User
- Role
- Permission
- Access Scope
- Ownership
- Authorization
- Audit
- rolurile operaționale NicMar OS


============================================================
10. NIVELUL 8 – NOTIFICATION ARCHITECTURE
============================================================

Document 10 – Notification Engine

Flux:

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


============================================================
11. NIVELUL 9 – API ARCHITECTURE
============================================================

Document 11 – API & Service Architecture

Flux:

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
- endpoint
- input
- output
- authentication
- authorization
- Business Object
- Event
- Engine
- error model


============================================================
12. NIVELUL 10 – AI / AGENT ARCHITECTURE
============================================================

Document 12 – AI & Agent Architecture

Agent Registry planificat:

- Contact Agent
- Conversation Agent
- FollowUp Agent
- Qualification Agent
- Client Agent
- Partner Agent
- Mission Agent
- Content Agent
- Ads Agent
- Performance Agent
- Audit Agent

Pentru fiecare Agent:
- Purpose
- Trigger
- Input
- Knowledge
- Tools
- Decision Rules
- Actions
- Output
- Human Approval
- Audit

Acesta este nivelul în care NicMar OS devine AI-native.


============================================================
13. NIVELUL 11 – APPLICATION ARCHITECTURE
============================================================

Document 13 – Application Architecture

Zone principale:
- Dashboard
- Contacts
- Conversations
- Clients
- Partners
- Missions
- FollowUps
- Meetings
- Presentations
- Experiences
- KPIs
- Reports
- Settings

Fiecare zonă este conectată la API și la motoarele corespunzătoare.


============================================================
14. NIVELUL 12 – UI / UX ARCHITECTURE
============================================================

Document 14 – UI Component System

Componente:
- Cards
- Tables
- Forms
- Timeline
- State indicators
- Event timeline
- KPI cards
- Mission cards
- Contact profile
- Conversation view
- Partner profile
- Client profile
- Dashboard widgets


============================================================
15. NIVELUL 13 – INTEGRATION ARCHITECTURE
============================================================

Document 15 – Integration Architecture

Integrări planificate:
- Facebook
- WhatsApp
- Email
- Calendar
- Zoom
- Forms
- Landing Page
- Analytics

Fiecare integrare este controlată printr-un model standard de integrare.


============================================================
16. NIVELUL 14 – OBSERVABILITY & AUDIT
============================================================

Document 16 – Observability Architecture

Definește:
- System Logs
- Event Logs
- AuditLog
- Engine Logs
- Workflow Logs
- Error Logs
- Performance Metrics
- Health Monitoring


============================================================
17. NIVELUL 15 – TESTING ARCHITECTURE
============================================================

Document 17 – Testing & Validation

Teste:
- Business Object tests
- State Machine tests
- Event tests
- Workflow tests
- Engine tests
- API tests
- Integration tests
- Agent tests
- End-to-end tests


============================================================
18. NIVELUL 16 – DEPLOYMENT & INFRASTRUCTURE
============================================================

Document 18 – Infrastructure Architecture

Definește:
- Development
- Testing
- Production
- Database
- Storage
- Backup
- Security
- Monitoring
- Deployment
- Versioning


============================================================
19. NIVELUL 17 – IMPLEMENTATION ROADMAP
============================================================

Document 19 – NicMar OS Implementation Plan

Ordinea oficială de execuție:

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


============================================================
20. NIVELUL 18 – NICMAR OS OPERATIONAL SYSTEM
============================================================

Rezultatul final:

                 NICMAR OS
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   RELATIONSHIP   EXECUTION    INTELLIGENCE
        │             │             │
   Contact         Mission       AI Agents
   Conversation    FollowUp      Decision
   Partner         Habit         Scoring
   Client          Meeting       Prediction
        │             │             │
        └─────────────┼─────────────┘
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


============================================================
21. ORDINEA OFICIALĂ MASTER
============================================================

ETAPA 0
Document 01 – Business Objects
STATUS: ÎNCHIS

ETAPA 1
5 Verticale Fundamentale
STATUS: ÎNCHIS

ETAPA 2
Document 04 – Database Architecture
STATUS: ÎN CONSTRUCȚIE

ETAPA 3
Document 05 – Workflow Engine
URMEAZĂ

ETAPA 4
Document 06 – Engine Architecture
URMEAZĂ

ETAPA 5
Document 07 – Rules & Decision Engine
URMEAZĂ

ETAPA 6
Document 08 – KPI & Scoring
URMEAZĂ

ETAPA 7
Document 09 – Identity & Security
URMEAZĂ

ETAPA 8
Document 10 – Notification
URMEAZĂ

ETAPA 9
Document 11 – API & Services
URMEAZĂ

ETAPA 10
Document 12 – AI & Agents
URMEAZĂ

ETAPA 11
Document 13 – Application
URMEAZĂ

ETAPA 12
Document 14 – UI / UX
URMEAZĂ

ETAPA 13
Document 15 – Integrations
URMEAZĂ

ETAPA 14
Document 16 – Observability
URMEAZĂ

ETAPA 15
Document 17 – Testing
URMEAZĂ

ETAPA 16
Document 18 – Infrastructure
URMEAZĂ

ETAPA 17
Document 19 – Implementation
URMEAZĂ

ETAPA FINALĂ
NICMAR OS FUNCȚIONAL


============================================================
22. DATABASE ARCHITECTURE – CURRENT CANONICAL STATUS
============================================================

DB-ARCH-001
Database Architecture Standard
STATUS: ÎNGHEȚAT

DB-BO-001
Business Object Data Model
STATUS: ÎNGHEȚAT

DB-REL-001
Relationship & Foreign Key Model
STATUS: DERIVAT

DB-STATE-001
State Persistence Model
STATUS: DERIVAT / PENTRU VALIDARE

DB-EVENT-001
Event Store Model
URMEAZĂ

DB-AUDIT-001
AuditLog Model
URMEAZĂ

DB-KPI-001
KPI & Score Model
URMEAZĂ

DB-INT-001
Database Integrity & Indexing
URMEAZĂ

DB-SEC-001
Database Security Model
URMEAZĂ


============================================================
23. REGISTRUL CANONIC – 38 BUSINESS OBJECTS
============================================================

1. User – users
2. Profile – profiles
3. Identity – identities
4. Partner – partners
5. Client – clients
6. Team – teams
7. Leader – leaders

8. Contact – contacts
9. Conversation – conversations
10. Meeting – meetings
11. Presentation – presentations
12. FollowUp – follow_ups
13. Objection – objections

14. Mission – missions
15. Habit – habits
16. Task – tasks
17. DailyPlan – daily_plans
18. DailyReview – daily_reviews
19. Priority – priorities

20. Experience – experiences
21. Knowledge – knowledge
22. Library – library_items
23. LearningRecord – learning_records

24. KPI – kpis
25. Dashboard – dashboards
26. DashboardState – dashboard_states
27. Score – scores
28. Assessment – assessments

29. Notification – notifications
30. Event – events
31. Workflow – workflows
32. Rule – rules
33. Automation – automations
34. Permission – permissions
35. Role – roles
36. AuditLog – audit_logs
37. Attachment – attachments
38. SystemSetting – system_settings


============================================================
24. ARCHITECTURAL GOVERNANCE
============================================================

Reguli de guvernanță:

1. Documentul 01 este SSOT pentru Business Objects.
2. State Machine este SSOT pentru stările unui Business Object.
3. Event Catalog este SSOT pentru evenimentele oficiale ale verticale.
4. Database Architecture persistă structurile definite de nivelurile anterioare.
5. Workflow-urile orchestrează procesele.
6. Engines execută logica de business.
7. Rules & Decision Layer definește deciziile formale.
8. KPI Layer definește calculul performanței.
9. API Layer expune operațiunile către aplicație.
10. AI / Agent Layer operează în limitele regulilor, permisiunilor și auditului.
11. Integrările externe sunt controlate prin Integration Architecture.
12. Observability, Audit și Security sunt transversale întregului sistem.
13. Fiecare document nou este derivat din SSOT-urile deja înghețate.
14. Terminologia Business Objects și identificatorii canonici rămân stabili pe parcursul construcției.


============================================================
25. CONDIȚIA FINALĂ DE ÎNCHIDERE
============================================================

NicMar OS este considerat arhitectural complet atunci când nivelurile:

Business Foundation
Core Architecture
Database Architecture
Workflow Architecture
Engine Architecture
Rules & Decision Architecture
KPI Architecture
Identity & Security
Notification
API & Services
AI & Agents
Application
UI / UX
Integrations
Observability
Testing
Infrastructure
Implementation

sunt definite, validate, înghețate și conectate prin dependențe explicite.

Rezultatul final:

NICMAR OS
= Business Objects
+ State Machines
+ Events
+ Database
+ Workflows
+ Engines
+ Rules
+ KPI
+ Security
+ API
+ AI Agents
+ Application
+ UI/UX
+ Integrations
+ Observability
+ Testing
+ Infrastructure
+ Implementation


============================================================
26. POZIȚIA ACTUALĂ
============================================================

FOUNDATION
        ↓
38 BUSINESS OBJECTS
        ↓
5 VERTICALE FUNDAMENTALE
        ↓
DATABASE ARCHITECTURE
        ↓
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
WORKFLOW + ENGINE
        ↓
RULES + KPI
        ↓
API + SERVICES
        ↓
AI + AGENTS
        ↓
APPLICATION
        ↓
UI / UX
        ↓
INTEGRATIONS
        ↓
OBSERVABILITY
        ↓
TESTING
        ↓
INFRASTRUCTURE
        ↓
IMPLEMENTATION
        ↓
NICMAR OS


============================================================
END OF MASTER ARCHITECTURE DOCUMENT
============================================================

---

**Notă adăugată — coerență cu Living Vision:**
Deasupra tuturor nivelurilor tehnice descrise în acest document se află `docs/living-vision/00_Manifest_NicMar.md` (de ce există NicMar OS) și `docs/living-vision/01_Caracter_NicMar_OS.md` (cei 5 piloni, cele 4 linii roșii, testul suprem: *"Dacă nu îl ajută pe om, nu îl construim."*). Orice decizie arhitecturală nouă ar trebui verificată față de aceste două documente înainte de a fi înghețată.
