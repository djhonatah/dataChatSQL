import duckdb
import os

def run_tests():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'datachat.duckdb')
    
    if not os.path.exists(db_path):
        print("Banco de dados não encontrado. Execute setup_database.py primeiro.")
        return
        
    print(f"Conectando ao banco de dados: {db_path}")
    conn = duckdb.connect(db_path)
    
    queries = {
        "1. Quantos pedidos existem na base?": """
            SELECT COUNT(*) AS total_pedidos FROM orders;
        """,
        "2. Quantos clientes únicos realizaram compras?": """
            SELECT COUNT(DISTINCT customer_unique_id) AS clientes_unicos 
            FROM customers;
        """,
        "3. Qual categoria possui mais produtos?": """
            SELECT product_category_name, COUNT(*) as total_produtos 
            FROM products 
            WHERE product_category_name IS NOT NULL
            GROUP BY product_category_name 
            ORDER BY total_produtos DESC 
            LIMIT 1;
        """,
        "4. Qual categoria teve o maior faturamento?": """
            SELECT p.product_category_name, SUM(oi.price) AS faturamento
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE p.product_category_name IS NOT NULL
            GROUP BY p.product_category_name
            ORDER BY faturamento DESC
            LIMIT 1;
        """,
        "5. Qual forma de pagamento é mais utilizada?": """
            SELECT payment_type, COUNT(*) as qtd_utilizada
            FROM payments
            GROUP BY payment_type
            ORDER BY qtd_utilizada DESC
            LIMIT 1;
        """
    }
    
    print("\nExecutando Consultas de Teste:\n" + "-"*40)
    for description, query in queries.items():
        print(description)
        print(f"SQL: {query.strip()}")
        result = conn.execute(query).fetchdf()
        print("Resultado:")
        print(result.to_string(index=False))
        print("-" * 40)
        
    conn.close()

if __name__ == '__main__':
    run_tests()
