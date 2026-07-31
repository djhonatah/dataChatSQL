"""
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
    Returns:
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
        "explicacao": None,
        "erro": None,
    }

    try:
        # Obter schema do banco
        schema_ddl = get_schema_ddl()

        # Gerar SQL
        sql = generate_sql(pergunta, schema_ddl)
        
        # Bloquear perguntas fora de contexto
        if sql == "OFF_TOPIC":
            response["erro"] = "Essa pergunta parece estar fora do contexto dos dados de e-commerce que analiso. Por favor, faça perguntas sobre vendas, clientes, produtos ou pagamentos."
            return response
            
        response["sql"] = sql

        # Executar query no DuckDB
        resultado = execute_query(sql)
        response["resultado"] = resultado

    #ratamento de erros
    except Exception as e:
        response["erro"] = f"Erro durante o processamento da pergunta: {e}"

    return response


if __name__ == "__main__":
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
            print(f" Erro: {result['erro']}")
        else:
            print(f"SQL: {result['sql']}")
            print(f"\nResultado:")
            print(result["resultado"].head(10).to_string(index=False))
            print(f"\nExplicação: {result['explicacao']}")
