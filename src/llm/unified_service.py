from src.llm.provider_factory import ProviderFactory

class UnifiedLLMService:
    def generate(self, prompt, provider="gemini"):
        return ProviderFactory.get_response(prompt, provider)
