from apps.playground.state import PlaygroundRequest
from src.llm.unified_service import UnifiedLLMService
import os

class UnifiedAdapter:
    def __init__(self):
        self.llm_service = UnifiedLLMService()

    def execute(self, request: PlaygroundRequest) -> str:
        """
        Adaptorul oficial care traduce cererea din Playground 
        și o expediază prin UnifiedLLMService către providerul selectat.
        """
        try:
            response = self.llm_service.generate(
                prompt=request.prompt,
                provider=request.provider
            )
            return response
        except Exception as e:
            return f"🔴 Eroare în UnifiedAdapter (Provider: {request.provider}) -> {type(e).__name__}: {e}"
