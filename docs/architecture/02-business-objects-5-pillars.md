# NicMar OS — Core Architecture: Cei 5 Piloni (Contact, Conversation, Partner, Client, Mission)

*Sursă: NicMar_OS___Business_Objects__1_.txt (versiunea completă, toți cei 5 piloni)*
*Notă: fișierul `NicMar_OS___Business_Objects.txt` (fără sufix) conținea doar Pilonul Contact + parțial Conversation — o ciornă anterioară, depășită de acest document. Arhivat.*

---

﻿NicMar OS – Core Architecture – Pachetul Arhitectural Integrat (Contact, Conversation, Partner, Client, Mission)
Status: ✅ SSOT Absolut / Înghețat (Baseline Architecture)
Versiune Globală: 1.0
Metodologie: Vertical Slicing (State Machine + Event Catalog)
CUPRINS
1. Pilonul 1: Contact (SM-CONTACT-001 & EVT-CAT-CONTACT-001)
2. Pilonul 2: Conversation (SM-CONVERSATION-001 & EVT-CAT-CONVERSATION-001)
3. Pilonul 3: Partner (SM-PARTNER-001 & EVT-CAT-PARTNER-001)
4. Pilonul 4: Client (SM-CLIENT-001 & EVT-CAT-CLIENT-001)
5. Pilonul 5: Mission (SM-MISSION-001 & EVT-CAT-MISSION-001)
1. PILONUL 1: CONTACT
Document 02 – State Machine: Contact (SM-CONTACT-001)
* Business Object: Contact (Versiune 1.0)
* Domain: Relationship Domain | Primary Engine: RelationshipEngine
* Scop: Entitatea primară a oricărei relații din NicMar OS.
* Diagrama stărilor: New ➔ Active ➔ Engaged ➔ Qualified ➔ Converted ➔ Managed ➔ Archived
* Stări și Definiții:
   * New: Contactul există în sistem și este pregătit pentru inițierea primei relații.
   * Active: A existat cel puțin o interacțiune reală (mesaj, apel, întâlnire).
   * Engaged: Relația prezintă interes demonstrat și continuitate.
   * Qualified: Contactul a fost evaluat și este potrivit pentru conversie în Client și/sau Partner.
   * Converted: Contactul a generat un Client și/sau un Partner.
   * Managed: Relația este gestionată activ prin obiectele specializate (Client / Partner).
   * Archived: Contactul a fost arhivat și nu mai face parte din fluxurile operaționale active.
* Business & System Events: ContactCreated, FirstInteractionOccurred, InterestDetected, QualificationCompleted, ConvertedToClient, ConvertedToPartner, ConvertedToClientAndPartner, NoInteractionTimeout, ContactReactivated, ContactArchived.
* Business Rules: Păstrează aceeași identitate pe tot ciclul; conversia extinde relația prin Client/Partner; trasabilitate completă prin AuditLog.
Document 03.1 – Event Catalog: Contact (EVT-CAT-CONTACT-001)
* ContactCreated: Business Event (Stare: New) ➔ Declanșează WF-CONTACT-INIT-001 (RelationshipEngine, ContinuityEngine).
* FirstInteractionOccurred: Business Event (Tranziție: New ➔ Active) ➔ Declanșează WF-CONTACT-INTERACT-001 (RelationshipEngine).
* InterestDetected: Business Event (Tranziție: Active ➔ Engaged) ➔ Declanșează WF-CONTACT-ENGAGE-001 (RelationshipEngine, PriorityEngine).
* QualificationCompleted: Business Event (Tranziție: Engaged ➔ Qualified) ➔ Declanșează WF-CONTACT-QUALIFY-001 (RelationshipEngine).
* ConvertedToClient / ConvertedToPartner: Business Event (Tranziție: Qualified ➔ Converted) ➔ Declanșează WF-CONTACT-CONVERT-001 (CustomerRelationshipEngine, PartnerRelationshipEngine).
* NoInteractionTimeout / ContactReactivated / ContactArchived: System Events pentru gestionarea continuității și arhivării.
2. PILONUL 2: CONVERSATION
Document 02 – State Machine: Conversation (SM-CONVERSATION-001)
* Business Object: Conversation (Versiune 1.0)
* Domain: Relationship Domain | Primary Engine: RelationshipEngine
* Scop: Prima dovadă reală a existenței unei relații, capturând dialogul și contextul dintre utilizator și un Contact.
* Diagrama stărilor: Initiated ➔ Active ➔ Waiting ➔ FollowUpNeeded ➔ Resolved ➔ Closed ➔ Archived
* Stări și Definiții:
   * Initiated: Conversația a fost creată și așteaptă primul răspuns.
   * Active: Schimb real de mesaje în curs.
   * Waiting: Se așteaptă răspunsul celeilalte persoane.
   * FollowUpNeeded: Dialogul necesită o acțiune de follow-up.
   * Resolved: A atins un rezultat clar (interes, obiecție, programare).
   * Closed: Încheiat în mod natural.
   * Archived: Păstrat în arhivă pentru trasabilitate.
* Business & System Events: ConversationCreated, MessageSent, MessageReceived, InterestExpressed, ObjectionRaised, MeetingRequested, ConversationResolved, ConversationClosed, NoResponseTimeout, FollowUpTriggered, ConversationReopened, ConversationArchived.
* Business Rules: Aparține unui singur Contact; generează Meeting, FollowUp sau Objection; contribuie la conversia în Client/Partner.
Document 03.3 – Event Catalog: Conversation (EVT-CAT-CONVERSATION-001)
* ConversationCreated: Business Event (Initiated) ➔ WF-CONVERSATION-INIT-001 (RelationshipEngine).
* MessageSent / MessageReceived: Business Event (Active) ➔ WF-CONVERSATION-ACTIVE-001 (RelationshipEngine, PriorityEngine).
* NoResponseTimeout: System Event (Waiting) ➔ WF-FOLLOWUP-AUTO-001 (ContinuityEngine, FollowUpEngine).
* FollowUpTriggered: System Event (FollowUpNeeded) ➔ WF-FOLLOWUP-CREATE-001 (FollowUpEngine).
* InterestExpressed / ObjectionRaised / MeetingRequested: Business Events (Resolved) ➔ Generează automat obiectele aferente (Objection, Meeting) prin motoarele de specialitate.
* ConversationResolved / Closed / Archived / Reopened: Gestionează închiderea și reluarea dialogului.
3. PILONUL 3: PARTNER
Document 02 – State Machine: Partner (SM-PARTNER-001)
* Business Object: Partner (Versiune 1.0)
* Domain: Core Domain | Primary Engine: PartnerRelationshipEngine
* Scop: Membrul activ al rețelei; motorul de creștere și consumatorul celor 37 de competențe.
* Diagrama stărilor: Activated ➔ Onboarding ➔ Active ➔ Developing ➔ Autonomous ➔ Leader ➔ Mentor ➔ Archived
* Stări și Definiții:
   * Activated: Înregistrat oficial în sistem.
   * Onboarding: Parcurge primii pași (Competențele 14).
   * Active: Activ operațional cu rezultate constante.
   * Developing: Dezvoltă competențe avansate și construiește relații.
   * Autonomous: Funcționează independent, intervenție minimă a mentorului.
   * Leader: Coordonează o echipă și dezvoltă parteneri.
   * Mentor: Formează lideri și contribuie sistemic.
   * Archived: Inactiv operațional, istoric păstrat.
