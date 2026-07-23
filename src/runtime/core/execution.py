import time
import uuid
from typing import Dict, Any, Optional
from src.llm.unified_service import UnifiedLLMService

class ExecutionContext:
    """
    Gestionează starea completă a unei execuții, generând un Trace ID unic,
    urmărind latența, tokenii și contextul injectat.
    """
    def __init__(self, prompt: str, provider: str, model: str, temperature: float, max_tokens: int):
        self.trace_id = f"trace-{uuid.uuid4().hex[:8]}"
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.prompt = prompt
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.start_time = 0.0
        self.end_time = 0.0
        self.latency_ms = 0.0
        
        self.response = ""
        self.status = "PENDING"
        self.error: Optional[str] = None
        
        # Tokeni estimati
        self.prompt_tokens = len(prompt) // 4
        self.completion_tokens = 0
        self.total_tokens = self.prompt_tokens

    def start(self):
        self.start_time = time.time()
        self.status = "RUNNING"

    def finish(self, response: str):
        self.end_time = time.time()
        self.latency_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.response = response
        self.completion_tokens = len(response) // 4
        self.total_tokens = self.prompt_tokens + self.completion_tokens
        self.status = "SUCCESS"

    def fail(self, error_msg: str):
        self.end_time = time.time()
        self.latency_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.error = error_msg
        self.status = "FAILED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "latency_ms": self.latency_ms,
            "status": self.status,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "error": self.error
        }

class RuntimeOrchestrator:
    """
    Motorul intern de execuție care încapsulează apelurile către UnifiedLLMService
    și produce contextul complet de debugging și observație.
    """
    def __init__(self):
        self.llm_service = UnifiedLLMService()

    def run(self, prompt: str, provider: str = "gemini", model: str = "gemini-2.5-flash", 
            temperature: float = 0.7, max_tokens: int = 1000) -> ExecutionContext:
        
        context = ExecutionContext(prompt, provider, model, temperature, max_tokens)
        context.start()
        
        try:
            # Apelul efectiv prin serviciul unificat existent
            result = self.llm_service.generate(prompt=prompt, provider=provider)
            context.finish(result)
        except Exception as e:
            context.fail(str(e))
            
        return context
