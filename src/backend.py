"""
    Pergunta → SQL → Execução → Explicação
"""

import sys
import os
import pandas as pd

# Adiciona src ao path para imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_schema_ddl, execute_query
from text_to_sql import generate_sql, fix_sql_error


def process_question(pergunta: str, historico: list = None) -> dict:
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

        # Gerar SQL (agora com histórico)
        sql = generate_sql(pergunta, schema_ddl, historico)
        
        # Bloquear perguntas fora de contexto
        if sql == "OFF_TOPIC":
            response["erro"] = "Essa pergunta parece estar fora do contexto dos dados de e-commerce que analiso. Por favor, faça perguntas sobre vendas, clientes, produtos ou pagamentos."
            return response
            
        response["sql"] = sql

        # Executar query no DuckDB com lógica de Auto-Correção (Self-Healing)
        try:
            resultado = execute_query(sql)
            response["resultado"] = resultado
        except Exception as db_error:
            error_msg = str(db_error)
            sucesso = False
            
            # Tenta corrigir a query até 2 vezes
            for tentativa in range(2):
                try:
                    sql = fix_sql_error(pergunta, schema_ddl, sql, error_msg)
                    response["sql"] = sql  # atualiza para mostrar a query que funcionou
                    resultado = execute_query(sql)
                    response["resultado"] = resultado
                    sucesso = True
                    break
                except Exception as ex:
                    error_msg = str(ex)  # novo erro para a próxima iteração
                    
            if not sucesso:
                raise RuntimeError(f"O agente não conseguiu gerar uma query válida. Último erro: {error_msg}")

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
