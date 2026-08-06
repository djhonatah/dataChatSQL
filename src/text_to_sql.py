import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))

# ─── Configuração do LLM ───────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY não encontrada no .env. "
        "Defina a variável de ambiente GROQ_API_KEY."
    )


LLM_MODEL = "llama-3.3-70b-versatile"


def _get_llm(temperature: float = 0.0) -> ChatGroq:
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=temperature,
        max_tokens=2048,
    )


# ─── Prompt para Geração de SQL ────────────────────────────────────────

SQL_SYSTEM_PROMPT = """Você é um especialista em SQL e DuckDB. Sua tarefa é converter perguntas em linguagem natural para consultas SQL válidas.

REGRAS OBRIGATÓRIAS:
1. Gere APENAS a query SQL, sem explicações, sem markdown, sem ```sql```.
2. Use APENAS as tabelas e colunas listadas no schema abaixo.
3. Use JOINs quando a pergunta envolver dados de múltiplas tabelas.
4. Para datas, use funções do DuckDB: YEAR(), MONTH(), EXTRACT(), etc.
5. Sempre use aliases descritivos (ex: AS faturamento, AS total_pedidos).
6. Limite resultados a 20 linhas com LIMIT quando fizer sentido.
7. Trate valores NULL quando necessário (IS NOT NULL, COALESCE).
8. Para categorias traduzidas, use JOIN com category_translation.
9. NUNCA use SELECT * em produção; selecione apenas colunas necessárias.
10. Use ORDER BY para resultados ordenados.
11. Se a pergunta não tiver absolutamente NENHUMA relação com os dados fornecidos, e-commerce, clientes, pagamentos ou produtos (ex: "Qual a capital do Brasil?", "Me conte uma piada"), responda EXATAMENTE com a string: OFF_TOPIC

SCHEMA DO BANCO DE DADOS:
{schema}
"""

SQL_USER_PROMPT = """Histórico de Conversa Anterior:
{historico}

Pergunta Atual: {pergunta}

Gere a query SQL:"""


SQL_FIX_SYSTEM_PROMPT = """Você é um especialista em SQL e DuckDB.
Sua tarefa é corrigir uma query SQL que falhou ao ser executada.
Gere APENAS a query SQL corrigida, sem explicações, sem markdown.
Use APENAS o schema fornecido.

SCHEMA DO BANCO DE DADOS:
{schema}"""

SQL_FIX_USER_PROMPT = """Pergunta Original: {pergunta}

Query Incorreta:
{wrong_sql}

Erro retornado pelo DuckDB:
{error_msg}

Por favor, forneça apenas a query SQL corrigida que resolve este erro:"""


# ─── Funções Principais ───────────────────────────────────────────────

def generate_sql(pergunta: str, schema_ddl: str, historico: list = None) -> str:
    """
    Gera uma query SQL a partir de uma pergunta em linguagem natural.

    Args:
        pergunta: Pergunta do usuário em linguagem natural.
        schema_ddl: DDL do banco de dados para contexto.
        historico: Lista de dicionários com as interações anteriores.

    Returns:
        String contendo a query SQL gerada.
    """
    llm = _get_llm(temperature=0.0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SQL_SYSTEM_PROMPT),
        ("human", SQL_USER_PROMPT),
    ])

    chain = prompt | llm | StrOutputParser()

    hist_text = "Nenhum histórico recente."
    if historico:
        hist_text = ""
        # Limita as últimas 3 interações para não estourar o limite de tokens do prompt
        for item in historico[-3:]:
            hist_text += f"Usuário: {item['pergunta']}\nSQL Retornado: {item['sql']}\n\n"

    try:
        sql = chain.invoke({
        "schema": schema_ddl,
        "historico": hist_text.strip(),
        "pergunta": pergunta,
        })

    #tratamento de erros
    except Exception as e:
        raise RuntimeError(
            f"Erro ao comunicar com o LLM: {e}"
        )                                               

    # Limpar a resposta 
    sql = sql.strip()
    if sql.startswith("```"):
        lines = sql.split("\n")
        # Remove primeira e última linha 
        lines = [l for l in lines if not l.strip().startswith("```")]
        sql = "\n".join(lines).strip()

    return sql


def fix_sql_error(pergunta: str, schema_ddl: str, wrong_sql: str, error_msg: str) -> str:
    """
    Agente corretor: Pede ao LLM para corrigir uma query que falhou.
    """
    llm = _get_llm(temperature=0.0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SQL_FIX_SYSTEM_PROMPT),
        ("human", SQL_FIX_USER_PROMPT),
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        sql = chain.invoke({
            "schema": schema_ddl,
            "pergunta": pergunta,
            "wrong_sql": wrong_sql,
            "error_msg": error_msg,
        })
    except Exception as e:
        raise RuntimeError(f"Erro ao comunicar com o LLM na correção: {e}")

    sql = sql.strip()
    if sql.startswith("```"):
        lines = sql.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        sql = "\n".join(lines).strip()

    return sql