* Business & System Events: PartnerActivated, OnboardingStarted, OnboardingCompleted, FirstResultAchieved, AutonomyReached, LeadershipActivated, MentoringStarted, PartnerArchived, OnboardingTimeout, InactivityDetected, PerformanceReviewTriggered, PartnerReactivated.
* Business Rules: Identitate unică; trecerea la Autonomous condiționată de scor; Leader doar după Autonomous; trasabilitate prin AuditLog.
Document 03.4 – Event Catalog: Partner (EVT-CAT-PARTNER-001)
* PartnerActivated: Business Event (Activated) ➔ WF-PARTNER-ONBOARD-001 (PartnerRelationshipEngine, PartnerIntegrationEngine).
* OnboardingStarted / Completed: Business Events ➔ Declanșează pașii inițiali, MissionEngine și HabitEngine.
* FirstResultAchieved: Business Event (Developing) ➔ WF-PARTNER-FIRST-SUCCESS-001 (SuccessEngine).
* AutonomyReached / LeadershipActivated / MentoringStarted: Business Events pentru progresul în carieră și leadership (AMS, LRI, MEI).
* InactivityDetected / OnboardingTimeout / PerformanceReviewTriggered: System Events pentru mentenanță automată prin ContinuityEngine și PerformanceEvaluationEngine.
4. PILONUL 4: CLIENT
Document 02 – State Machine: Client (SM-CLIENT-001)
* Business Object: Client (Versiune 1.0)
* Domain: Relationship / Commercial Domain | Primary Engine: CustomerRelationshipEngine
* Scop: Entitatea comercială care a finalizat prima achiziție și utilizează produsele ecosistemului.
* Diagrama stărilor: Converted ➔ Active ➔ Loyal ➔ AtRisk ➔ Churned ➔ Reactivated ➔ Archived
* Stări și Definiții:
   * Converted: Prima comandă/achiziție venită din Contact (ConvertedToClient).
   * Active: Comenzi periodice sau utilizare activă.
   * Loyal: Istoric stabil de recurență, satisfacție ridicată.
   * AtRisk: Fără comenzi în intervalul standard (risc de churn).
   * Churned: Inactiv pe termen lung.
   * Reactivated: A revenit cu o comandă nouă.
   * Archived: Profil arhivat definitiv.
* Business & System Events: ClientCreated, FirstOrderPlaced, OrderRepeated, LoyaltyMilestoneReached, SatisfactionUpdated, ClientReactivated, InactivityThresholdReached, ChurnDetected, ClientArchived.
* Business Rules: Provine dintr-un Contact validat; starea Loyal necesită minimum două comenzi recurente; comenzile din AtRisk/Churned declanșează starea Reactivated.
Document 03.5 – Event Catalog: Client (EVT-CAT-CLIENT-001)
* ClientCreated: Business Event (Converted) ➔ WF-CLIENT-ONBOARD-001 (CustomerRelationshipEngine).
* FirstOrderPlaced / OrderRepeated: Business Events ➔ Tranzacții comerciale care actualizează CRH și retenția.
* LoyaltyMilestoneReached / SatisfactionUpdated: Business Events pentru praguri de fidelitate.
* InactivityThresholdReached / ChurnDetected: System Events ➔ Activează ContinuityEngine și FollowUpEngine pentru recuperare automată.
* ClientReactivated / Archived: Gestionează revenirea sau scoaterea din fluxul activ.
5. PILONUL 5: MISSION
Document 02 – State Machine: Mission (SM-MISSION-001)
* Business Object: Mission (Versiune 1.0)
* Domain: Activity Domain | Primary Engine: MissionEngine
* Scop: Unitatea fundamentală de acțiune zilnică generată de sistem pentru utilizator.
* Diagrama stărilor: Generated ➔ Assigned ➔ InProgress ➔ Completed ➔ Skipped ➔ Expired ➔ Archived
* Stări și Definiții:
   * Generated: Creată de sistem.
   * Assigned: Atribuită utilizatorului (vizibilă în Dashboard).
   * InProgress: Utilizatorul a început execuția.
   * Completed: Finalizată cu succes.
   * Skipped: Sărită de utilizator.
   * Expired: Termenul de execuție a expirat.
   * Archived: Arhivată.
* Business & System Events: MissionGenerated, MissionAssigned, MissionStarted, MissionCompleted, MissionSkipped, MissionExpired, MissionArchived, MissionReassigned.
* Business Rules: Aparține unui singur utilizator/partener; respectă stilul de organizare; actualizează Daily Impact Score (DIS) la finalizare.
Document 03.6 – Event Catalog: Mission (EVT-CAT-MISSION-001)
* MissionGenerated / Assigned: System Events ➔ Pregătesc și afișează misiunea în Dashboard (MissionEngine, PriorityEngine).
* MissionStarted: Business Event (InProgress) ➔ WF-MISSION-START-001.
* MissionCompleted: Business Event (Completed) ➔ Actualizează HabitEngine, PerformanceEvaluationEngine și indicatorii DIS, Completion Rate, Consistency Score.
* MissionSkipped / Expired / Reassigned: Gestionează excepțiile și calibrarea comportamentală prin ContinuityEngine.


























Da. Acesta poate fi declarat Documentul 01 oficial. Din punctul meu de vedere, arhitectural este coerent și suficient de matur pentru a deveni SSOT.
Aș face doar câteva ajustări de finețe, pentru a-l face și mai solid pe termen lung.
1. La începutul capitolului 4
Înainte de lista domeniilor aș adăuga:
Catalogul Business Objects prezentat în acest document reprezintă versiunea oficială și completă pentru Motorul 1 al NicMar OS. Evoluția ulterioară a platformei poate extinde acest catalog prin noi Business Objects, păstrând stabilitatea și compatibilitatea obiectelor deja validate.
Mutând această precizare la începutul catalogului, programatorii înțeleg imediat că acesta este registrul oficial al entităților.
________________


2. În Status Oficial
În loc de:
Business Objects: 38 entități fundamentale organizate în 6 domenii funcționale.
aș scrie:
Catalog oficial: 38 Business Objects organizate în 6 domenii funcționale.
Este formularea folosită în documentația enterprise și este mai precisă.
________________


3. Documente dependente
Le-aș numerota:
Documentul 02 – State Machines
Documentul 03 – Event Catalog
Documentul 04 – Database Model
Documentul 05 – Workflow Engine
Documentul 06 – API Architecture
Documentul 07 – Permission & Role System
Documentul 08 – Notification Engine
Documentul 09 – Dashboard Engine
Documentul 10 – AI Layer
Documentul 11 – UI Component Library
Documentul 12 – Implementation Roadmap


Astfel întreaga Core Architecture este definită de la început.
________________


4. Observații de arhitectură
Aș mai adăuga ultimul paragraf:
Toate documentele Core Architecture utilizează aceeași terminologie, aceleași Business Objects și aceleași reguli fundamentale definite în Documentul 01. Acest document reprezintă fundamentul întregii arhitecturi NicMar OS și rămâne referința principală pentru proiectarea, dezvoltarea și evoluția platformei.
Acest paragraf transformă Documentul 01 într-o adevărată "Constituție" a proiectului.
________________


