import duckdb
import os
import glob

def setup():
    # Caminhos
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'datasCSV', 'dataset_olist')
    db_dir = os.path.join(base_dir, 'data')
    
    # Criar pasta data se não existir
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'datachat.duckdb')
    
    print(f"Criando banco de dados em: {db_path}")
    conn = duckdb.connect(db_path)
    
    # Mapeamento dos arquivos CSV para o nome da tabela
    tables_map = {
        'olist_orders_dataset.csv': 'orders',
        'olist_order_items_dataset.csv': 'order_items',
        'olist_products_dataset.csv': 'products',
        'olist_customers_dataset.csv': 'customers',
        'olist_sellers_dataset.csv': 'sellers',
        'olist_order_payments_dataset.csv': 'payments',
        'olist_order_reviews_dataset.csv': 'reviews',
        'product_category_name_translation.csv': 'category_translation'
    }
    
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        if filename in tables_map:
            table_name = tables_map[filename]
            print(f"Importando {filename} para a tabela {table_name}...")
            query = f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM read_csv_auto('{csv_file}');"
            try:
                conn.execute(query)
                print(f"Tabela {table_name} importada com sucesso!")
            except Exception as e:
                print(f"Erro ao importar {table_name}: {e}")
                # Caso a tabela já exista, podemos tentar dropar e recriar ou ignorar
                pass
                
    # Mostra as tabelas criadas
    print("\nTabelas criadas no banco de dados:")
    tables = conn.execute("SHOW TABLES").fetchall()
    for t in tables:
        print(f"- {t[0]}")
        
    conn.close()
    print("\nBanco de dados configurado com sucesso!")

if __name__ == '__main__':
    setup()
