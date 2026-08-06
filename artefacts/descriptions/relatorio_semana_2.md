<div align="center">
  <img src="../../assets/cropped-favicon.webp" width="150" alt="UEPB Logo">
  <br>
  <h3>Universidade Estadual da Paraíba (UEPB)</h3>
  <h4>Grupo: Djhonatah Wesley, Mirelle Casimiro e Filipe Antonny</h4>
</div>
<br>

<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Universidade_Estadual_da_Para%C3%ADba_-_marca.svg/1200px-Universidade_Estadual_da_Para%C3%ADba_-_marca.svg.png" width="150">
  <br>
  <h3>Universidade Estadual da Paraíba (UEPB)</h3>
</div>

<br>

# Relatório Técnico: Entrega da Semana 2
**Projeto**: DataChat SQL Lite
**Domínio**: Brazilian E-Commerce Public Dataset (Olist)

---

## 1. Integração com o Banco de Dados

Foi desenvolvido o módulo `src/db.py`, responsável por realizar a integração direta com o DuckDB. O componente atua como a camada de dados e fornece:
- **Extração do Esquema**: Uma função que extrai dinamicamente o DDL de todas as tabelas, incluindo amostras de dados, essencial para munir o LLM com o contexto necessário.
- **Conexão Segura**: Uso de `read_only=True` ao instanciar conexões para evitar injeção e alterações não desejadas nos dados.
- **Execução**: Um executor de queries simples que padroniza os retornos no formato tabular usando `pandas.DataFrame`.

## 2. Implementação do Módulo Text-to-SQL

A tradução da linguagem natural para SQL foi implementada no módulo `src/text_to_sql.py`:
- **Modelos e APIs**: Optou-se pela utilização do **LangChain** para facilitar a criação e a estruturação das *chains*. Como LLM, foi escolhido o **LLaMA 3.3 70B** executado por meio da provedora **Groq**, garantindo que as respostas sejam altamente velozes e precisas.
- **Comparação de LLMs Avaliados**:

  | Critério | LLaMA 3.3 70B (via Groq) | Gemini 2.5 Flash (Google) | GPT-4o (OpenAI) |
  | :--- | :--- | :--- | :--- |
  | **Velocidade (Latência)** | **Altíssima** (Infraestrutura LPU) | **Alta** (Otimizado para velocidade) | **Média** (Modelo mais pesado) |
  | **Custo por Requisição** | **Gratuito / Muito Baixo** | **Muito Baixo** | **Alto** |
  | **Limites de API (Tier Grátis)**| **~30 RPM** (Requisições por Minuto) | **15 RPM** (Requisições por Minuto) | **Sem tier grátis** (Depende de recarga) |
  | **Precisão Text-to-SQL** | **Alta** (Excelente lógica) | **Alta** (Boa estruturação) | **Altíssima** (Referência no mercado) |
- **Prompt Engineering**: Foi desenvolvido um *System Prompt* detalhado, injetando as instruções e restrições obrigatórias (ex.: limitar linhas, tratar NULL, não enviar markdown ou texto avulso, aderir ao DuckDB) juntamente com o DDL da estrutura do banco.

## 3. Desenvolvimento do Backend

O orquestrador do sistema, presente no arquivo `src/backend.py`, foi criado para alinhar todo o fluxo da requisição de forma sequencial:
1. Extração do schema atualizado (`db.py`).
2. Passagem da pergunta e do schema para o LLM gerar a SQL (`text_to_sql.py`).
3. Recuperação da query gerada e envio para o banco (`db.py`).
4. Retorno centralizado dos resultados em formato estruturado.

## 4. Primeiros Testes com Perguntas Simples

Para atestar o pleno funcionamento do núcleo, implementamos um script de testes (`src/test_text_to_sql.py`) contendo apenas perguntas de validação simples, de acordo com o escopo desta semana. Os testes avaliados e executados com sucesso foram:
- *"Quantos pedidos existem na base?"*
- *"Quantos clientes únicos realizaram compras?"*
- *"Qual categoria possui mais produtos?"*

Todos resultaram em geração SQL perfeitamente válida e dados precisos.