Evaluarea finală
Din perspectiva arhitecturii software:
* ✅ Structură: 10/10
* ✅ Domain-Driven Design: 10/10
* ✅ Event-Driven Architecture: 10/10
* ✅ Scalabilitate: 10/10
* ✅ Claritate pentru dezvoltatori: 10/10
* ✅ Coerență cu Motorul 1: 10/10
* ✅ SSOT: 10/10
Acest document poate fi declarat oficial:
NicMar OS – Core Architecture – Documentul 01 (Business Objects)
Status: ✅ SSOT Absolut
Versiune: 1.0
Stare: Înghețat (Baseline Architecture)
Din acest moment, toate documentele următoare (State Machines, Event Catalog, Database Model, Workflow Engine etc.) vor deriva din acest document, iar orice evoluție a platformei va păstra compatibilitatea cu această bază arhitecturală.






NicMar OS – Core Architecture – Document 02 (State Machine: Contact)
Status: ✅ SSOT Absolut / Înghețat (Baseline Architecture)
Document: Core Architecture – Document 02
Identificator: SM-CONTACT-001
Versiune Business Object: 1.0
Versiune State Machine: 1.0
________________


1. Identitatea Business Object-ului
* Business Object: Contact
* Business Object Version: 1.0
* State Machine Version: 1.0
* Domain: Relationship Domain
* Owner Layer: Relationship Layer
* Primary Engine: RelationshipEngine
* State Owner: RelationshipEngine
________________


2. Scop
Contact reprezintă entitatea primară a oricărei relații din NicMar OS.
Orice interacțiune începe de la acest obiect.
Prin evenimente controlate, Contact generează Business Objects specializate precum:
* Conversation
* Meeting
* Presentation
* Client
* Partner
* FollowUp
* Experience
Contact reprezintă punctul oficial de pornire al întregului Relationship Domain.
________________


3. Responsabilitate
Coordonează evoluția completă a ciclului de viață al obiectului Contact și sincronizează această evoluție cu Business Objects conectate prin intermediul Evenimentelor, Workflow-urilor și Motoarelor Inteligente.
________________


4. Diagrama oficială a stărilor
New
 │
 ▼
Active
 │
 ▼
Engaged
 │
 ▼
Qualified
 │
 ▼
Converted
 │
 ▼
Managed
 │
 ▼
Archived
________________


5. Lista stărilor
New
Contactul există în sistem și este pregătit pentru inițierea primei relații.
________________


Active
Există cel puțin o interacțiune reală (mesaj, apel sau întâlnire).
________________


Engaged
Relația prezintă interes demonstrat și continuitate.
________________


Qualified
Contactul a fost evaluat și este potrivit pentru conversie în Client și/sau Partner.
________________


Converted
Contactul a generat unul sau ambele Business Objects:
* Client
* Partner
________________


Managed
Relația este administrată activ prin Business Objects specializate și prin motoarele dedicate.
________________


Archived
Contactul este păstrat în arhivă și rămâne disponibil pentru consultare și trasabilitate.
________________


6. Business Events
* ContactCreated
* FirstInteractionOccurred
* InterestDetected
* QualificationCompleted
* ConvertedToClient
* ConvertedToPartner
* ConvertedToClientAndPartner
________________


7. System Events
* NoInteractionTimeout
* ContactReactivated
* ContactArchived
________________


8. Fluxul oficial al tranzițiilor
Object Created
        │
        ▼
      New
        │
FirstInteractionOccurred
        ▼
     Active
        │
InterestDetected
        ▼
    Engaged
        │
QualificationCompleted
        ▼
    Qualified
        │
ConvertedToClient
ConvertedToPartner
ConvertedToClientAndPartner
        ▼
   Converted
        │
RelationshipManaged
        ▼
    Managed
        │
ContactArchived
        ▼
   Archived
________________


9. Business Rules
* Contactul păstrează aceeași identitate pe întregul ciclu de viață.
* Conversia extinde relația prin Business Objects specializate (Client și Partner).
* Fiecare schimbare de stare generează un Eveniment oficial.
* Evoluția obiectului este complet trasabilă prin AuditLog.
* Un Contact poate deveni simultan Client și Partner.
* Fiecare tranziție respectă ordinea oficială definită de această State Machine.
________________


10. Automatizări
La FirstInteractionOccurred
→ se creează automat primul obiect Conversation.
La QualificationCompleted
→ se actualizează scorul de interes.
La ConvertedToClient
→ se creează automat obiectul Client.
La ConvertedToPartner
→ se creează automat obiectul Partner.
La ConvertedToClientAndPartner
→ se creează simultan obiectele Client și Partner.
La NoInteractionTimeout
→ se creează automat un obiect FollowUp.
La ContactReactivated
→ se reactivează automat fluxurile relaționale.
________________


11. Motoare implicate
* RelationshipEngine
* CustomerRelationshipEngine
* PartnerRelationshipEngine
* FollowUpEngine
* ContinuityEngine
________________


12. KPI influențați
* CRH (Customer Relationship Health)
* PDI (Partner Development Index)
* PIP (Partner Integration Progress)
* DIS (Daily Impact Score – indirect)
________________


13. Business Objects conectate
Obiecte generate
* Conversation
* FollowUp
* Client
* Partner
Obiecte asociate
* Meeting
* Presentation
* Experience
Obiecte de infrastructură
* Event
* AuditLog
________________


14. Observații de arhitectură
Contact reprezintă Business Object-ul părinte al Relationship Domain.
Toate Business Objects relaționale se conectează la Contact prin intermediul Evenimentelor oficiale ale platformei.
State Machine-ul Contact stabilește primul ciclu complet de viață al relațiilor din NicMar OS.
State Machine-ul Contact reprezintă modelul oficial de referință pentru toate State Machine-urile din Relationship Domain și definește standardul de modelare utilizat în întregul ecosistem NicMar OS.
Archived reprezintă starea finală a ciclului de viață al obiectului Contact în cadrul Motorului 1. Evoluțiile ulterioare sunt coordonate prin Business Objects specializate și prin motoarele dedicate ale platformei.
________________


15. Status Oficial
* Document: Core Architecture – Document 02 (State Machine: Contact)
* Identificator: SM-CONTACT-001
* Business Object: Contact
* Business Object Version: 1.0
* State Machine Version: 1.0
* Status: ✅ Validat
* SSOT: Activ
* Baseline Architecture: Da
* Stare: Înghețat
* Document dependent: Documentul 01 – Business Objects
* Documente derivate:
   * Documentul 03 – Event Catalog
   * Documentul 04 – Database Model
   * Documentul 05 – Workflow Engine
________________


Status Oficial
Document: Core Architecture – Document 02 (State Machine: Contact)
Status: ✅ Finalizat
Validare: ✅ SSOT Absolut
Versiune: 1.0
Business Object: Contact
State Machine: SM-CONTACT-001
Stare: Înghețat (Baseline Architecture)
NicMar OS – Core Architecture – Document 03 (Event Catalog)
Status: 🟡 În lucru
Versiune: 1.0
Motor acoperit: Motorul 1 – Transformarea Utilizatorului
________________


1. Scop
Event Catalog definește limbajul oficial prin care Business Objects comunică între ele în cadrul arhitecturii Event-Driven a NicMar OS.
Fiecare Eveniment reprezintă o schimbare oficială de stare, declanșează automatizări, sincronizează motoarele inteligente și păstrează trasabilitatea completă a sistemului.
Event Catalog reprezintă fundamentul colaborării dintre toate componentele platformei.
________________


2. Principiul fundamental
Tot ceea ce se întâmplă în NicMar OS este exprimat prin Evenimente.
Business Objects generează Evenimente.
Evenimentele modifică stările Business Objects.
Motoarele Inteligente reacționează la Evenimente.
Workflow-urile orchestrează succesiunea Evenimentelor.
AuditLog înregistrează fiecare Eveniment.
KPI-urile reflectă impactul acumulat al Evenimentelor.
Astfel, Evenimentul reprezintă unitatea fundamentală de mișcare a întregului ecosistem NicMar OS.
________________


