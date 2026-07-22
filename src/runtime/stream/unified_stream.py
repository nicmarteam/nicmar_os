import os
from google import genai

class UnifiedStreamService:
    """
    Gestionează streamingul în timp real pentru providerii suportati (Gemini, etc.).
    """
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")

    def stream_generate(self, prompt: str, provider: str = "gemini"):
        if provider == "gemini":
            client = genai.Client(api_key=self.gemini_api_key)
            # Folosim API-ul nativ de streaming al Google GenAI SDK
            response = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        else:
            # Fallback simulat pentru alți provideri până la integrarea completă
            full_text = f"[Streaming Mock pentru {provider}] Răspuns în timp real pentru: {prompt}"
            for word in full_text.split():
                yield word + " "
