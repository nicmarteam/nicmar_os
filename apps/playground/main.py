from apps.playground.ui.layout import create_playground_ui

if __name__ == "__main__":
    app = create_playground_ui()
    # Lansăm interfața în mod local / debug în Colab
    app.launch(inline=True, share=False, debug=True)
