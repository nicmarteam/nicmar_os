# ADR 004: Pipeline Pattern pentru Context Builder

- **Status:** Acceptat
- **Context:** Diversele surse de context (Memory, RAG, User) riscau să creeze dependențe circulare.
- Decizie: Adoptarea unui Pattern Pipeline cu enrichers independenți.