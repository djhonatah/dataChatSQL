# Dicionário de Dados - Olist E-commerce

Este dicionário provê contexto de negócio sobre o banco de dados para auxiliar o LLM na geração de queries SQL mais precisas.

## Tabelas e Domínios

### orders
Contém o registro mestre de pedidos.
- `order_status`: Status do pedido. Valores comuns: 'delivered' (entregue), 'shipped' (enviado), 'canceled' (cancelado), 'invoiced' (faturado), 'processing' (processando).
- Datas importantes: `order_purchase_timestamp` (data da compra), `order_delivered_customer_date` (data de entrega).

### order_items
Itens de cada pedido. Um pedido pode ter múltiplos itens.
- `price`: Preço do produto no item. Faturamento = soma de price.
- `freight_value`: Valor do frete.

### payments
Pagamentos relacionados aos pedidos.
- `payment_type`: Forma de pagamento. Valores comuns: 'credit_card', 'boleto', 'voucher', 'debit_card'.
- `payment_value`: Valor pago.

### reviews
Avaliações dadas pelos clientes aos pedidos.
- `review_score`: Nota de 1 a 5 (onde 5 é a maior/melhor nota).

### products
Dados físicos e de categoria dos produtos.
- `product_category_name`: Nome da categoria em português.

### category_translation
Tabela auxiliar de tradução.
- Serve para traduzir `product_category_name` (pt) para `product_category_name_english` (en).

### customers & sellers
Dados de localização.
- Usam estados (customer_state, seller_state) representados por siglas (SP, RJ, MG, etc).
- `customer_unique_id`: Identifica unicamente um cliente (um cliente pode ter múltiplas compras, ou seja, múltiplos `customer_id` mas um só `customer_unique_id`).
