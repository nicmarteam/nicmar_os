# ADR 005: Separarea Agent Runtime de Workflow Engine

- **Status:** Acceptat
- **Context:** Agenții autonomi au nevoie de bucle de gândire și planificare (Loop), în timp ce workflow-urile orchestrează pași determinisți.
- Decizie: Crearea a două subsisteme distincte (src/agents și src/workflows).