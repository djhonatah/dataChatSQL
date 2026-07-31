# Relatório Técnico: Entrega da Semana 3
**Projeto**: DataChat SQL Lite
**Domínio**: Brazilian E-Commerce Public Dataset (Olist)

---

## 1. Integração Completa com LLM

A integração completa da aplicação com a inteligência artificial foi finalizada, orquestrando todo o pipeline.
- **Implementação**: Através do `src/text_to_sql.py` e `src/backend.py`.
- **Dinâmica**: O aplicativo capta a pergunta do usuário via interface e envia para o backend. O backend puxa o schema, injeta no prompt em conjunto com a pergunta e envia à API do Groq (`llama-3.3-70b-versatile`). O modelo devolve a query formatada que é executada contra o DuckDB, garantindo que o ciclo completo de *text-to-SQL-to-data* funcione nativamente.

---

## 2. Tratamento de Erros e Estabilidade

A aplicação foi protegida contra falhas comuns durante a inferência ou na execução das consultas.
- **Captura de Exceções**: Blocos `try/except` foram implementados no `src/backend.py` e `src/text_to_sql.py`.
- **Tratamento no Frontend**: Se o modelo gerar um SQL inválido (alucinação) ou ocorrer um erro de conexão/API, a exceção é convertida em um alerta visual amigável (`st.error()`) através do Streamlit no arquivo `app/app.py`, garantindo que o aplicativo nunca congele ou "quebre" bruscamente para o usuário.

---

## 3. Implementação do Histórico de Consultas

Foi adicionado um mecanismo de persistência de sessão para melhorar a experiência do usuário (UX).
- **Gerenciamento de Estado**: Utilização intensiva do `st.session_state` no Streamlit (`app/app.py`).
- **Comportamento**: Cada vez que o usuário executa uma consulta válida, os dados (pergunta original, query SQL executada e o DataFrame com o resultado) são salvos numa lista em memória. 
- **Visualização**: O histórico é exposto numa aba dedicada na interface, renderizando *expanders* para que o executivo recupere rapidamente dados anteriores sem custo adicional de token e processamento.

---

## 4. Validação com Consultas Multi-tabela

Para testar o estresse e a aderência das queries num banco de dados normalizado e altamente relacional, desenvolvemos baterias de testes complexas no script `tests/test_multi_table_queries.py`.
- **Desafio Analítico**: O motor de SQL (`DuckDB`) precisou compilar e rodar queries que envolvem `JOIN` de 3 ou mais tabelas.
- **Cenários Testados**:
    - *Faturamento total por estado do cliente* (envolvendo `orders`, `customers` e `order_items`).
    - *Top 5 vendedores por faturamento* (envolvendo `sellers`, `order_items` e `orders`).
    - *Nota média de avaliação por categoria* (envolvendo 5 tabelas simultâneas: `reviews`, `orders`, `order_items`, `products` e `category_translation`).
    - *Forma de pagamento mais usada por estado* e *Pedidos entre estados diferentes*.
- **Resultados**: Todos os cenários rodaram com sucesso, indicando que a camada analítica está íntegra e robusta para cruzamentos complexos.
