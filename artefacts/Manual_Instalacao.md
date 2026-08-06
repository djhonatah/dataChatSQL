<div align="center">
  <img src="../assets/cropped-favicon.webp" width="150" alt="UEPB Logo">
  <br>
  <h3>Universidade Estadual da Paraíba (UEPB)</h3>
  <h4>Grupo: Djhonatah Wesley, Mirelle Casimiro e Filipe Antonny</h4>
</div>
<br>

# Manual de Instalação e Execução
**Projeto**: DataChat SQL Lite
**Domínio**: Brazilian E-Commerce Public Dataset (Olist)

---

## 1. Acesso Rápido (Executável na Nuvem)

A forma mais fácil de utilizar o projeto é acessar a versão já hospedada e executada na nuvem. Você não precisa instalar nada no seu computador.

🌐 **Link de Acesso (Aplicação Pública):** [https://datachatsql.streamlit.app/](https://datachatsql.streamlit.app/)

1. Acesse o link através de qualquer navegador web (Google Chrome, Firefox, Safari, Edge).
2. Aguarde a aplicação carregar.
3. Digite sua pergunta em linguagem natural no campo de texto e clique em **"Consultar 🚀"**.

---

## 2. Instalação e Execução Local (Ambiente de Desenvolvimento)

Caso deseje rodar a aplicação no seu próprio computador, o projeto utiliza a ferramenta `uv` (gerenciador de pacotes ultrarrápido do Python) para gerenciar as dependências de forma padronizada.

### Pré-requisitos
- Python 3.10 ou superior.
- Git instalado na sua máquina.
- Gerenciador de pacotes `uv` instalado. (Instale via terminal com `pip install uv` ou seguindo as instruções oficiais).
- Uma chave de API da Groq (`GROQ_API_KEY`).

### Passo a Passo

**1. Clone o Repositório**
Abra o seu terminal e clone o projeto público do GitHub:
```bash
git clone https://github.com/djhonatah/dataChatSQL.git
cd dataChatSQL
```

**2. Configure as Variáveis de Ambiente**
Na raiz do projeto, você deve criar um arquivo chamado `.env` e adicionar a sua chave da Groq para a Inteligência Artificial funcionar:
```env
GROQ_API_KEY="cole_sua_chave_aqui"
```

**3. Instale as Dependências**
Utilize o `uv` para ler o arquivo `uv.lock` e instalar o ambiente perfeitamente replicado:
```bash
uv sync
```

**4. Execute a Aplicação**
Para iniciar o servidor local do Streamlit, execute o seguinte comando:
```bash
uv run streamlit run app/app.py
```

O seu navegador padrão abrirá automaticamente na aba `http://localhost:8501` contendo o DataChat SQL Lite!
