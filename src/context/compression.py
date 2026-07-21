from typing import List
from src.context.models import ContextFragment, ContextSourceType

class ContextCompressor:
    @staticmethod
    def compress_fragments(fragments: List[ContextFragment], target_reduction_tokens: int) -> List[ContextFragment]:
        """
        Strategie de compresie: Caută fragmentele de istoric sau memorie cu prioritate mai mică
        și le reduce conținutul sau le aplică un rezumat simplificat pentru a elibera tokeni.
        """
        compressed_fragments = []
        tokens_saved = 0

        for frag in fragments:
            # Comprimăm doar istoricul sau memoria dacă depășim ținta
            if frag.source_type in [ContextSourceType.CONVERSATION_HISTORY, ContextSourceType.MEMORY] and tokens_saved < target_reduction_tokens:
                original_len = len(frag.content)
                # Simulare de compresie/rezumat (păstrăm o fracțiune sau un sumar)
                compressed_content = "[Rezumat/Comprimat]: " + frag.content[:max(50, original_len // 2)]
                estimated_new_tokens = max(10, frag.token_count // 2)
                
                tokens_saved += (frag.token_count - estimated_new_tokens)
                
                # Creăm un fragment nou comprimat
                compressed_frag = ContextFragment(
                    source_type=frag.source_type,
                    content=compressed_content,
                    token_count=estimated_new_tokens,
                    priority=frag.priority,
                    metadata={**frag.metadata, "compressed": True}
                )
                compressed_fragments.append(compressed_frag)
            else:
                compressed_fragments.append(frag)
                
        return compressed_fragments
