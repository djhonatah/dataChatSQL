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

    # Consultas que exigem JOIN entre 3 ou mais tabelas, para validar a
    # integridade relacional completa da base (Semana 3 - testes multi-tabela).
    queries = {
        "1. Faturamento total por estado do cliente (orders + customers + order_items)": """
            SELECT c.customer_state, ROUND(SUM(oi.price + oi.freight_value), 2) AS faturamento_total
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_state
            ORDER BY faturamento_total DESC
            LIMIT 5;
        """,
        "2. Top 5 vendedores por faturamento em pedidos entregues (sellers + order_items + orders)": """
            SELECT s.seller_id, s.seller_city, ROUND(SUM(oi.price), 2) AS faturamento
            FROM sellers s
            JOIN order_items oi ON s.seller_id = oi.seller_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY s.seller_id, s.seller_city
            ORDER BY faturamento DESC
            LIMIT 5;
        """,
        "3. Nota média de avaliação por categoria (reviews + orders + order_items + products + category_translation)": """
            SELECT ct.product_category_name_english, ROUND(AVG(r.review_score), 2) AS nota_media, COUNT(*) AS total_avaliacoes
            FROM reviews r
            JOIN orders o ON r.order_id = o.order_id
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            JOIN category_translation ct ON p.product_category_name = ct.product_category_name
            GROUP BY ct.product_category_name_english
            HAVING COUNT(*) > 50
            ORDER BY nota_media DESC
            LIMIT 5;
        """,
        "4. Forma de pagamento mais usada pelos clientes de SP (payments + orders + customers)": """
            SELECT c.customer_state, pay.payment_type, COUNT(*) AS qtd
            FROM payments pay
            JOIN orders o ON pay.order_id = o.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE c.customer_state = 'SP'
            GROUP BY c.customer_state, pay.payment_type
            ORDER BY qtd DESC;
        """,
        "5. Pedidos onde cliente e vendedor são de estados diferentes (customers + orders + order_items + sellers)": """
            SELECT c.customer_state AS estado_cliente, s.seller_state AS estado_vendedor, COUNT(*) AS total_pedidos
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN sellers s ON oi.seller_id = s.seller_id
            WHERE c.customer_state != s.seller_state
            GROUP BY c.customer_state, s.seller_state
            ORDER BY total_pedidos DESC
            LIMIT 5;
        """
    }

    print("\nExecutando Consultas Multi-Tabela:\n" + "-" * 40)
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
