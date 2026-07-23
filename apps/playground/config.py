import os

class PlaygroundConfig:
    DEFAULT_PROVIDER = "gemini"
    DEFAULT_MODEL = "gemini-2.5-flash"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 1000
    
    MODELS_MAP = {
        "gemini": ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
        "openai": ["gpt-4o-mini", "gpt-4o"],
        "claude": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
    }
