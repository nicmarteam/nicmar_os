from __future__ import annotations

import os


class SecretProvider:
    """Furnizor responsabil cu extragerea sigură a secretelor (API Keys) din mediu."""

    # Mapare directă între numele providerului și variabila sa de mediu standard
    ENV_MAPPING = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GOOGLE_API_KEY",
    }

    @classmethod
    def get_api_key(cls, provider_name: str) -> str:
        """Returnează cheia API pentru providerul specificat sau aruncă eroare dacă lipsește."""
        normalized_name = provider_name.lower()
        env_var = cls.ENV_MAPPING.get(normalized_name)

        if not env_var:
            raise ValueError(f"Providerul '{provider_name}' nu are o cheie de mediu mapată în SecretProvider.")

        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(
                f"Cheia API pentru providerul '{provider_name}' lipsește din mediul de execuție "
                f"(variabila lipsă: {env_var})."
            )

        return api_key
