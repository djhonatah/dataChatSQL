"""
app.py — DataChat SQL Lite
"""

import sys
import os
import random
import streamlit as st
import pandas as pd
import pandas.api.types as ptypes

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend import process_question

# Mapeamento: tabela no banco -> arquivo CSV original
DB_TABLES = {
    "category_translation": "product_category_name_translation.csv",
    "customers": "olist_customers_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "products": "olist_products_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
}

def extract_sources(sql: str) -> list[str]:
    """Extrai nomes legíveis das tabelas referenciadas no SQL."""
    if not sql:
        return []
    sql_lower = sql.lower()
    return [label for key, label in DB_TABLES.items() if key in sql_lower]

# Configuração da página 
st.set_page_config(
    page_title="DataChat SQL",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS Customizado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .welcome-container {
        text-align: center;
        padding: 2rem 1rem 1rem;
    }
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .welcome-subtitle {
        color: #64748b;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    /* Botões */
    .stButton > button {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
        color: #475569;
        font-weight: 500;
        transition: all 0.2s ease;
        padding: 0.5rem 1rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .stButton > button:hover {
        border-color: #1e3a8a;
        color: #1e3a8a;
        background-color: #f8fafc;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Fonte Indicator */
    .source-indicator {
        font-size: 0.8rem;
        color: #94a3b8;
        border-top: 1px solid #e2e8f0;
        padding-top: 0.5rem;
        margin-top: 1rem;
        letter-spacing: 0.01em;
    }
    .source-indicator span {
        font-weight: 600;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)


# Inicializa estado da sessão para chat
if "messages" not in st.session_state:
    st.session_state.messages = []

if "auto_send" not in st.session_state:
    st.session_state.auto_send = None

# === SIDEBAR: Histórico de Conversas ===
with st.sidebar:
    st.header("🕰️ Histórico do Chat")
    st.markdown("Relembre as perguntas feitas nesta sessão:")
    
    user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
    
    if user_messages:
        for i, msg in enumerate(reversed(user_messages), start=1):
            st.markdown(f"**{i}.** {msg['content']}")
    else:
        st.info("Nenhuma pergunta realizada ainda.")
# =======================================



def _formatar_valor(valor) -> str:
    """Formata números com separador de milhar/decimal em padrão BR."""
    if isinstance(valor, (int, float)):
        try:
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".").rstrip("0").rstrip(",")
        except (ValueError, TypeError):
            return str(valor)
    return str(valor)

def montar_explicacao_generica(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "A consulta foi executada, mas não retornou nenhum registro."

    linhas, colunas = df.shape

    if linhas == 1 and colunas == 1:
        coluna = df.columns[0]
        valor = _formatar_valor(df.iloc[0, 0])
        return f"O resultado é {valor} (referente a {coluna})."

    if linhas == 1:
        pares = [f"{col}: {_formatar_valor(df.iloc[0][col])}" for col in df.columns]
        return "O registro encontrado contém — " + "; ".join(pares) + "."

    colunas_texto = ", ".join(f"{c}" for c in df.columns)
    return f"A consulta retornou {linhas} registros. Detalhados nas colunas: {colunas_texto}."

# Title
st.markdown("""
    <div class="welcome-container">
        <h1 class="welcome-title">DataChat SQL</h1>
        <p class="welcome-subtitle">Faça perguntas sobre a base Olist em linguagem natural.</p>
    </div>
""", unsafe_allow_html=True)


# Renderiza mensagens anteriores
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Renderiza artefatos se for assistente
        if msg["role"] == "assistant":
            # Caso de erro
            if msg.get("erro"):
                st.error(msg["erro"])
            
            # Caso de sucesso com SQL e DF
            df = msg.get("df")
            sql = msg.get("sql")
            
            if sql:
                with st.expander("🛠️ Ver SQL Gerado"):
                    st.code(sql, language="sql")
                    
                sources = extract_sources(sql)
                if sources:
                    st.markdown(f'<div class="source-indicator"><span>Fontes consultadas:</span> {", ".join(sources)}</div>', unsafe_allow_html=True)
            
            if df is not None and not df.empty:
                linhas, colunas = df.shape
                
                # GRÁFICOS DINÂMICOS AUTOMÁTICOS
                if linhas > 1 and colunas >= 2:
                    numeric_cols = [c for c in df.columns if ptypes.is_numeric_dtype(df[c])]
                    categorical_cols = [c for c in df.columns if not ptypes.is_numeric_dtype(df[c])]
                    
                    if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
                        # Pega a primeira categórica pra X e a primeira numérica pra Y
                        x_col = categorical_cols[0]
                        y_col = numeric_cols[0]
                        
                        df_chart = df.head(30).set_index(x_col)[[y_col]]
                        st.markdown(f"**Gráfico: {y_col} por {x_col}**")
                        st.bar_chart(df_chart)
                
                st.markdown("**Tabela de Dados**")
                st.dataframe(df, hide_index=True)


# Sugestões iniciais de perguntas (apenas se não houver mensagens ainda)
if len(st.session_state.messages) == 0:
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase;'>Experimente perguntar:</p>", unsafe_allow_html=True)
    
    perguntas_dinamicas = [
        "Qual o faturamento total por estado?",
        "Quais as cinco categorias de maior faturamento?",
        "Qual estado possui a maior base de clientes?",
        "Qual forma de pagamento é mais utilizada?",
        "Quantos pedidos foram entregues no ano de 2018?",
    ]
    
    col1, col2 = st.columns(2)
    def preencher(texto):
        st.session_state.auto_send = texto
        
    for i, ex in enumerate(perguntas_dinamicas[:4]):
        with col1 if i % 2 == 0 else col2:
            st.button(ex, use_container_width=True, on_click=preencher, args=[ex], key=f"sug_{i}")


# Input do usuário (st.chat_input)
prompt = st.chat_input("Faça uma pergunta sobre os dados...")

# Se o usuário clicou em uma sugestão, substituímos o prompt pelo auto_send
if st.session_state.auto_send:
    prompt = st.session_state.auto_send
    st.session_state.auto_send = None


if prompt:
    # 1. Adiciona e mostra a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Processa e mostra a resposta do assistente
    with st.chat_message("assistant"):
        with st.spinner("Analisando base de dados..."):
            
            # Montar histórico em string para o backend
            history_str = "Histórico:\n"
            # Pega as últimas interações de user e assistant
            for m in st.session_state.messages[-5:-1]:
                if m["role"] == "user":
                    history_str += f"User: {m['content']}\n"
                elif m["role"] == "assistant" and "sql" in m:
                    history_str += f"SQL Anterior: {m['sql']}\n\n"

            # Chama o processamento (que tem self-healing no backend)
            resultado = process_question(prompt, history_str)

        # Monta a resposta a ser salva no state e mostrada
        msg_assistant = {"role": "assistant"}
        
        if resultado.get("erro"):
            msg_assistant["content"] = "Desculpe, ocorreu um problema."
            msg_assistant["erro"] = resultado["erro"]
            st.error(resultado["erro"])
        else:
            sql_gerado = resultado.get("sql", "")
            df = resultado.get("resultado")
            explicacao = resultado.get("explicacao") or montar_explicacao_generica(df)
            
            msg_assistant["content"] = explicacao
            msg_assistant["sql"] = sql_gerado
            msg_assistant["df"] = df
            
            st.markdown(explicacao)
            
            with st.expander("🛠️ Ver SQL Gerado"):
                st.code(sql_gerado, language="sql")
                
            sources = extract_sources(sql_gerado)
            if sources:
                st.markdown(f'<div class="source-indicator"><span>Fontes consultadas:</span> {", ".join(sources)}</div>', unsafe_allow_html=True)
            
            # Gráficos Dinâmicos
            if df is not None and not df.empty:
                linhas, colunas = df.shape
                if linhas > 1 and colunas >= 2:
                    numeric_cols = [c for c in df.columns if ptypes.is_numeric_dtype(df[c])]
                    categorical_cols = [c for c in df.columns if not ptypes.is_numeric_dtype(df[c])]
                    
                    if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
                        x_col = categorical_cols[0]
                        y_col = numeric_cols[0]
                        df_chart = df.head(30).set_index(x_col)[[y_col]]
                        st.markdown(f"**Gráfico: {y_col} por {x_col}**")
                        st.bar_chart(df_chart)

                st.markdown("**Tabela de Dados**")
                st.dataframe(df, hide_index=True)
            else:
                st.info("Nenhum dado encontrado para a consulta.")
        
        # Salva a resposta no histórico da sessão
        st.session_state.messages.append(msg_assistant)