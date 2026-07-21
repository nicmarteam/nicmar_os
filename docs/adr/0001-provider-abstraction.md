# ADR 0001: Provider Abstraction & Unified LLM Service

## Status
Accepted

## Context
NicMar OS interacționează cu mai mulți furnizori de modele de limbaj (OpenAI, Anthropic Claude, etc.). Fiecare furnizor are propriul SDK, format de cerere și structură de răspuns. Aveam nevoie de o decuplare completă între codul de business al agenților/workflow-urilor și API-urile specifice fiecărui furnizor.

## Decision
Am implementat un `UnifiedLLMService` sprijinit de un `ProviderRegistry` și o fabrică de provideri (`ProviderFactory`), bazate pe interfețe standardizate (`BaseClient`). Aplicația solicită servicii LLM generice, iar adaptorul intern mapează cererea către furnizorul activ.

## Consequences
- **Pros:** Schimbarea unui model sau adăugarea unuia nou (ex. Gemini) se face fără a modifica codul aplicației. Testarea este simplificată prin mock-uri uniforme.
- **Cons:** Necesită întreținerea unui strat de mapare (mappers) pentru streaming și tool calling pentru fiecare nou furnizor integrat.