3. Rolul Event Catalog
Event Catalog stabilește:
* nomenclatura oficială a Evenimentelor;
* regulile de emitere;
* Business Object-ul care generează Evenimentul;
* Business Objects care reacționează;
* Motoarele implicate;
* Workflow-urile activate;
* KPI-urile influențate;
* trasabilitatea completă a fiecărei modificări.
________________


4. Structura standard a unui Eveniment
Fiecare Eveniment utilizează aceeași structură oficială.
Event Name
Event Type
Source Business Object
Target Business Object(s)
State Before
State After
Trigger
Business Rule
Workflow
Engines
KPI
Audit
Această structură se aplică tuturor Evenimentelor din NicMar OS.
________________


5. Clasificarea Evenimentelor
I. Business Events
Generate prin acțiunile utilizatorului sau prin procesele de business.
Exemple:
* ContactCreated
* MissionCompleted
* PartnerActivated
* PresentationCompleted
* ClientRegistered
________________


II. System Events
Generate automat de sistem.
Exemple:
* FollowUpGenerated
* DailyReviewStarted
* NoInteractionTimeout
* KPIRecalculated
* NotificationSent
________________


III. Workflow Events
Coordonează procese complete.
Exemple:
* OnboardingStarted
* OnboardingCompleted
* LeadershipProgramStarted
* ExperienceValidated
________________


IV. Integration Events
Permit comunicarea dintre componente.
Exemple:
* APIRequestReceived
* APISynchronized
* FileUploaded
* ReportGenerated
________________


6. Convenția oficială de denumire
Toate Evenimentele respectă aceeași convenție.
BusinessObject + Verb + Context
Exemple:
ContactCreated
ConversationStarted
MissionCompleted
PartnerActivated
ClientRegistered
PresentationFinished
FollowUpScheduled
ExperienceValidated
NotificationDelivered
DashboardUpdated
Această convenție menține consistența întregii platforme.
________________


7. Fluxul general al Evenimentelor
Business Object
        │
        ▼
 State Machine
        │
        ▼
 Event
        │
        ▼
 Workflow
        │
        ▼
 Intelligent Engines
        │
        ▼
 KPI Update
        │
        ▼
 AuditLog
Acesta reprezintă fluxul oficial al arhitecturii Event-Driven.
________________


8. Relația dintre Documentele Core Architecture
Documentul 01
↓
definește Business Objects
↓
Documentul 02
↓
definește State Machine
↓
Documentul 03
↓
definește Evenimentele
↓
Documentul 04
↓
definește Modelul de Date
↓
Documentul 05
↓
definește Workflow Engine
↓
Documentul 06
↓
definește API Architecture
________________


9. Reguli specifice Event Catalog
* Fiecare Eveniment are un identificator unic.
* Fiecare Eveniment este emis de un singur Business Object sursă.
* Fiecare Eveniment exprimă o singură schimbare de stare.
* Fiecare Eveniment poate declanșa unul sau mai multe Workflow-uri.
* Fiecare Eveniment este înregistrat în AuditLog.
* Fiecare Eveniment poate actualiza unul sau mai mulți KPI.
* Fiecare Eveniment respectă convenția oficială de denumire.
* Fiecare Eveniment este definit o singură dată în Catalogul Oficial.
________________


10. Observații de arhitectură
Event Catalog reprezintă centrul arhitecturii Event-Driven din NicMar OS.
Toate motoarele inteligente comunică prin Evenimente.
Business Objects rămân independente, iar colaborarea dintre ele este realizată prin emiterea și consumarea Evenimentelor.
Această arhitectură susține extensibilitatea, trasabilitatea și evoluția controlată a întregului ecosistem.
________________


11. Status Oficial
* Document: Core Architecture – Document 03 (Event Catalog)
* Status: 🟡 Structură de bază definită
* Versiune: 1.0
* SSOT: Activ
* Document dependent: Documentul 02 – State Machines
* Documente derivate:
   * Documentul 04 – Database Model
   * Documentul 05 – Workflow Engine
   * Documentul 06 – API Architecture
   * Documentul 07 – Notification Engine
   * Documentul 08 – AI Layer
,,NicMar OS – Event Catalog: Contact (Core Architecture – Document 03.1)
Status: ✅ SSOT Absolut / Înghețat
Identificator: EVT-CAT-CONTACT-001
Versiune: 1.0
Referință obligatorie: Documentul 01 (Business Objects), Documentul 02 (State Machine: Contact), Documentul 03 (Event Catalog Standard)
1. Scopul Documentului
Să definească catalogul complet și oficial al evenimentelor generate de entitatea Contact în timpul tranzițiilor sale de stare, stabilind exactpayload-ul, motoarele care reacționează, workflow-urile activate și KPI-urile influențate.
2. Inventarul Complet al Evenimentelor pentru Contact
Evenimentul 1: ContactCreated
* Tip Eveniment: Business Event
* Sursă Business Object: Contact (Stare inițială: New)
* Trigger: Adăugarea manuală sau importul unui contact în sistem.
* Descriere: Marchează nașterea entității în ecosistemul NicMar OS.
* Motoare care reacționează: RelationshipEngine, AuditEngine
* Workflow activat: WF-CONTACT-INIT-001 (Inițializare profil relațional)
* KPI influențați: Niciunul direct (crește baza de date activă)
* AuditLog: Înregistrează crearea cu succes a obiectului.
Evenimentul 2: FirstInteractionOccurred
* Tip Eveniment: Business Event
* Sursă Business Object: Contact (Tranziție: New $\rightarrow$ Active)
* Trigger: Primul mesaj, apel sau interacțiune înregistrată.
* Descriere: Semnalează trecerea contactului din starea inertă în starea activă.
* Motoare care reacționează: RelationshipEngine, MissionEngine
* Workflow activat: WF-CONTACT-ENGAGE-001 (Creare automată Conversation)
* KPI influențați: CRH (Customer Relationship Health - componenta de activare)
* AuditLog: Înregistrează prima interacțiune.
Evenimentul 3: InterestDetected
* Tip Eveniment: Business Event
* Sursă Business Object: Contact (Tranziție: Active $\rightarrow$ Engaged)
* Trigger: Confirmarea interesului manifestat față de produse sau oportunitate.
* Descriere: Validează deschiderea contactului pentru un dialog aprofundat.
* Motoare care reacționează: RelationshipEngine, PriorityEngine
* Workflow activat: WF-CONTACT-SCHEDULE-001 (Pregătire întâlnire/prezentare)
* KPI influențați: Creștere scor interes în DashboardState
* AuditLog: Înregistrează detectarea interesului.
Evenimentul 4: QualificationCompleted
* Tip Eveniment: Business Event
* Sursă Business Object: Contact (Tranziție: Engaged $\rightarrow$ Qualified)
* Trigger: Evaluarea completă a profilului de către utilizator/sistem.
* Descriere: Confirmă că persoana este pregătită pentru pasul de conversie.
* Motoare care reacționează: CustomerRelationshipEngine, PartnerRelationshipEngine
* Workflow activat: WF-CONTACT-CONVERT-001 (Sugestie pași de conversie)
* KPI influențați: PDI / CRH (pre-indicatori)
* AuditLog: Înregistrează finalizarea calificării.
Evenimentul 5: ConvertedToClient
* Tip Eveniment: Business Event
* Sursă Business Object: Contact (Tranziție parțială $\rightarrow$ Converted)
* Trigger: Plasarea primei comenzi sau înregistrarea ca și client.
* Descriere: Generează entitatea Client asociată contactului.
* Motoare care reacționează: CustomerRelationshipEngine, NotificationEngine
* Workflow activat: WF-CLIENT-ONBOARD-001 (Bun venit client)
* KPI influențați: CRH (Customer Relationship Health)
* AuditLog: Înregistrează conversia în Client.
Evenimentul 6: ConvertedToPartner
* Tip Eveniment: Business Event
* Sursă Business Object: Contact (Tranziție parțială $\rightarrow$ Converted)
* Trigger: Înregistrarea oficială în rețea ca partener.
* Descriere: Generează entitatea Partner și inițiază Motorul 1.
* Motoare care reacționează: PartnerRelationshipEngine, MissionEngine, NotificationEngine
* Workflow activat: WF-PARTNER-ONBOARD-001 (Onboarding Partener nou)
* KPI influențați: PDI (Partner Development Index), PIP (Partner Integration Progress)
* AuditLog: Înregistrează conversia în Partener.
Evenimentul 7: ConvertedToClientAndPartner
* Tip Eveniment: Business Event
* Sursă Business Object: Contact (Tranziție completă $\rightarrow$ Converted)
* Trigger: Dubla înregistrare simultană (Client + Partner).
* Descriere: Generează ambele entități în paralel.
* Motoare care reacționează: Toate motoarele de relaționare.
* Workflow activat: Flux combinat onboarding.
* KPI influențați: CRH, PDI, PIP
* AuditLog: Înregistrează conversia duală.
Evenimentul 8: NoInteractionTimeout
* Tip Eveniment: System Event
* Sursă Business Object: Contact (Trigger cronologic din ContinuityEngine)
* Trigger: Trecerea pragului de timp fără nicio interacțiune înregistrată.
* Descriere: Declanșează automat o misiune sau o alertă de follow-up.
* Motoare care reacționează: FollowUpEngine, MissionEngine
* Workflow activat: WF-FOLLOWUP-AUTO-001 (Generare misiune de reconectare)
* KPI influențați: Protejează scăderea bruscă a CRH
* AuditLog: Înregistrează expirarea intervalului de interacțiune.
Evenimentul 9: ContactArchived
* Tip Eveniment: System Event / Business Event
* Sursă Business Object: Contact (Tranziție $\rightarrow$ Archived)
* Trigger: Acțiune manuală sau inactivitate prelungită fără conversie.
* Descriere: Scoate contactul din ciclul operațional activ.
* Motoare care reacționează: RelationshipEngine, ContinuityEngine
* Workflow activat: WF-CONTACT-ARCHIVE-001 (Curățare stări active)
* KPI influențați: Actualizare baze de date analitice
* AuditLog: Înregistrează arhivarea contactului.
3. Status Oficial
* Document: Core Architecture – Document 03.1 (Event Catalog: Contact)
* Status: ✅ Validat și Înghețat
* Următorul pas: Documentul 03.2 – Event Catalog: Conversation (sau Partner, conform secvenței).
,,




