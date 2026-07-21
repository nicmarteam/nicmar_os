from __future__ import annotations

import json
import logging
from typing import Any, Type
from pydantic import BaseModel, ValidationError
from src.llm.structured.models import StructuredResponse

logger = logging.getLogger(__name__)


class StructuredOutputValidator:
    """Validează și parsează răspunsul text brut de la LLM într-un model Pydantic tipizat."""

    @staticmethod
    def parse_and_validate(
        raw_content: str,
        schema_cls: Type[BaseModel],
        model: str,
        provider: str,
        raw_response: Any = None
    ) -> StructuredResponse:
        """Parsează JSON-ul din răspuns și îl validează pe schema Pydantic furnizată."""
        if not raw_content:
            raise ValueError("Răspunsul primit de la LLM este gol, nu se poate parsa structura.")

        # Curățăm eventualele blocuri de cod markdown (ex: ```json ... ```)
        cleaned_content = raw_content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]
        cleaned_content = cleaned_content.strip()

        try:
            data_dict = json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            logger.error(f"Eroare la decodarea JSON din răspunsul LLM: {e}. Conținut: {cleaned_content}")
            raise ValueError(f"Răspunsul LLM nu este un JSON valid: {e}") from e

        try:
            parsed_model = schema_cls.model_validate(data_dict)
        except ValidationError as e:
            logger.error(f"Eroare de validare Pydantic pe schema {schema_cls.__name__}: {e}")
            raise ValueError(f"Datele returnate de LLM nu respectă schema Pydantic cerută: {e}") from e

        return StructuredResponse(
            parsed_data=parsed_model,
            raw_content=raw_content,
            model=model,
            provider=provider,
            raw_response=raw_response
        )
