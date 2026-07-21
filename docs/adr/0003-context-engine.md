# ADR 0003: Context Engine & Provider Architecture

## Status
Accepted

## Context
Trimiterea brută a întregului istoric, a memoriei și a documentelor RAG ducea rapid la depășirea ferestrei de context a modelelor, la costuri ridicate și la pierderea relevanței răspunsurilor.

## Decision
Am proiectat un `ContextEngine` modular, bazat pe un protocol (`ContextProvider`), un algoritm strict de alocare a bugetului (`BudgetAllocator`), un orchestrator (`ContextResolver`), strategii de compresie (`ContextCompressor`) și un modul de observabilitate dedicat.

## Consequences
- **Pros:** Control absolut asupra costurilor și a tokenilor trimiși către LLM. Decuplare completă între sursele de date (SQLite, Vector DB, Profil) și modul în care ele sunt asamblate în context.
- **Cons:** Arhitectură mai complexă care necesită configurarea corectă a priorităților pentru fiecare sursă de date.
