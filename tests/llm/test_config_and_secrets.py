from __future__ import annotations

import os
import pytest
from unittest.mock import patch

from src.llm.config import ProviderConfig, LLMConfig
from src.llm.secrets import SecretProvider
from src.llm.provider_factory import ProviderFactory


def test_provider_config_and_llm_config():
    config = LLMConfig.default_config()
    assert config.default_provider == "openai"
    
    openai_cfg = config.get_provider_config("openai")
    assert openai_cfg.default_model == "gpt-4o"
    assert openai_cfg.timeout == 30.0

    with pytest.raises(ValueError):
        config.get_provider_config("inexistent")


def test_secret_provider_success():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-123"}):
        key = SecretProvider.get_api_key("openai")
        assert key == "sk-test-123"


def test_secret_provider_missing():
    with patch.dict(os.environ, {}, clear=True):
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
            
        with pytest.raises(ValueError, match="lipsește din mediul de execuție"):
            SecretProvider.get_api_key("openai")


@patch("src.llm.provider_factory.ClaudeClient")
@patch("src.llm.provider_factory.OpenAIClient")
def test_provider_factory_uses_config_and_secrets(mock_openai_client_cls, mock_claude_client_cls):
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "ant-key-999"}):
        client = ProviderFactory.get_client("anthropic")
        
        mock_claude_client_cls.assert_called_once_with(
            api_key="ant-key-999",
            timeout=30.0
        )
