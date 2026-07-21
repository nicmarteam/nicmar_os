from typing import List, Tuple
from src.context.models import ContextFragment, ContextBudget, ContextDiagnostics

class BudgetAllocator:
    @staticmethod
    def allocate(
        fragments: List[ContextFragment], 
        budget: ContextBudget
    ) -> Tuple[List[ContextFragment], List[ContextFragment], int, int]:
        """
        Sortează fragmentele descrescător după prioritate și le adaugă 
        în bucla de buget disponibil (max_tokens minus rezerva pentru output).
        Returnează: (fragmente acceptate, fragmente eliminate, total tokeni folosiți, tokeni eliminați)
        """
        # Sortăm după prioritate (cele mai mari prime)
        sorted_fragments = sorted(fragments, key=lambda f: f.priority, reverse=True)
        
        max_allowed_tokens = budget.max_tokens - budget.output_tokens_reserve
        current_tokens = 0
        accepted: List[ContextFragment] = []
        dropped: List[ContextFragment] = []
        
        for fragment in sorted_fragments:
            if current_tokens + fragment.token_count <= max_allowed_tokens:
                accepted.append(fragment)
                current_tokens += fragment.token_count
            else:
                dropped.append(fragment)
                
        tokens_dropped = sum(f.token_count for f in dropped)
        return accepted, dropped, current_tokens, tokens_dropped
