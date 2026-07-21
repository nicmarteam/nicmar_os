import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

class ContextSourceType(str, Enum):
    SYSTEM_PROMPT = "system_prompt"
    USER_PROFILE = "user_profile"
    CONVERSATION_HISTORY = "conversation_history"
    MEMORY = "memory"
    RAG = "rag"

@dataclass
class ContextBudget:
    max_tokens: int
    output_tokens_reserve: int

@dataclass
class ContextFragment:
    source_type: ContextSourceType
    content: str
    token_count: int
    priority: int

@dataclass
class ContextRequest:
    user_id: str
    session_id: str
    query: str
    budget: ContextBudget

@dataclass
class ResolvedContext:
    system_prompt: str
    messages: List[Dict[str, str]]
    total_tokens: int

@runtime_checkable
class ContextProvider(Protocol):
    name: str
    priority: int
    async def provide(self, request: ContextRequest) -> List[ContextFragment]:
        ...

class BudgetAllocator:
    @staticmethod
    def allocate(fragments: List[ContextFragment], budget: ContextBudget) -> List[ContextFragment]:
        sorted_fragments = sorted(fragments, key=lambda f: f.priority, reverse=True)
        current_tokens = 0
        accepted = []

        for f in sorted_fragments:
            if current_tokens + f.token_count <= (budget.max_tokens - budget.output_tokens_reserve):
                accepted.append(f)
                current_tokens += f.token_count
            else:
                break
        return accepted

class UserProfileProvider:
    def __init__(self):
        self.name = "user_profile_provider"
        self.priority = 10

    async def provide(self, request: ContextRequest) -> List[ContextFragment]:
        profile_text = f"Utilizator ID: {request.user_id}. Rol: Lider echipă / Antreprenor. Interesat de scalarea afacerii."
        token_count = len(profile_text) // 4 
        return [
            ContextFragment(
                source_type=ContextSourceType.USER_PROFILE,
                content=profile_text,
                token_count=token_count,
                priority=self.priority
            )
        ]

class ContextResolver:
    def __init__(self, providers: List[Any]):
        self.providers = sorted(providers, key=lambda p: p.priority, reverse=True)

    async def resolve(self, request: ContextRequest) -> ResolvedContext:
        all_fragments = []
        for provider in self.providers:
            fragments = await provider.provide(request)
            if fragments:
                all_fragments.extend(fragments)

        final_fragments = BudgetAllocator.allocate(all_fragments, request.budget)
        total_tokens = sum(f.token_count for f in final_fragments)
        
        system_prompt = "\n\n".join(
            [f.content for f in final_fragments if f.source_type == ContextSourceType.SYSTEM_PROMPT]
        )
        messages = [
            {"role": "user", "content": f.content}
            for f in final_fragments
            if f.source_type != ContextSourceType.SYSTEM_PROMPT
        ]

        return ResolvedContext(
            system_prompt=system_prompt,
            messages=messages,
            total_tokens=total_tokens
        )
