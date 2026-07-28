# 🚀 Guia de Execução do Projeto

## Pré-requisitos

- Python **3.11** ou superior instalado
- pip (geralmente vem com Python)

## Passo 1: Criar e ativar o ambiente virtual

Na **raiz do repositório**:

```bash
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

> Use `.venv` (e não `.env`) para o ambiente virtual — `.env` é reservado para arquivos de segredos locais.

## Passo 2: Instalar dependências

```bash
pip install -r requirements.txt
```

## Passo 3: Executar a aplicação Streamlit

A partir da **raiz do repositório**:

```bash
streamlit run app/Home.py
```

A aplicação abre em `http://localhost:8501`.

### Primeira execução (Streamlit) ⚠️

O Streamlit **não** baixa dados automaticamente. É necessário carregar a base oficial de cada loteria:

1. Na **barra lateral**, use o link **"⬇️ Baixar base atualizada"** (site da Caixa) e faça o download do **XLSX** da loteria desejada.
2. Em **"📤 Upload Manual do XLSX"**, selecione a loteria correspondente e envie o arquivo.
3. Confira o **"📂 Status das Bases"** na página inicial — loterias com arquivo carregado aparecem com ✅.
4. Navegue pelas páginas no menu lateral:
   - **📊 Estatísticas**
   - **🎯 Verificação**
   - **🔮 Forecast** (combinações inéditas)
   - **👨‍💻 Feito por**

### Onde os dados ficam (Streamlit)

Cada loteria é gravada em um XLSX próprio sob `app/data/`, conforme `app/core/lotteries.py`:

| Loteria | Arquivo |
|---------|---------|
| Mega-Sena | `app/data/Mega-Sena.xlsx` |
| Lotofácil | `app/data/Lotofácil.xlsx` |
| Quina | `app/data/Quina.xlsx` |
| Dupla Sena | `app/data/Dupla Sena.xlsx` |
| Lotomania | `app/data/Lotomania.xlsx` |
| Dia de Sorte | `app/data/Dia de Sorte.xlsx` |
| Timemania | `app/data/Timemania.xlsx` |
| Super Sete | `app/data/Super Sete.xlsx` |
| +Milionária | `app/data/+Milionária.xlsx` |

Esses arquivos são ignorados pelo Git (`.gitignore`).

---

## Opção 2: API REST (FastAPI)

A API é **independente** do Streamlit: não há chamadas HTTP entre eles. Ela opera hoje apenas com **Mega-Sena**, em formato **CSV** separado do fluxo XLSX da interface.

### Passo 1: Instalar dependências da API

```bash
pip install -r requirements-api.txt
```

### Passo 2: Executar a API

A partir da **raiz do repositório**:

```bash
uvicorn api.main:app --reload
```

A API fica em `http://localhost:8000`.

### Passo 3: Documentação interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Primeira execução (API) ⚠️

Antes de usar `/verify/` ou `/forecast/`, crie o dataset da Mega-Sena:

1. Acesse http://localhost:8000/docs
2. Abra `POST /dataset/`
3. Clique em **Try it out** → **Execute**

Isso baixa o XLSX oficial da Mega-Sena e grava **`app/data/megasena.csv`** (formato usado somente pela API).

Para consultar metadados do CSV: `GET /dataset/`.

### Endpoints disponíveis

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/verify/` | Verifica se um jogo da Mega-Sena já foi sorteado (`{"numbers": [1, 5, 12, 23, 34, 56]}`) |
| `GET` | `/forecast/?n=10` | Gera até 100 combinações inéditas da Mega-Sena |
| `GET` | `/dataset/` | Informações sobre o CSV carregado |
| `POST` | `/dataset/` | Baixa e atualiza `app/data/megasena.csv` |

---

## Dois caminhos de ingestão de dados

| Caminho | Onde | Como | Arquivo gerado |
|---------|------|------|----------------|
| **Upload manual (Streamlit)** | Barra lateral da Home | Download do XLSX no site da Caixa + upload | `app/data/<Loteria>.xlsx` (uma base por loteria) |
| **Download automático (API)** | `POST /dataset/` no Swagger | Scraper baixa Mega-Sena da Caixa | `app/data/megasena.csv` (somente Mega-Sena) |

O botão **"Atualizar Dataset"** **não existe** na interface Streamlit atual. Atualização automática via scraper está disponível **apenas pela API**.

---

## 🐳 Opção 3: Docker (recomendado)

Na raiz do repositório:

```bash
docker compose up --build
```

| Serviço | URL |
|---------|-----|
| Streamlit | http://localhost:8501 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |

Dados em `app/data/` persistem no volume Docker `apostas-data`.

Apenas Streamlit:

```bash
docker compose up --build streamlit
```

Apenas API:

```bash
docker compose up --build api
```

Build manual (sem Compose):

```bash
docker build -f docker/Dockerfile.streamlit -t loterias-analyzer-streamlit .
docker run --rm -p 8501:8501 -v loterias-data:/app/app/data loterias-analyzer-streamlit

docker build -f docker/Dockerfile.api -t loterias-analyzer-api .
docker run --rm -p 8000:8000 -v loterias-data:/app/app/data loterias-analyzer-api
```

---

## 🧪 Executar testes

```bash
pytest
```

Com mais detalhes:

```bash
pytest -v
```

---

## ❓ Solução de problemas

### Erro: base/dataset não encontrado (Streamlit)

**Solução:** faça upload do XLSX oficial na barra lateral da Home (`app/Home.py`) para a loteria desejada. Verifique **"📂 Status das Bases"**.

### Erro: dataset não encontrado (API)

**Solução:** execute `POST /dataset/` em http://localhost:8000/docs para gerar `app/data/megasena.csv`.

### Erro: `ModuleNotFoundError`

**Solução:** ative `.venv`, instale dependências e execute os comandos a partir da **raiz** do projeto:

```bash
pip install -r requirements.txt
pip install -r requirements-api.txt   # se for usar a API
```

### Erro ao executar Streamlit (`app/main.py` não encontrado)

**Solução:** o entrypoint correto é `app/Home.py` (não existe `app/main.py`):

```bash
streamlit run app/Home.py
```

### Porta já em uso

Streamlit em outra porta:

```bash
streamlit run app/Home.py --server.port 8502
```

API em outra porta:

```bash
uvicorn api.main:app --reload --port 8001
```

---

## 📝 Notas importantes

- **Streamlit:** bases em `app/data/*.xlsx` (upload manual, multi-loteria).
- **API:** base em `app/data/megasena.csv` (download via `POST /dataset/`, Mega-Sena).
- Forecast gera combinações **aleatórias inéditas** — não há modelo de machine learning em produção.
- Projeto com finalidade **educacional**; sorteios são eventos aleatórios.
