from __future__ import annotations

import logging
from typing import Any, Iterable, List, Optional
from anthropic import Anthropic
from src.llm.base_client import AbstractLLMClient, LLMResponse, LLMStreamChunk
from src.llm.config import LLMConfig
from src.llm.tools.formatters import ClaudeFormatter
from src.llm.tools.mappers import ClaudeMapper
from src.llm.tools.models import ToolResult

logger = logging.getLogger(__name__)


class ClaudeClient(AbstractLLMClient):
    """Client concret pentru integrarea cu API-ul Anthropic Claude, cu suport pentru tool calling."""

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or LLMConfig.get_api_key("claude")
        self.client = Anthropic(api_key=key)

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        tool_choice: Any = "auto",
        tool_results: Optional[List[ToolResult]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        target_model = model or LLMConfig.DEFAULT_CLAUDE_MODEL

        messages: List[Any] = []
        if tool_results:
            messages.append({"role": "user", "content": prompt})
            for res in tool_results:
                messages.append(ClaudeMapper.tool_result_to_claude_message(res))
        else:
            messages.append({"role": "user", "content": prompt})

        payload: dict = {
            "model": target_model,
            "max_tokens": 1024,
            "messages": messages,
        }

        formatted_tools = ClaudeFormatter.format_tools(tools)
        if formatted_tools:
            payload["tools"] = formatted_tools
            formatted_choice = ClaudeFormatter.format_tool_choice(tool_choice)
            if formatted_choice:
                payload["tool_choice"] = formatted_choice

        response = self.client.messages.create(**payload, **kwargs)

        content_text = None
        tool_calls = []

        for content_block in response.content:
            if content_block.type == "text":
                content_text = content_block.text
            elif content_block.type == "tool_use":
                tool_calls.append(ClaudeMapper.tool_call_from_claude(content_block))

        return LLMResponse(
            content=content_text,
            model=target_model,
            provider="claude",
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
        target_model = model or LLMConfig.DEFAULT_CLAUDE_MODEL
        payload: dict = {
            "model": target_model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }

        formatted_tools = ClaudeFormatter.format_tools(tools)
        if formatted_tools:
            payload["tools"] = formatted_tools
            formatted_choice = ClaudeFormatter.format_tool_choice(tool_choice)
            if formatted_choice:
                payload["tool_choice"] = formatted_choice

        with self.client.messages.stream(**payload, **kwargs) as stream:
            for text in stream.text_stream:
                if text:
                    yield LLMStreamChunk(delta=text, model=target_model, provider="claude", raw_chunk=text)
