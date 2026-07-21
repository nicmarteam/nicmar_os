import streamlit as st
import time

st.set_page_config(page_title="NicMar Playground", layout="wide")

st.title("🚀 NicMar OS - Playground & Control Center")
st.markdown("Centrul de comandă și observabilitate pentru ecosistemul NicMar.")

# 1. Control Center (Sidebar)
st.sidebar.header("Control Center")
provider = st.sidebar.selectbox("Provider", ["Claude", "OpenAI", "Gemini"])
model = st.sidebar.selectbox("Model", ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
max_tokens = st.sidebar.slider("Max Tokens", 100, 4000, 1000)

st.sidebar.markdown("---")
enable_memory = st.sidebar.checkbox("Memory ON", value=True)
enable_rag = st.sidebar.checkbox("RAG ON", value=True)
enable_eval = st.sidebar.checkbox("Evaluation ON", value=True)

# 2. Workspace / Chat Principal
st.subheader("Workspace")
prompt = st.text_area("Introdu promptul pentru NicMar OS:", "Analizeaza istoricul si gaseste informatii despre produs.")

if st.button("Generează Răspuns"):
    with st.spinner("Se procesează cererea prin NicMar OS Core..."):
        start_time = time.time()
        # Simulim execuția nucleului conectat la logica construită până acum
        time.sleep(1)
        latency = time.time() - start_time
        
        response_text = f"[{provider} / {model}] Am analizat solicitarea ta: '{prompt}'. Sistemul a rulat cu succes folosind Memoria și RAG-ul activate."

    # 3. Afișare Răspuns
    st.success("Execuție finalizată cu succes!")
    st.markdown("### Răspuns:")
    st.write(response_text)

    # 5. Metrics Panel & Inspector
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Latență", value=f"{latency:.2f}s")
    with col2:
        st.metric(label="Tokeni Estimați", value="340 / 150")
    with col3:
        st.metric(label="Evaluation Score", value="0.94" if enable_eval else "N/A")