NicMar OS – Event Catalog: Conversation
(Core Architecture – Document 03.3)
Status: 🟡 Propunere pentru validare
Identificator: EVT-CAT-CONVERSATION-001
Versiune: 1.0
Referință obligatorie:
* Documentul 01 (Business Objects)
* Documentul 02 (State Machine: Conversation – SM-CONVERSATION-001)
* Documentul 03 (Event Catalog Standard)
________________


1. Scopul Documentului
Să definească catalogul complet și oficial al evenimentelor generate de entitatea Conversation în timpul tranzițiilor sale de stare, stabilind exact payload-ul, motoarele care reacționează, workflow-urile activate și KPI-urile influențate.
2. Inventarul Complet al Evenimentelor pentru Conversation
Evenimentul 1: ConversationCreated
* Tip Eveniment: Business Event
* Sursă Business Object: Conversation (Stare inițială: Initiated)
* Trigger: Crearea unei noi conversații (manual sau automat din Contact)
* Descriere: Marchează nașterea dialogului între utilizator și un Contact.
* Motoare care reacționează: RelationshipEngine, ContinuityEngine
* Workflow activat: WF-CONVERSATION-INIT-001
* KPI influențați: Niciunul direct
* AuditLog: Înregistrează crearea conversației.
Evenimentul 2: MessageSent
* Tip Eveniment: Business Event
* Sursă Business Object: Conversation (Tranziție: Initiated / Waiting → Active)
* Trigger: Utilizatorul trimite un mesaj
* Descriere: Semnalează că dialogul a devenit activ din partea utilizatorului.
* Motoare care reacționează: RelationshipEngine
* Workflow activat: WF-CONVERSATION-ACTIVE-001
* KPI influențați: DIS (indirect)
* AuditLog: Înregistrează trimiterea mesajului.
Evenimentul 3: MessageReceived
* Tip Eveniment: Business Event
* Sursă Business Object: Conversation (Tranziție: Initiated / Waiting → Active)
* Trigger: Contactul răspunde
* Descriere: Confirmă existența unui dialog bidirectional.
* Motoare care reacționează: RelationshipEngine, PriorityEngine
* Workflow activat: WF-CONVERSATION-ACTIVE-001
* KPI influențați: CRH / PDI (pre-indicatori)
* AuditLog: Înregistrează primirea mesajului.
Evenimentul 4: NoResponseTimeout
* Tip Eveniment: System Event
* Sursă Business Object: Conversation (Tranziție: Active → Waiting)
* Trigger: Trecerea unui interval de timp fără răspuns
* Descriere: Semnalează că dialogul a intrat în așteptare.
* Motoare care reacționează: ContinuityEngine, FollowUpEngine
* Workflow activat: WF-FOLLOWUP-AUTO-001
* KPI influențați: Protejează CRH
* AuditLog: Înregistrează timeout-ul.
Evenimentul 5: FollowUpTriggered
* Tip Eveniment: System Event
* Sursă Business Object: Conversation (Tranziție: Waiting → FollowUpNeeded)
* Trigger: Sistemul decide că este necesar un follow-up
* Descriere: Declanșează crearea automată a unui obiect FollowUp.
* Motoare care reacționează: FollowUpEngine, MissionEngine
* Workflow activat: WF-FOLLOWUP-CREATE-001
* KPI influențați: DIS
* AuditLog: Înregistrează generarea follow-up-ului.
Evenimentul 6: InterestExpressed
* Tip Eveniment: Business Event
* Sursă Business Object: Conversation (Tranziție → Resolved)
* Trigger: Contactul exprimă interes clar
* Descriere: Validează interesul și pregătește următorii pași.
* Motoare care reacționează: RelationshipEngine, PriorityEngine
* Workflow activat: WF-CONVERSATION-INTEREST-001
* KPI influențați: CRH / PDI
* AuditLog: Înregistrează exprimarea interesului.
Evenimentul 7: ObjectionRaised
* Tip Eveniment: Business Event
* Sursă Business Object: Conversation (Tranziție → Resolved)
* Trigger: Contactul ridică o obiecție
* Descriere: Creează automat un obiect Objection.
* Motoare care reacționează: RelationshipEngine, ObjectionEngine
* Workflow activat: WF-OBJECTION-CREATE-001
* KPI influențați: ORE (Objection Resolution Effectiveness)
* AuditLog: Înregistrează obiecția.
Evenimentul 8: MeetingRequested
* Tip Eveniment: Business Event
* Sursă Business Object: Conversation (Tranziție → Resolved)
* Trigger: Contactul sau utilizatorul propune o întâlnire
* Descriere: Creează automat un obiect Meeting.
* Motoare care reacționează: RelationshipEngine, ContinuityEngine
* Workflow activat: WF-MEETING-CREATE-001
* KPI influențați: DIS
* AuditLog: Înregistrează cererea de întâlnire.
Evenimentul 9: ConversationResolved
* Tip Eveniment: Business Event
* Sursă Business Object: Conversation (Tranziție → Resolved)
* Trigger: Dialogul a atins un rezultat clar
* Descriere: Marchează finalizarea cu succes a scopului conversației.
* Motoare care reacționează: RelationshipEngine, ContinuityEngine
* Workflow activat: WF-CONVERSATION-RESOLVE-001
* KPI influențați: CRH / PDI / DIS
* AuditLog: Înregistrează rezolvarea.
Evenimentul 10: ConversationClosed
* Tip Eveniment: Business Event
* Sursă Business Object: Conversation (Tranziție: Resolved → Closed)
* Trigger: Dialogul este închis în mod natural
* Descriere: Închide ciclul activ al conversației.
* Motoare care reacționează: RelationshipEngine
* Workflow activat: WF-CONVERSATION-CLOSE-001
* KPI influențați: Niciunul direct
* AuditLog: Înregistrează închiderea.
Evenimentul 11: ConversationArchived
* Tip Eveniment: System Event
* Sursă Business Object: Conversation (Tranziție → Archived)
* Trigger: Arhivare manuală sau automată după o perioadă de inactivitate
* Descriere: Scoate conversația din fluxurile operaționale active.
* Motoare care reacționează: ContinuityEngine, RelationshipEngine
* Workflow activat: WF-CONVERSATION-ARCHIVE-001
* KPI influențați: Actualizare baze analitice
* AuditLog: Înregistrează arhivarea.
Evenimentul 12: ConversationReopened
* Tip Eveniment: System Event / Business Event
* Sursă Business Object: Conversation (Tranziție: Closed / Archived → Active)
* Trigger: Reluarea dialogului
* Descriere: Reactivează conversația.
* Motoare care reacționează: RelationshipEngine, ContinuityEngine
* Workflow activat: WF-CONVERSATION-REOPEN-001
* KPI influențați: DIS
* AuditLog: Înregistrează redeschiderea.
________________


