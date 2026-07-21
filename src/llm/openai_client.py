from __future__ import annotations

import logging
from typing import Any, Iterable, List, Optional
from openai import OpenAI
from src.llm.base_client import AbstractLLMClient, LLMResponse, LLMStreamChunk
from src.llm.config import LLMConfig
from src.llm.tools.formatters import OpenAIFormatter
from src.llm.tools.mappers import OpenAIMapper
from src.llm.tools.models import ToolResult

logger = logging.getLogger(__name__)


class OpenAIClient(AbstractLLMClient):
    """Client concret pentru integrarea cu API-ul OpenAI, cu suport pentru tool calling."""

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or LLMConfig.get_api_key("openai")
        self.client = OpenAI(api_key=key)

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Any = "auto",
        tool_results: Optional[List[ToolResult]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        target_model = model or LLMConfig.DEFAULT_OPENAI_MODEL

        messages: List[Any] = []
        
        # Dacă avem rezultate anterioare de la tool-uri, construim istoricul de mesaje corespunzător
        if tool_results:
            messages.append({"role": "user", "content": prompt})
            # Aici simulăm/adăugăm mesajul asistentului cu tool_calls anterioare dacă este cazul, 
            # sau adăugăm direct mesajele de tip tool.
            for res in tool_results:
                messages.append(OpenAIMapper.tool_result_to_openai_message(res))
        else:
            messages.append({"role": "user", "content": prompt})

        payload: dict = {
            "model": target_model,
            "messages": messages,
        }

        formatted_tools = OpenAIFormatter.format_tools(tools)
        if formatted_tools:
            payload["tools"] = formatted_tools
            payload["tool_choice"] = OpenAIFormatter.format_tool_choice(tool_choice)

        response = self.client.chat.completions.create(**payload, **kwargs)
        choice = response.choices[0]
        message = choice.message

        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(OpenAIMapper.tool_call_from_openai(tc))

        return LLMResponse(
            content=message.content,
            model=target_model,
            provider="openai",
            tool_calls=tool_calls,
            raw_response=response
        )

    def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Any = "auto",
        **kwargs: Any
    ) -> Iterable[LLMStreamChunk]:
        target_model = model or LLMConfig.DEFAULT_OPENAI_MODEL
        payload: dict = {
            "model": target_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }

        formatted_tools = OpenAIFormatter.format_tools(tools)
        if formatted_tools:
            payload["tools"] = formatted_tools
            payload["tool_choice"] = OpenAIFormatter.format_tool_choice(tool_choice)

        stream_response = self.client.chat.completions.create(**payload, **kwargs)
        for chunk in stream_response:
            delta = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else None
            if delta:
                yield LLMStreamChunk(delta=delta, model=target_model, provider="openai", raw_chunk=chunk)
