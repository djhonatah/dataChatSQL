"""
Backend — Orquestrador do pipeline DataChat SQL.
Conecta os módulos db.py e text_to_sql.py em um fluxo completo:
    Pergunta → SQL → Execução → Explicação
"""

import sys
import os
import pandas as pd

# Adiciona src ao path para imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_schema_ddl, execute_query
from text_to_sql import generate_sql


def process_question(pergunta: str) -> dict:
    """
    Processa uma pergunta em linguagem natural e retorna o resultado completo.

    Pipeline:
        1. Extrai o schema DDL do banco
        2. Gera SQL a partir da pergunta usando o LLM
        3. Executa a query no DuckDB
        4. Gera explicação em linguagem natural

    Args:
        pergunta: Pergunta do usuário em linguagem natural.

    Returns:
        Dicionário com:
            - pergunta (str): pergunta original
            - sql (str): query SQL gerada
            - resultado (pd.DataFrame): resultado da consulta
            - explicacao (str): explicação em linguagem natural
            - erro (str | None): mensagem de erro se houver falha
    """
    response = {
        "pergunta": pergunta,
        "sql": "",
        "resultado": pd.DataFrame(),
        "erro": None,
    }

    # 1. Obter schema do banco
    schema_ddl = get_schema_ddl()

    # 2. Gerar SQL via LLM
    sql = generate_sql(pergunta, schema_ddl)
    response["sql"] = sql

    # 3. Executar query no DuckDB
    resultado = execute_query(sql)
    response["resultado"] = resultado

    return response


if __name__ == "__main__":
    # Teste rápido do pipeline completo
    perguntas = [
        "Quantos pedidos existem na base?",
        "Qual categoria teve maior faturamento?",
    ]

    for p in perguntas:
        print(f"\n{'='*60}")
        print(f"Pergunta: {p}")
        print("=" * 60)

        result = process_question(p)

        if result["erro"]:
            print(f"❌ Erro: {result['erro']}")
        else:
            print(f"SQL: {result['sql']}")
            print(f"\nResultado:")
            print(result["resultado"].head(10).to_string(index=False))
            print(f"\nExplicação: {result['explicacao']}")