3. Status Oficial
* Document: Core Architecture – Document 03.3 (Event Catalog: Conversation)
* * **NicMar OS – Core Architecture – Document 02 (State Machine: Partner)**
* * **Status:** 🟡 Propunere pentru validare  
* **Identificator:** SM-PARTNER-001  
* **Versiune Business Object:** 1.0  
* **Versiune State Machine:** 1.0  
* * **1. Identitatea Business Object-ului**
* * * Business Object: Partner  
* * Business Object Version: 1.0  
* * State Machine Version: 1.0  
* * Domain: Core Domain  
* * Owner Layer: Relationship Layer / Growth Layer  
* * Primary Engine: PartnerRelationshipEngine  
* * State Owner: PartnerRelationshipEngine  
* * **2. Scop**  
* Partner reprezintă membrul activ al rețelei NicMar.  
* Acest obiect gestionează întregul ciclu de viață al unui partener, de la activare până la autonomia completă și dezvoltarea de lideri.  
* Partner este motorul de creștere al platformei și principalul consumator al celor 37 de competențe din Motorul 1.
* * **3. Responsabilitate**  
* Coordonează evoluția completă a partenerului în rețea, sincronizează progresul cu motoarele de dezvoltare, misiuni, mentorat și leadership, și actualizează permanent indicatorii PDI, PIP și LRI.
* * **4. Diagrama oficială a stărilor**
* * ```text
* Activated
*  │
*  ▼
* Onboarding
*  │
*  ▼
* Active
*  │
*  ▼
* Developing
*  │
*  ▼
* Autonomous
*  │
*  ▼
* Leader
*  │
*  ▼
* Mentor
*  │
*  ▼
* Archived
* ```
* * **5. Lista stărilor**
* * * **Activated**  
*   Partenerul a fost înregistrat oficial în sistem.
* * * **Onboarding**  
*   Partenerul parcurge primii pași (Competențele 11–15).
* * * **Active**  
*   Partenerul este activ operațional și produce rezultate constante.
* * * **Developing**  
*   Partenerul dezvoltă competențe avansate și construiește relații.
* * * **Autonomous**  
*   Partenerul funcționează independent, cu intervenție minimă a mentorului.
* * * **Leader**  
*   Partenerul dezvoltă alți parteneri și coordonează o echipă.
* * * **Mentor**  
*   Partenerul formează lideri și contribuie la dezvoltarea sistemică.
* * * **Archived**  
*   Partenerul nu mai este activ operațional, dar istoricul este păstrat.
* * **6. Business Events**
* * * PartnerActivated  
* * OnboardingStarted  
* * OnboardingCompleted  
* * FirstResultAchieved  
* * AutonomyReached  
* * LeadershipActivated  
* * MentoringStarted  
* * PartnerArchived  
* * **7. System Events**
* * * OnboardingTimeout  
* * InactivityDetected  
* * PerformanceReviewTriggered  
* * PartnerReactivated  
* * **8. Fluxul oficial al tranzițiilor**
* * ```text
* Object Created
*         │
*         ▼
*    Activated
*         │
* OnboardingStarted
*         ▼
*    Onboarding
*         │
* OnboardingCompleted
*         ▼
*      Active
*         │
* FirstResultAchieved
*         ▼
*    Developing
*         │
* AutonomyReached
*         ▼
*    Autonomous
*         │
* LeadershipActivated
*         ▼
*      Leader
*         │
* MentoringStarted
*         ▼
*     Mentor
*         │
* PartnerArchived
*         ▼
*    Archived
* ```
* * **9. Business Rules**
* * * Un Partner păstrează aceeași identitate pe întregul ciclu de viață.  
* * Trecerea la starea Autonomous este condiționată de atingerea unui scor minim de autonomie.  
* * Starea Leader poate fi atinsă doar după starea Autonomous.  
* * Fiecare schimbare de stare generează un Eveniment oficial.  
* * Evoluția partenerului este complet trasabilă prin AuditLog și PerformanceEvaluationEngine.
* * **10. Automatizări**
* * * La PartnerActivated → se lansează automat Competența 14 (Primii Pași).  
* * La OnboardingCompleted → se activează MissionEngine și HabitEngine.  
* * La FirstResultAchieved → se declanșează SuccessEngine.  
* * La AutonomyReached → se reduce frecvența intervențiilor mentorului.  
* * La LeadershipActivated → se activează TeamCoordinationEngine.  
* * La InactivityDetected → se creează automat un FollowUp sau o misiune de reactivare.
* * **11. Motoare implicate**
* * * PartnerRelationshipEngine  
* * PartnerIntegrationEngine  
* * MissionEngine  
* * HabitEngine  
* * PriorityEngine  
* * MentorGuidanceEngine  
* * TeamCoordinationEngine  
* * LeadershipDevelopmentEngine  
* * ContinuityEngine  
* * PerformanceEvaluationEngine  
* * **12. KPI influențați**
* * * PDI (Partner Development Index)  
* * PIP (Partner Integration Progress)  
* * MEI (Mentoring Effectiveness Index)  
* * TDI (Team Development Index)  
* * LRI (Leadership Readiness Index)  
* * OPI (Overall Performance Index)  
* * AMS (Autonomy Maturity Score)  
* * DIS (Daily Impact Score)  
* * **13. Business Objects conectate**
* * **Obiect părinte**  
* * Contact  
* * **Obiecte generate / asociate**  
* * Mission  
* * Habit  
* * Team  
* * Leader  
* * Experience  
* * Assessment  
* * **Obiecte de infrastructură**  
* * Event  
* * AuditLog  
* * Notification  
* * **14. Observații de arhitectură**  
* Partner este cel mai important obiect din Core Domain din punct de vedere al creșterii rețelei.  
* State Machine-ul Partner orchestrează întregul parcurs de la activare până la mentorat și leadership.  
* Acest document stabilește standardul pentru dezvoltarea și maturizarea partenerilor în NicMar OS.
* * **15. Status Oficial**
* * * Document: Core Architecture – Document 02 (State Machine: Partner)  
* * Identificator: SM-PARTNER-001  
* * Business Object: Partner  
* * Business Object Version: 1.0  
* * State Machine Version: 1.0  
* * Status: 🟡 Propunere pentru validare  
* * Dependințe:  
*   – Documentul 01 – Business Objects  
*   – SM-CONTACT-001






