import streamlit as st
import pandas as pd
import time

# Configuração da página
st.set_page_config(
    page_title="DataChat SQL Lite",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização básica opcional
st.markdown("""
<style>
    .sql-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        font-family: monospace;
        margin-bottom: 20px;
    }
    .explanation-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar para configurações e histórico
with st.sidebar:
    st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=50)
    st.title("DataChat SQL")
    st.markdown("Assistente inteligente para explorar o banco Olist usando Linguagem Natural.")
    st.divider()
    
    st.subheader("⚙️ Configurações (Mock)")
    llm_model = st.selectbox("Modelo LLM", ["GPT-4o-mini", "Llama 3 (Ollama)"])
    st.checkbox("Mostrar Histórico de Consultas", value=True)
    
    st.divider()
    st.caption("Desenvolvido para a Semana 1")

# Conteúdo principal
st.title("📊 DataChat SQL Lite")
st.markdown("Faça perguntas sobre as vendas, produtos, clientes e pagamentos (Base Olist).")

# Campo de entrada
pergunta = st.text_input("Qual a sua pergunta?", placeholder="Ex: Qual categoria de produto teve o maior faturamento em 2018?")

col1, col2 = st.columns([1, 5])
with col1:
    btn_consultar = st.button("Consultar 🚀", use_container_width=True, type="primary")

# Área de resultados (simulados)
if btn_consultar and pergunta:
    with st.spinner("Interpretando pergunta e gerando SQL..."):
        time.sleep(1.5) # Simula o delay do LLM
        
    st.divider()
    st.subheader("Resultados da Consulta")
    
    # Abas para organizar a saída
    tab1, tab2 = st.tabs(["Visualização", "SQL Gerada"])
    
    with tab1:
        # Tabela simulada
        mock_data = pd.DataFrame({
            "Categoria": ["Bed & Bath", "Health & Beauty", "Sports & Leisure", "Computers Accessories", "Furniture Decor"],
            "Faturamento (R$)": [2148320.50, 1502400.20, 1200300.90, 1150000.00, 950800.75]
        })
        st.dataframe(mock_data, use_container_width=True, hide_index=True)
        
        # Explicação simulada
        st.markdown(f"""
        <div class="explanation-box">
            <strong>🗣️ Explicação:</strong><br>
            Em resposta à sua pergunta, a categoria com maior faturamento foi <b>Bed & Bath</b>, alcançando mais de R$ 2,1 milhões no período analisado.
        </div>
        """, unsafe_allow_html=True)
        
    with tab2:
        st.markdown("**Consulta SQL gerada automaticamente:**")
        mock_sql = """SELECT 
    p.product_category_name, 
    SUM(oi.price) AS faturamento
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE YEAR(o.order_purchase_timestamp) = 2018
GROUP BY p.product_category_name
ORDER BY faturamento DESC
LIMIT 5;"""
        st.code(mock_sql, language="sql")
        
elif btn_consultar and not pergunta:
    st.warning("Por favor, digite uma pergunta antes de consultar.")
