from __future__ import annotations

import json
from typing import Any, Dict, Type
from pydantic import BaseModel


class StructuredFormatter:
    """Pregătește schema Pydantic pentru cererile trimise către diferiți furnizori LLM."""

    @staticmethod
    def format_openai_response_format(schema_cls: Type[BaseModel]) -> Dict[str, Any]:
        """Returnează configurarea nativă response_format pentru OpenAI (Structured Outputs)."""
        schema_name = schema_cls.__name__
        json_schema = schema_cls.model_json_schema()
        
        return {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": json_schema
            }
        }

    @staticmethod
    def format_claude_system_instruction(schema_cls: Type[BaseModel]) -> str:
        """Generează o instrucțiune de sistem pentru Claude pentru a forța output-ul JSON valid pe schemă."""
        schema_json = json.dumps(schema_cls.model_json_schema(), indent=2)
        instruction = (
            "You must respond ONLY with a valid JSON object that strictly adheres to the following JSON Schema. "
            "Do not include any explanatory text, markdown formatting blocks unless necessary, or extra commentary.\n\n"
            "JSON Schema:\n" + schema_json
        )
        return instruction