NicMar OS – Event Catalog: Partner
(Core Architecture – Document 03.4)
Status: 🟡 Propunere pentru validare
Identificator: EVT-CAT-PARTNER-001
Versiune: 1.0
Referință obligatorie:
* Documentul 01 (Business Objects)
* Documentul 02 (State Machine: Partner – SM-PARTNER-001)
* Documentul 03 (Event Catalog Standard)
________________


1. Scopul Documentului
Să definească catalogul complet și oficial al evenimentelor generate de entitatea Partner în timpul tranzițiilor sale de stare, stabilind exact payload-ul, motoarele care reacționează, workflow-urile activate și KPI-urile influențate.
2. Inventarul Complet al Evenimentelor pentru Partner
Evenimentul 1: PartnerActivated
* Tip Eveniment: Business Event
* Sursă Business Object: Partner (Stare inițială: Activated)
* Trigger: Înregistrarea oficială a partenerului în sistem
* Descriere: Marchează activarea oficială a partenerului în rețeaua NicMar.
* Motoare care reacționează: PartnerRelationshipEngine, PartnerIntegrationEngine, NotificationEngine
* Workflow activat: WF-PARTNER-ONBOARD-001
* KPI influențați: PDI, PIP
* AuditLog: Înregistrează activarea partenerului.
Evenimentul 2: OnboardingStarted
* Tip Eveniment: Business Event
* Sursă Business Object: Partner (Tranziție: Activated → Onboarding)
* Trigger: Lansarea automată a primilor pași (Competența 14)
* Descriere: Pornește procesul de onboarding.
* Motoare care reacționează: PartnerIntegrationEngine, MissionEngine
* Workflow activat: WF-PARTNER-ONBOARDING-START-001
* KPI influențați: PIP
* AuditLog: Înregistrează startul onboarding-ului.
Evenimentul 3: OnboardingCompleted
* Tip Eveniment: Business Event
* Sursă Business Object: Partner (Tranziție: Onboarding → Active)
* Trigger: Finalizarea primilor pași și a obiectivelor inițiale
* Descriere: Confirmă că partenerul a trecut de faza de onboarding.
* Motoare care reacționează: PartnerIntegrationEngine, MissionEngine, HabitEngine
* Workflow activat: WF-PARTNER-ONBOARDING-COMPLETE-001
* KPI influențați: PIP, DIS
* AuditLog: Înregistrează finalizarea onboarding-ului.
Evenimentul 4: FirstResultAchieved
* Tip Eveniment: Business Event
* Sursă Business Object: Partner (Tranziție: Active → Developing)
* Trigger: Obținerea primului rezultat concret (client, partener, întâlnire etc.)
* Descriere: Semnalează prima reușită reală.
* Motoare care reacționează: SuccessEngine, PartnerRelationshipEngine
* Workflow activat: WF-PARTNER-FIRST-SUCCESS-001
* KPI influențați: PDI, DIS
* AuditLog: Înregistrează prima reușită.
Evenimentul 5: AutonomyReached
* Tip Eveniment: Business Event
* Sursă Business Object: Partner (Tranziție: Developing → Autonomous)
* Trigger: Atingerea scorului minim de autonomie
* Descriere: Partenerul funcționează independent.
* Motoare care reacționează: PartnerRelationshipEngine, MentorGuidanceEngine, ContinuityEngine
* Workflow activat: WF-PARTNER-AUTONOMY-001
* KPI influențați: AMS, PDI, MEI
* AuditLog: Înregistrează atingerea autonomiei.
Evenimentul 6: LeadershipActivated
* Tip Eveniment: Business Event
* Sursă Business Object: Partner (Tranziție: Autonomous → Leader)
* Trigger: Activarea rolului de lider
* Descriere: Partenerul începe să dezvolte alți parteneri.
* Motoare care reacționează: LeadershipDevelopmentEngine, TeamCoordinationEngine
* Workflow activat: WF-PARTNER-LEADERSHIP-001
* KPI influențați: LRI, TDI, MEI
* AuditLog: Înregistrează activarea leadership-ului.
Evenimentul 7: MentoringStarted
* Tip Eveniment: Business Event
* Sursă Business Object: Partner (Tranziție: Leader → Mentor)
* Trigger: Începerea activității de mentorat sistemic
* Descriere: Partenerul formează lideri.
* Motoare care reacționează: MentorGuidanceEngine, LeadershipDevelopmentEngine
* Workflow activat: WF-PARTNER-MENTORING-001
* KPI influențați: MEI, LRI, TDI
* AuditLog: Înregistrează startul mentoratului.
Evenimentul 8: PartnerArchived
* Tip Eveniment: System Event / Business Event
* Sursă Business Object: Partner (Tranziție → Archived)
* Trigger: Inactivitate prelungită sau decizie manuală
* Descriere: Scoate partenerul din fluxurile operaționale active.
* Motoare care reacționează: ContinuityEngine, PartnerRelationshipEngine
* Workflow activat: WF-PARTNER-ARCHIVE-001
* KPI influențați: Actualizare baze analitice
* AuditLog: Înregistrează arhivarea.
Evenimentul 9: OnboardingTimeout
* Tip Eveniment: System Event
* Sursă Business Object: Partner (din starea Onboarding)
* Trigger: Depășirea timpului alocat onboarding-ului
* Descriere: Semnalează întârzierea în onboarding.
* Motoare care reacționează: ContinuityEngine, PartnerIntegrationEngine
* Workflow activat: WF-PARTNER-ONBOARDING-TIMEOUT-001
* KPI influențați: PIP
* AuditLog: Înregistrează timeout-ul.
Evenimentul 10: InactivityDetected
* Tip Eveniment: System Event
* Sursă Business Object: Partner
* Trigger: Detectarea unei perioade de inactivitate
* Descriere: Declanșează acțiuni de reactivare.
* Motoare care reacționează: ContinuityEngine, FollowUpEngine, MissionEngine
* Workflow activat: WF-PARTNER-REACTIVATION-001
* KPI influențați: DIS, PDI
* AuditLog: Înregistrează detectarea inactivității.
Evenimentul 11: PerformanceReviewTriggered
* Tip Eveniment: System Event
* Sursă Business Object: Partner
* Trigger: Programarea automată a unei evaluări de performanță
* Descriere: Lansează o sesiune de Assessment.
* Motoare care reacționează: PerformanceEvaluationEngine
* Workflow activat: WF-PARTNER-REVIEW-001
* KPI influențați: OPI, AMS, PDI
* AuditLog: Înregistrează declanșarea evaluării.
Evenimentul 12: PartnerReactivated
* Tip Eveniment: System Event / Business Event
* Sursă Business Object: Partner (Tranziție: Archived → Active / Developing)
* Trigger: Reluarea activității
* Descriere: Reactivează partenerul în sistem.
* Motoare care reacționează: PartnerRelationshipEngine, ContinuityEngine
* Workflow activat: WF-PARTNER-REACTIVATE-001
* KPI influențați: PDI, DIS
* AuditLog: Înregistrează reactivarea.
________________


