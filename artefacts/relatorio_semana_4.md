<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Universidade_Estadual_da_Para%C3%ADba_-_marca.svg/1200px-Universidade_Estadual_da_Para%C3%ADba_-_marca.svg.png" width="150">
  <br>
  <h3>Universidade Estadual da Paraíba (UEPB)</h3>
</div>

<br>

# Relatório Técnico: Entrega da Semana 4
**Projeto**: DataChat SQL Lite
**Domínio**: Brazilian E-Commerce Public Dataset (Olist)

---

## 1. Desenvolvimento da Interface

A interface da aplicação foi integralmente desenvolvida utilizando o framework **Streamlit**, focando em uma experiência de usuário (UX) intuitiva e executiva.
- **Design Sóbrio e Moderno**: Implementação de estilos CSS personalizados para ocultar elementos desnecessários da UI base, estilizar botões e áreas de chat, garantindo uma aparência profissional.
- **Consultas Recomendadas**: Inclusão de botões rápidos ("Consultas Recomendadas") para perguntas pré-definidas, facilitando o primeiro contato do usuário com a ferramenta.
- **Visualização em Abas**: Resultados são separados em duas abas: "Visualização" (explicação natural e tabela de dados) e "SQL Gerada" (para auditoria da consulta elaborada pelo LLM).

---

## 2. Explicações em Linguagem Natural e Formatação

Para entregar valor de negócio e não apenas dados brutos, a aplicação gera uma explicação amigável para cada retorno:
- **Templates Dinâmicos**: O sistema analisa o `DataFrame` resultante e a pergunta do usuário para criar textos explicativos. Por exemplo, formatação de números em padrão brasileiro (R$ e separador de milhar).
- **Fallback Genérico**: Caso a consulta do LLM fuja dos padrões pré-mapeados, uma explicação genérica dinâmica é acionada, descrevendo o volume de registros e colunas retornadas.
- **Indicador de Fonte**: Inserção de um marcador de fonte para que o usuário saiba exatamente de quais tabelas do banco DuckDB / Olist os dados foram extraídos.

---

## 3. Testes Finais e Validação

A aplicação passou por uma bateria de testes finais abordando todas as exigências obrigatórias do projeto.
- **Resiliência a Erros (RF08)**: Validado o comportamento da aplicação diante de perguntas fora de contexto ("OFF_TOPIC") ou falhas de SQL, com a interface exibindo um erro de processamento não obstrutivo.
- **Consultas com JOIN (RF10)**: Verificado o funcionamento de consultas complexas envolvendo relacionamentos entre múltiplas tabelas simultaneamente (`orders`, `order_items`, `products`, `customers`, etc.).
- **Histórico (RF09)**: O histórico funcional na barra lateral permite a revisão rápida e eficiente das interações prévias, evitando novos processamentos no LLM.

---

## 4. Documentação, Vídeo e Apresentação

Com o código finalizado, o esforço da Semana 4 consolidou-se nas entregas finais exigidas no edital:
- **Documentação Final**: Consolidação de todos os relatórios semanais técnicos (contendo o cabeçalho acadêmico oficial da UEPB), além da finalização da configuração do projeto.
- **Gravação do Vídeo**: Elaborado roteiro para o vídeo demonstrativo (até 5 minutos), focando em demonstrar o pipeline end-to-end: inserção da pergunta -> geração LLM -> SQL -> DuckDB -> Resultado explicado.
- **Apresentação**: Preparação do material para apresentação (10 a 15 minutos), enfatizando os desafios técnicos enfrentados em Prompt Engineering, a arquitetura com Llama 3.3 70B e a aderência integral a todos os requisitos.
