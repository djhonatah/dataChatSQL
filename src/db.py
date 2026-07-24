import duckdb
import pandas as pd
import os

def _get_db_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "data", "datachat.duckdb")


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Retorna uma conexão com o banco de dados DuckDB.
    O banco deve ter sido criado previamente pelo setup_database.py.
    """
    db_path = _get_db_path()
    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Banco de dados não encontrado em: {db_path}\n"
            "Execute 'uv run python src/setup_database.py' primeiro."
        )
    return duckdb.connect(db_path, read_only=True)


def get_table_names() -> list[str]:
    """Retorna a lista de tabelas disponíveis no banco."""
    conn = get_connection()
    try:
        tables = conn.execute("SHOW TABLES").fetchall()
        return [t[0] for t in tables]
    finally:
        conn.close()


def get_schema_ddl() -> str:
    conn = get_connection()
    try:
        tables = conn.execute("SHOW TABLES").fetchall()
        ddl_parts = []

        for (table_name,) in tables:
            # Obter colunas e tipos de cada tabela
            columns = conn.execute(
                f"DESCRIBE {table_name}"
            ).fetchall()

            col_defs = []
            for col in columns:
                col_name = col[0]
                col_type = col[1]
                col_defs.append(f"    {col_name} {col_type}")

            ddl = f"CREATE TABLE {table_name} (\n"
            ddl += ",\n".join(col_defs)
            ddl += "\n);"

            # Obter amostra de dados (3 linhas) para contexto
            sample = conn.execute(
                f"SELECT * FROM {table_name} LIMIT 3"
            ).fetchdf()
            sample_str = sample.to_string(index=False)

            ddl_parts.append(
                f"{ddl}\n-- Exemplo de dados ({table_name}):\n{sample_str}"
            )

        return "\n\n".join(ddl_parts)
    finally:
        conn.close()

# Executa consulta SQL no banco de dados DuckDB
def execute_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        result = conn.execute(sql).fetchdf()
        return result
    except duckdb.Error as e:
        raise RuntimeError(f"Erro ao executar SQL: {e}\nQuery: {sql}")
    finally:
        conn.close()


if __name__ == "__main__":
    # Teste rápido
    print("=== Tabelas disponíveis ===")
    for t in get_table_names():
        print(f"  - {t}")

    print("\n=== Schema DDL (primeiras 500 chars) ===")
    ddl = get_schema_ddl()
    print(ddl[:500])

    print("\n=== Teste de query ===")
    df = execute_query("SELECT COUNT(*) AS total FROM orders")
    print(df)
