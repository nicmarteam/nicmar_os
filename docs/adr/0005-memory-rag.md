# ADR 0005: Decoupled Memory and RAG Repositories

## Status
Accepted

## Context
Platforma trebuie să rețină preferințele utilizatorilor și să recupereze cunoștințe specializate (ex. materiale de business, documentație).

## Decision
Am decuplat complet logica de stocare pe termen scurt/lung (Memory) și căutare semantică/documentară (RAG) de nucleul de decizie al contextului, acestea funcționând ca furnizori standardizați prin protocolul de context.

## Consequences
- **Pros:** Flexibilitate maximă în schimbarea motoarelor de căutare sau a bazelor de date utilizate, fără a afecta restul sistemului.
- **Cons:** Necesită sincronizare între fluxurile de scriere în memorie și indexarea RAG.
