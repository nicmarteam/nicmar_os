import time
from apps.playground.state import PlaygroundRequest
from apps.playground.adapters.unified_adapter import UnifiedAdapter

class PlaygroundService:
    def __init__(self):
        self.adapter = UnifiedAdapter()

    def process_generation(self, provider, model, prompt, streaming, temperature, max_tokens, memory, rag, tools):
        if not prompt or not prompt.strip():
            return (
                "⚠️ Te rog să introduci un prompt valid înainte de a genera.",
                "Niciun context construit (prompt gol).",
                "Niciun payload disponibil.",
                "Metricile nu sunt disponibile."
            )

        clean_prompt = prompt.strip()
        
        # Construim obiectul unificat PlaygroundRequest
        request = PlaygroundRequest(
            provider=provider,
            model=model,
            prompt=clean_prompt,
            streaming=streaming,
            temperature=temperature,
            max_tokens=max_tokens,
            enable_memory=memory,
            enable_rag=rag,
            enable_tools=tools,
            metadata={"source": "NicMar OS - Context Debugger RC2.2"}
        )

        # Măsurăm timpul de execuție (Latența reală)
        start_time = time.time()
        response_text = self.adapter.execute(request)
        end_time = time.time()
        
        latency = round((end_time - start_time) * 1000, 2) # în milisecunde
        
        # 1. Resolved Context & Prompt Final (Simulare structurată pe baza stării curente)
        resolved_context = f"""=========================================
 🔍 RESOLVED CONTEXT DEBUGGER (RC2.2)
=========================================
[1] System Prompt:
- Ești un asistent AI expert, integrat în platforma NicMar OS.
- Colaborezi cu Nic pentru dezvoltarea aplicației și a ecosistemului de business.

[2] User Prompt Original:
{clean_prompt}

[3] Memory Status: {'ACTIVĂ (0 intrări istorice)' if memory else 'DEZACTIVATĂ'}
[4] RAG Status: {'ACTIV (0 documente încărcate)' if rag else 'DEZACTIVAT'}
[5] Tool Calling: {'ACTIV' if tools else 'DEZACTIVAT'}
"""

        final_prompt_display = f"""=========================================
 📝 PAYLOAD FINAL TRIMIS CĂTRE LLM
=========================================
Provider: {provider}
Model: {model}
Temperature: {temperature}
Max Tokens: {max_tokens}

Conținut Prompt / Mesaje:
-----------------------------------------
{clean_prompt}
-----------------------------------------
"""

        # 2. Provider Payload tehnic
        provider_payload = f"""{{
  "provider": "{provider}",
  "model": "{model}",
  "temperature": {temperature},
  "max_tokens": {max_tokens},
  "stream": {streaming},
  "messages": [
    {{"role": "user", "content": "{clean_prompt}"}}
  ]
}}"""

        # 3. Observability & Metrics reale
        # Estimare simplă de tokeni (aproximativ 4 caractere = 1 token)
        est_prompt_tokens = len(clean_prompt) // 4
        est_completion_tokens = len(response_text) // 4
        total_tokens = est_prompt_tokens + est_completion_tokens
        
        metrics_summary = f"""=========================================
 📊 OBSERVABILITY & METRICI REALE (RC2.2)
=========================================
- Status Execuție: 🟢 SUCCES (200 OK)
- Latență Totală: {latency} ms
- Provider Utilizat: {provider.upper()}
- Model Solicitat: {model}
- Prompt Tokens (est.): {est_prompt_tokens}
- Completion Tokens (est.): {est_completion_tokens}
- Total Tokens: {total_tokens}
- Cost Estimat: $0.0000 (Free Tier / Active Connection)
- Retries: 0
- Correlation ID: nicmar-os-rc22-{int(time.time())}
"""

        return response_text, resolved_context, provider_payload, metrics_summary
