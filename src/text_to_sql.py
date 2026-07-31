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
    """Retorna uma instância do LLM Groq configurada."""
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=temperature,
        max_tokens=2048,
    )

def _get_data_dictionary() -> str:
    """Lê o dicionário de dados caso exista."""
    dict_path = os.path.join(_PROJECT_ROOT, "data", "data_dictionary.md")
    if os.path.exists(dict_path):
        with open(dict_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# ─── Prompt para Geração de SQL ────────────────────────────────────────

SQL_SYSTEM_PROMPT = """Você é um especialista em SQL e DuckDB. Sua tarefa é converter perguntas em linguagem natural para consultas SQL válidas.

REGRAS OBRIGATÓRIAS:
1. Gere APENAS a query SQL, sem explicações, sem markdown, sem ```sql```.
2. Use APENAS as tabelas e colunas listadas no schema abaixo.
3. Use JOINs quando a pergunta envolver dados de múltiplas tabelas.
4. Para datas, use funções do DuckDB: YEAR(), MONTH(), EXTRACT(), etc.
5. Sempre use aliases descritivos (ex: AS faturamento, AS total_pedidos).
6. Limite resultados a 20 linhas com LIMIT quando fizer sentido (a não ser que seja um valor agregado).
7. Trate valores NULL quando necessário (IS NOT NULL, COALESCE).
8. Para categorias traduzidas, use JOIN com category_translation.
9. NUNCA use SELECT * em produção; selecione apenas colunas necessárias.
10. Use ORDER BY para resultados ordenados.
11. Se a pergunta não tiver absolutamente NENHUMA relação com os dados fornecidos, e-commerce, clientes, pagamentos ou produtos (ex: "Qual a capital do Brasil?", "Me conte uma piada"), responda EXATAMENTE com a string: OFF_TOPIC
12. (Desafio Extra) O usuário pode fazer perguntas com base no HISTÓRICO da conversa (ex: "E em 2018?"). Utilize o histórico para entender o contexto.
13. (Desafio Extra) Sinta-se livre para usar subconsultas (subqueries) e CTEs (WITH) para responder perguntas analíticas complexas.

SCHEMA DO BANCO DE DADOS:
{schema}

DICIONÁRIO DE DADOS (Regras de Negócio / Domínio):
{dictionary}

HISTÓRICO DA CONVERSA:
{history}
"""

SQL_USER_PROMPT = """Pergunta: {pergunta}

Gere a query SQL:"""


FIX_SQL_SYSTEM_PROMPT = """Você é um especialista em DuckDB. A query SQL anterior que você gerou falhou ao ser executada.
Corrija o erro e devolva APENAS o código SQL, sem explicações, sem markdown.

SCHEMA DO BANCO DE DADOS:
{schema}

DICIONÁRIO DE DADOS:
{dictionary}
"""

FIX_SQL_USER_PROMPT = """Query SQL original:
{sql}

Erro retornado pelo banco de dados:
{error}

Corrija a query para DuckDB e retorne APENAS o SQL válido:"""


# ─── Funções Principais ───────────────────────────────────────────────

def _clean_sql(sql: str) -> str:
    sql = sql.strip()
    if sql.startswith("```"):
        lines = sql.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        sql = "\n".join(lines).strip()
    return sql

def generate_sql(pergunta: str, schema_ddl: str, history: str = "") -> str:
    """
    Gera uma query SQL a partir de uma pergunta em linguagem natural, considerando histórico.
    """
    llm = _get_llm(temperature=0.0)
    dictionary = _get_data_dictionary()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SQL_SYSTEM_PROMPT),
        ("human", SQL_USER_PROMPT),
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        sql = chain.invoke({
            "schema": schema_ddl,
            "dictionary": dictionary,
            "history": history,
            "pergunta": pergunta,
        })
    except Exception as e:
        raise RuntimeError(f"Erro ao comunicar com o LLM: {e}")

    return _clean_sql(sql)

def fix_sql(sql_errada: str, erro_db: str, schema_ddl: str) -> str:
    """
    Tenta corrigir um SQL que falhou usando o LLM (Agente Autocorreção).
    """
    llm = _get_llm(temperature=0.0)
    dictionary = _get_data_dictionary()

    prompt = ChatPromptTemplate.from_messages([
        ("system", FIX_SQL_SYSTEM_PROMPT),
        ("human", FIX_SQL_USER_PROMPT),
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        sql_fixed = chain.invoke({
            "schema": schema_ddl,
            "dictionary": dictionary,
            "sql": sql_errada,
            "error": erro_db,
        })
    except Exception as e:
        raise RuntimeError(f"Erro ao comunicar com o LLM durante a correção: {e}")

    return _clean_sql(sql_fixed)


if __name__ == "__main__":
    from db import get_schema_ddl
    schema = get_schema_ddl()
    pergunta = "Quantos pedidos existem na base?"
    print(f"Pergunta: {pergunta}")
    sql = generate_sql(pergunta, schema)
    print(f"SQL gerada: {sql}")
