import time
from typing import List
from src.context.models import ContextRequest, ResolvedContext, ContextDiagnostics
from src.context.protocols import ContextProvider
from src.context.allocator import BudgetAllocator

class ContextResolver:
    def __init__(self, providers: List[ContextProvider]):
        self.providers = providers

    async def resolve(self, request: ContextRequest) -> ResolvedContext:
        start_time = time.time()
        all_fragments = []
        providers_used = []
        providers_dropped = []
        drop_reasons = {}

        for provider in self.providers:
            try:
                fragments = await provider.provide(request)
                if fragments:
                    all_fragments.extend(fragments)
                    providers_used.append(provider.name)
                else:
                    providers_dropped.append(provider.name)
                    drop_reasons[provider.name] = "No fragments returned"
            except Exception as e:
                providers_dropped.append(provider.name)
                drop_reasons[provider.name] = str(e)

        accepted, dropped, total_tokens, tokens_dropped = BudgetAllocator.allocate(
            all_fragments, request.budget
        )

        for d in dropped:
            source_name = d.source_type.value if hasattr(d.source_type, "value") else str(d.source_type)
            if source_name not in drop_reasons:
                drop_reasons[source_name] = "Exceeded token budget"

        system_prompt_parts = []
        messages = []

        for frag in accepted:
            source_val = frag.source_type.value if hasattr(frag.source_type, "value") else str(frag.source_type)
            if source_val == "system_prompt" or source_val == "user_profile":
                system_prompt_parts.append(frag.content)
            else:
                role = "assistant" if source_val == "memory" else "user"
                messages.append({"role": role, "content": frag.content})

        system_prompt = "\n\n".join(system_prompt_parts)
        latency = (time.time() - start_time) * 1000.0

        diagnostics = ContextDiagnostics(
            total_tokens_available=request.budget.max_tokens,
            total_tokens_used=total_tokens,
            tokens_dropped=tokens_dropped,
            tokens_compressed=0,
            providers_used=providers_used,
            providers_dropped=providers_dropped,
            drop_reasons=drop_reasons,
            estimated_cost=round(total_tokens * 0.000002, 6),
            latency_ms=round(latency, 2)
        )

        return ResolvedContext(
            system_prompt=system_prompt,
            messages=messages,
            total_tokens=total_tokens,
            diagnostics=diagnostics
        )
