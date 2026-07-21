# ADR 0004: Standardized Tool Registry and Execution Loop

## Status
Accepted

## Context
Agenții din NicMar OS au nevoie să execute acțiuni externe (calcul, căutare, operațiuni de business). Era necesar un mecanism sigur, validat și ușor de extins pentru înregistrarea și apelarea uneltelor de către LLM.

## Decision
Am implementat un `ToolRegistry` centralizat împreună cu un `ExecutorLoop` dedicat care validează schema parametrilor, execută unalta cerută de model și returnează rezultatul structurat înapoi în bucla de conversație.

## Consequences
- **Pros:** Siguranță sporită în execuția codului/funcțiilor, trasabilitate clară și posibilitatea de a adăuga unelte noi printr-un simple decorator sau înregistrare în registry.
- **Cons:** Necesită o atenție deosebită la validarea tipurilor de date transmise de model.
