import os
from google import genai

class ProviderFactory:
    @staticmethod
    def get_response(prompt, provider="gemini"):
        if provider == "openai":
            import openai
            client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        elif provider == "gemini":
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        else:
            raise ValueError(f"Provider necunoscut: {provider}")
