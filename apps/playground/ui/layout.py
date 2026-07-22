import gradio as gr
from apps.playground.config import PlaygroundConfig
from apps.playground.services.playground_service import PlaygroundService

def create_playground_ui():
    service = PlaygroundService()

    with gr.Blocks(title="NicMar OS - Context Debugger RC2.2") as demo:
        gr.Markdown("# 🚀 NicMar OS - Real Playground & Context Debugger (RC2.2)")
        gr.Markdown("Consola centrală de dezvoltare: vizualizează în timp real contextul, payload-ul și metricile pentru fiecare cerere.")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Configurare Cerere")
                
                provider_dd = gr.Dropdown(
                    choices=list(PlaygroundConfig.MODELS_MAP.keys()),
                    value=PlaygroundConfig.DEFAULT_PROVIDER,
                    label="Provider"
                )
                
                model_dd = gr.Dropdown(
                    choices=PlaygroundConfig.MODELS_MAP[PlaygroundConfig.DEFAULT_PROVIDER],
                    value=PlaygroundConfig.DEFAULT_MODEL,
                    label="Model"
                )

                def update_models(selected_provider):
                    models = PlaygroundConfig.MODELS_MAP.get(selected_provider, [])
                    return gr.update(choices=models, value=models[0] if models else "")

                provider_dd.change(fn=update_models, inputs=provider_dd, outputs=model_dd)

                temperature_slider = gr.Slider(minimum=0.0, maximum=1.0, value=PlaygroundConfig.DEFAULT_TEMPERATURE, step=0.05, label="Temperature")
                max_tokens_slider = gr.Slider(minimum=100, maximum=4000, value=PlaygroundConfig.DEFAULT_MAX_TOKENS, step=100, label="Max Tokens")

                gr.Markdown("### 🧩 Module Active")
                streaming_chk = gr.Checkbox(label="Streaming ON/OFF (Urmează RC2.3)", value=False)
                memory_chk = gr.Checkbox(label="Enable Memory", value=False)
                rag_chk = gr.Checkbox(label="Enable RAG", value=False)
                tools_chk = gr.Checkbox(label="Enable Tool Calling", value=False)

                submit_btn = gr.Button("🚀 Generate & Debug", variant="primary", scale=2)

            with gr.Column(scale=2):
                gr.Markdown("### 💬 Interfață & Consolă de Debugging")
                prompt_box = gr.Textbox(lines=3, label="Prompt / Întrebare", placeholder="Scrie aici mesajul tău (ex: Cine ești?)")
                
                with gr.Tabs():
                    with gr.TabItem("💬 Răspuns Model"):
                        output_box = gr.Textbox(lines=8, label="Rezultat Output Primit")
                        
                    with gr.TabItem("🔍 Resolved Context"):
                        context_box = gr.Textbox(lines=8, label="Context Construit (System, Prompt, Stare)")
                        
                    with gr.TabItem("📦 Provider Payload"):
                        payload_box = gr.Textbox(lines=8, label="Payload tehnic trimis către Provider")
                        
                    with gr.TabItem("📊 Observability & Metrics"):
                        metrics_box = gr.Textbox(lines=8, label="Latență, Tokeni, Cost și Stare Execuție")

        # Legarea evenimentului către cele 4 ieșiri din PlaygroundService
        submit_btn.click(
            fn=service.process_generation,
            inputs=[
                provider_dd,
                model_dd,
                prompt_box,
                streaming_chk,
                temperature_slider,
                max_tokens_slider,
                memory_chk,
                rag_chk,
                tools_chk
            ],
            outputs=[output_box, context_box, payload_box, metrics_box]
        )

    return demo
