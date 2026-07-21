# ADR 0002: Centralized Prompt Service

## Status
Accepted

## Context
Prompturile folosite în platformă erau inițial împrăștiate prin codul sursă, ceea ce făcea dificilă versiunea, optimizarea și auditarea lor de către utilizator sau echipă.

## Decision
Am creat un `PromptService` dedicat, care gestionează șabloanele de prompt, parametrizarea și randarea lor dintr-un singur loc centralizat.

## Consequences
- **Pros:** Reutilizare ridicată a prompturilor, coerență în tonul agenților și posibilitate facilă de A/B testing sau optimizare ulterioară.
- **Cons:** Un strat suplimentar de abstracție care trebuie administrat odată cu creșterea numărului de funcționalități.
