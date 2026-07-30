"""
app.py — DataChat SQL Lite
"""

import sys
import os
import streamlit as st
import pandas as pd
 
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

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #334155;
    }

    /* ocultar elementos desnecessários da UI base */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Ocultar controle lateral do sidebar completo */
    [data-testid="collapsedControl"] { display: none; }

    /* Welcome Container Sóbrio */
    .welcome-container {
        text-align: center;
        padding: 4rem 2rem 2rem;
    }
    .welcome-title {
        font-size: 3rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    .welcome-subtitle {
        color: #64748b;
        font-size: 1.125rem;
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
        padding: 0.75rem 1rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .stButton > button:hover {
        border-color: #1e3a8a;
        color: #1e3a8a;
        background-color: #f8fafc;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Chat  */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 2.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.02);
    }

    /* Input Chat */
    [data-testid="stChatInput"] {
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Resposta natural */
    .natural-response {
        font-size: 1.35rem;
        color: #0f172a;
        line-height: 1.6;
        font-weight: 400;
        margin-bottom: 1.25rem;
    }

    /* Indicador de fonte */
    .source-indicator {
        font-size: 0.8rem;
        color: #94a3b8;
        border-top: 1px solid #e2e8f0;
        padding-top: 0.75rem;
        margin-bottom: 1.5rem;
        letter-spacing: 0.01em;
    }
    .source-indicator span {
        font-weight: 600;
        color: #64748b;
    }

    /* Estilização sutil das abas*/
    [data-baseweb="tab-list"] {
        gap: 2rem;
        margin-top: 1rem;
    }
    [data-baseweb="tab"] {
        font-weight: 500;
        color: #64748b;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        color: #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

# callbacks
if "pergunta_input" not in st.session_state:
    st.session_state.pergunta_input = ""

if "auto_consultar" not in st.session_state:
    st.session_state.auto_consultar = False

#historico de consultas
if "historico" not in st.session_state:
    st.session_state.historico = []


def preencher_pergunta(texto: str):
    """Preenche o campo de pergunta E já sinaliza para disparar a consulta automaticamente."""
    st.session_state.pergunta_input = texto
    st.session_state.auto_consultar = True


# funções das explicações em linguagem natural
def _formatar_valor(valor) -> str:
    """Formata números com separador de milhar/decimal em padrão BR, mantém o resto como string."""
    if isinstance(valor, (int, float)):
        try:
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".").rstrip("0").rstrip(",")
        except (ValueError, TypeError):
            return str(valor)
    return str(valor)

def montar_explicacao_generica(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "A consulta foi executada com sucesso, mas não retornou nenhum registro para os critérios informados."

    linhas, colunas = df.shape

    if linhas == 1 and colunas == 1:
        coluna = df.columns[0]
        valor = _formatar_valor(df.iloc[0, 0])
        return f"O resultado da sua consulta é {valor} (referente a {coluna})."

    if linhas == 1:
        pares = [f"{col}: {_formatar_valor(df.iloc[0][col])}" for col in df.columns]
        return "A consulta retornou um único registro, com os seguintes valores — " + "; ".join(pares) + "."

    colunas_texto = ", ".join(f"{c}" for c in df.columns)
    return (
        f"A consulta retornou {linhas} registros, detalhados pelas colunas {colunas_texto}. "
        "Confira a tabela completa abaixo ou o SQL gerado na aba ao lado."
    )


def _explicacao_pedidos_totais(df: pd.DataFrame) -> str:
    valor = _formatar_valor(df.iloc[0, 0])
    return f"Foram encontrados {valor} pedidos na base de dados."


def _explicacao_clientes_unicos(df: pd.DataFrame) -> str:
    valor = _formatar_valor(df.iloc[0, 0])
    return f"A base possui {valor} clientes únicos que realizaram compras."


def _explicacao_categoria_mais_produtos(df: pd.DataFrame) -> str:
    categoria = df.iloc[0, 0]
    total = _formatar_valor(df.iloc[0, 1])
    return f"A categoria com mais produtos é {categoria}, com {total} produtos cadastrados."


def _explicacao_categoria_maior_faturamento(df: pd.DataFrame) -> str:
    categoria = df.iloc[0, 0]
    valor = _formatar_valor(df.iloc[0, 1])
    return f"A categoria com maior faturamento foi {categoria}, com R$ {valor} faturado."


def _explicacao_forma_pagamento(df: pd.DataFrame) -> str:
    tipo = df.iloc[0, 0]
    qtd = _formatar_valor(df.iloc[0, 1])
    return f"A forma de pagamento mais utilizada foi {tipo}, usada em {qtd} transações."


def _explicacao_estados_mais_clientes(df: pd.DataFrame) -> str:
    itens = [f"{row.iloc[0]} ({_formatar_valor(row.iloc[1])})" for _, row in df.head(5).iterrows()]
    return "Os estados com mais clientes são: " + ", ".join(itens) + "."


def _explicacao_faturamento_consolidado(df: pd.DataFrame) -> str:
    valor = _formatar_valor(df.iloc[0, 0])
    return f"O faturamento consolidado da operação é de R$ {valor}."


def _explicacao_cinco_categorias_faturamento(df: pd.DataFrame) -> str:
    itens = [f"{row.iloc[0]} (R$ {_formatar_valor(row.iloc[1])})" for _, row in df.head(5).iterrows()]
    return "As cinco categorias de maior faturamento são: " + ", ".join(itens) + "."


# template de explicação para as consultas
PERGUNTA_TEMPLATES = {
    "Quantos pedidos existem na base?": _explicacao_pedidos_totais,
    "Quantos pedidos foram realizados no total?": _explicacao_pedidos_totais,
    "Quantos clientes únicos realizaram compras?": _explicacao_clientes_unicos,
    "Qual categoria possui mais produtos?": _explicacao_categoria_mais_produtos,
    "Qual categoria teve o maior faturamento?": _explicacao_categoria_maior_faturamento,
    "Qual forma de pagamento é mais utilizada?": _explicacao_forma_pagamento,
    "Quais os cinco estados com mais clientes?": _explicacao_estados_mais_clientes,
    "Qual o faturamento consolidado da operação?": _explicacao_faturamento_consolidado,
    "Quais as cinco categorias de maior faturamento?": _explicacao_cinco_categorias_faturamento,
    "Qual estado possui a maior base de clientes?": _explicacao_estados_mais_clientes,
}


def montar_explicacao(pergunta: str, df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "A consulta foi executada com sucesso, mas não retornou nenhum registro para os critérios informados."

    template = PERGUNTA_TEMPLATES.get(pergunta.strip())
    if template:
        try:
            return template(df)
        except (IndexError, KeyError, TypeError):
            pass  # SQL gerado veio em formato diferente do esperado — usa o fallback genérico

    return montar_explicacao_generica(df)


# area principal
st.markdown("""
    <div class="welcome-container">
        <h1 class="welcome-title">DataChat SQL</h1>
        <p class="welcome-subtitle">Interface analítica executiva. Formule suas consultas de negócio em linguagem natural.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1.5rem;'>Consultas Recomendadas</p>", unsafe_allow_html=True)

exemplos = [
    "Quantos pedidos foram realizados no total?",
    "Qual o faturamento consolidado da operação?",
    "Quais as cinco categorias de maior faturamento?",
    "Qual estado possui a maior base de clientes?",
]

col1, col2 = st.columns(2)
for i, ex in enumerate(exemplos):
    with col1 if i % 2 == 0 else col2:
        st.button(ex, use_container_width=True, on_click=preencher_pergunta, args=[ex], key=f"btn_corp_{i}")

st.markdown("<br><br>", unsafe_allow_html=True)

# campo de entrada
pergunta = st.text_input(
    "Qual a sua pergunta?",
    placeholder="Ex: Qual categoria de produto teve o maior faturamento em 2018?",
    key="pergunta_input",
)

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    btn_consultar = st.button("Consultar 🚀", use_container_width=True, type="primary")

# resultados 
# Dispara a consulta se o botão "consultar" foi clicado OU se um botão de pergunta recomendada foi clicado
disparar_consulta = btn_consultar or st.session_state.auto_consultar
st.session_state.auto_consultar = False  # reseta para não repetir em reruns futuros

if disparar_consulta and pergunta:
    with st.spinner("Interpretando pergunta e gerando SQL..."):
        resultado = process_question(pergunta)

#historico de consultas
    if not resultado.get("erro"):
        st.session_state.historico.append({
            "pergunta": pergunta,
            "sql": resultado.get("sql", ""),
            "resultado": resultado.get("resultado"),
        })

    st.divider()
    st.subheader("Resultados da Consulta")

    if resultado.get("erro"):
        st.error(f"Erro de processamento: {resultado['erro']}")
    else:
        sql_gerado = resultado.get("sql", "")
        df = resultado.get("resultado")

        tab1, tab2, tab3 = st.tabs(["Visualização", "SQL Gerada", "Histórico de Consultas"])

        with tab1:
            explicacao = resultado.get("explicacao") or montar_explicacao(pergunta, df)

            st.markdown(
                f'<div class="natural-response">🗣️ {explicacao}</div>',
                unsafe_allow_html=True,
            )

            sources = extract_sources(sql_gerado)
            if sources:
                source_text = ", ".join(sources)
                st.markdown(
                    f'<div class="source-indicator"><span>Fonte:</span> DuckDB / Olist &mdash; {source_text}</div>',
                    unsafe_allow_html=True,
                )

            if df is not None and not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum dado retornado para esta consulta.")

        with tab2:
            st.markdown("Consulta SQL gerada automaticamente:")
            st.code(sql_gerado, language="sql")

        # adicionando histórico de consultas
        with tab3:
            st.markdown("### Histórico de consultas")

            if st.session_state.historico:

                for i, item in enumerate(
                    reversed(st.session_state.historico), start=1
                ):
                    with st.expander(f"{i}. {item['pergunta']}"):

                        st.markdown("**SQL gerado:**")
                        st.code(item["sql"], language="sql")

                        st.markdown("**Resultado:**")
                        st.dataframe(
                            item["resultado"],
                            hide_index=True,
                            use_container_width=True
                        )

            else:
                st.info("Nenhuma consulta realizada ainda.")

elif disparar_consulta and not pergunta:
    st.warning("Por favor, digite uma pergunta antes de consultar.")