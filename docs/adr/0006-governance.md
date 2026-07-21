# ADR 0006: Centralized AI Governance & Capability Engine

## Status
Accepted (Design Phase)

## Context
Pe măsură ce platforma integrează workflow-uri complexe, agenți multipli și consumatori diverși, controlul costurilor, al permisiunilor și al selecției modelului nu mai poate fi lăsat la latitudinea fiecărui modul izolat.

## Decision
Vom implementa un motor centralizat de **AI Governance** care va unifica bugetul, politicile de utilizare, permisiunile, evaluarea capabilităților (`Capability Engine`) și selecția dinamică a providerului (`Provider Selector`), interpus între Runtime-ul aplicației și `UnifiedLLMService`.

## Consequences
- **Pros:** Guvernanță unică la nivel de enterprise, securitate ridicată, auditabilitate completă și flexibilitate maximă în alegerea cost-eficientă a modelelor AI.
- **Cons:** Creșterea complexității inițiale a arhitecturii de rulare a cererilor.