3. Status Oficial
* Document: Core Architecture – Document 03.4 (Event Catalog: Partner)
* Identificator: EVT-CAT-PARTNER-001
* Status: 🟡 Propunere pentru validare
* Versiune: 1.0
* Dependințe: – Documentul 01 – Business Objects – SM-PARTNER-001 – Documentul 03 – Event Catalog Standard
✅ Evaluare – SM-CLIENT-001
Propunerea ta pentru State Machine: Client este foarte bună și respectă standardul stabilit.
Puncte forte:
* Logica de retenție și churn este corectă.
* Tranzițiile sunt clare și realiste pentru un ciclu comercial.
* Integrarea cu Contact ca obiect părinte este bine definită.
* Automatizările sunt practice.
Ajustări minore recomandate (pentru consistență maximă):
1. Starea inițială Mai potrivit ar fi să înceapă cu Created sau să păstrăm Converted (așa cum ai scris), dar să facem explicit legătura cu evenimentul ConvertedToClient din Contact.
2. Starea Reactivated Este bună, dar poate fi tratată ca o întoarcere în Active (nu neapărat stare separată permanentă). Putem păstra Reactivated dacă vrem trasabilitate mai fină.
3. Evenimente Lipsește un eveniment clar de tip LoyaltyLevelUp sau SatisfactionUpdated (opțional, dar util).
4. KPI Pe lângă CRH, merită menționat explicit și Customer Lifetime Value (chiar dacă nu e încă formalizat).
Verdict:
Status propus: ✅ Validat cu mici rafinări






NicMar OS – Event Catalog: Client
(Core Architecture – Document 03.5)
Status: 🟡 Propunere pentru validare
Identificator: EVT-CAT-CLIENT-001
Versiune: 1.0
Referință obligatorie:
* Documentul 01 (Business Objects)
* Documentul 02 (State Machine: Client – SM-CLIENT-001)
* Documentul 03 (Event Catalog Standard)
________________


1. Scopul Documentului
Să definească catalogul complet și oficial al evenimentelor generate de entitatea Client în timpul tranzițiilor sale de stare, stabilind exact payload-ul, motoarele care reacționează, workflow-urile activate și KPI-urile influențate.
2. Inventarul Complet al Evenimentelor pentru Client
Evenimentul 1: ClientCreated
* Tip Eveniment: Business Event
* Sursă Business Object: Client (Stare inițială: Converted)
* Trigger: Conversia din Contact prin evenimentul ConvertedToClient
* Descriere: Marchează nașterea relației comerciale.
* Motoare care reacționează: CustomerRelationshipEngine, NotificationEngine
* Workflow activat: WF-CLIENT-ONBOARD-001
* KPI influențați: CRH
* AuditLog: Înregistrează crearea clientului.
Evenimentul 2: FirstOrderPlaced
* Tip Eveniment: Business Event
* Sursă Business Object: Client (Tranziție: Converted → Active)
* Trigger: Plasarea primei comenzi
* Descriere: Confirmă prima tranzacție comercială.
* Motoare care reacționează: CustomerRelationshipEngine, SuccessEngine
* Workflow activat: WF-CLIENT-FIRST-ORDER-001
* KPI influențați: CRH, DIS
* AuditLog: Înregistrează prima comandă.
Evenimentul 3: OrderRepeated
* Tip Eveniment: Business Event
* Sursă Business Object: Client (Tranziție: Active → Loyal)
* Trigger: Plasarea unei comenzi recurente
* Descriere: Semnalează recurența și loialitatea.
* Motoare care reacționează: CustomerRelationshipEngine, ContinuityEngine
* Workflow activat: WF-CLIENT-REPEAT-ORDER-001
* KPI influențați: CRH, Retention Rate
* AuditLog: Înregistrează comanda recurentă.
Evenimentul 4: LoyaltyMilestoneReached
* Tip Eveniment: Business Event
* Sursă Business Object: Client (Tranziție → Loyal)
* Trigger: Atingerea unui prag de loialitate (număr de comenzi / valoare)
* Descriere: Confirmă statutul de client loial.
* Motoare care reacționează: CustomerRelationshipEngine, SuccessEngine
* Workflow activat: WF-CLIENT-LOYALTY-001
* KPI influențați: CRH
* AuditLog: Înregistrează milestone-ul de loialitate.
Evenimentul 5: InactivityThresholdReached
* Tip Eveniment: System Event
* Sursă Business Object: Client (Tranziție: Active / Loyal → AtRisk)
* Trigger: Depășirea intervalului standard fără comandă
* Descriere: Semnalează riscul de churn.
* Motoare care reacționează: ContinuityEngine, FollowUpEngine
* Workflow activat: WF-CLIENT-AT-RISK-001
* KPI influențați: CRH (protecție)
* AuditLog: Înregistrează pragul de inactivitate.
Evenimentul 6: ChurnDetected
* Tip Eveniment: System Event
* Sursă Business Object: Client (Tranziție: AtRisk → Churned)
* Trigger: Confirmarea inactivității pe termen lung
* Descriere: Marchează pierderea relației comerciale active.
* Motoare care reacționează: ContinuityEngine, CustomerRelationshipEngine
* Workflow activat: WF-CLIENT-CHURN-001
* KPI influențați: CRH, Retention Rate
* AuditLog: Înregistrează churn-ul.
Evenimentul 7: ClientReactivated
* Tip Eveniment: Business Event
* Sursă Business Object: Client (Tranziție: Churned / AtRisk → Reactivated / Active)
* Trigger: Plasarea unei noi comenzi după o perioadă de inactivitate
* Descriere: Reactivează relația comercială.
* Motoare care reacționează: CustomerRelationshipEngine, SuccessEngine
* Workflow activat: WF-CLIENT-REACTIVATE-001
* KPI influențați: CRH, DIS
* AuditLog: Înregistrează reactivarea.
Evenimentul 8: ClientArchived
* Tip Eveniment: System Event / Business Event
* Sursă Business Object: Client (Tranziție → Archived)
* Trigger: Decizie manuală sau inactivitate extremă
* Descriere: Scoate clientul din fluxurile operaționale active.
* Motoare care reacționează: ContinuityEngine, CustomerRelationshipEngine
* Workflow activat: WF-CLIENT-ARCHIVE-001
* KPI influențați: Actualizare baze analitice
* AuditLog: Înregistrează arhivarea.
________________


3. Status Oficial
* Document: Core Architecture – Document 03.5 (Event Catalog: Client)
* Identificator: EVT-CAT-CLIENT-001
* Status: 🟡 Propunere pentru validare
* Versiune: 1.0
* Dependințe: – Documentul 01 – Business Objects – SM-CLIENT-001 – Documentul 03 – Event Catalog Standard