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

Instalação recomendada via `pyproject.toml` (dependências pinadas):

```bash
pip install -e ".[dev]"
```

O extra `[dev]` **inclui o extra `[api]`** (fastapi, uvicorn, httpx, …), então esse comando único já habilita a UI, a API e a suíte de testes completa (incluindo `tests/test_api.py`, que usa o `TestClient`/`httpx`). Se quiser apenas a API em produção, sem ferramentas de dev, use `pip install -e ".[api]"`.

Alternativa equivalente usando os arquivos legados:

```bash
pip install -r requirements-dev.txt   # pytest, ruff, mypy, pre-commit + API (fastapi, httpx, …)
```

Para instalações mínimas específicas: `requirements.txt` (só o núcleo/UI) e `requirements-api.txt` (núcleo + API).

### Pre-commit (recomendado)

Com o ambiente ativo e `[dev]` instalado:

```bash
pre-commit install
```

Isso executa ruff, formatação, checagem de YAML e outros hooks antes de cada commit.

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
3. O sistema valida o XLSX, processa e **grava no SQLite** (`app/data/loterias.db`).
4. Confira o **"📂 Status das Bases"** na página inicial — loterias já persistidas no banco aparecem com ✅.
5. No painel **Controles** (sidebar), escolha a **loteria** e o **tema** (claro/escuro) — a preferência permanece ao navegar.
6. Navegue pelas páginas no menu lateral:
   - **📊 Estatísticas** — frequência clássica, análises específicas (trevos, Dupla Sena, Super Sete, Timemania) + PDF (Gerar → Baixar)
   - **🎯 Verificação** — conferir jogos + salvar no histórico local
   - **🔮 Combinações Inéditas** (sorteio aleatório, sem ML) + salvar no histórico
   - **📜 Histórico** — listar / exportar / apagar jogos salvos nesta instalação
   - **👨‍💻 Feito por**

### Onde os dados ficam

Streamlit e API compartilham **um único banco SQLite**:

| Item | Valor |
|------|-------|
| Arquivo padrão | `app/data/loterias.db` |
| Variável de ambiente | `LOTTERIAS_DB_PATH` (opcional; sobrescreve o caminho) |
| Tabelas | `draws` (sorteios), `lottery_metadata` (cache por modalidade), `user_games` (histórico local do usuário) |

O **XLSX da Caixa** é apenas o formato de **ingestão** no upload (ou no scraper da API). As páginas e a API **leem do SQLite**, não de arquivos `.xlsx` / `.csv` por loteria.

O arquivo `loterias.db` é ignorado pelo Git (`.gitignore`: `app/data/*.db`).

---

## Opção 2: API REST (FastAPI)

A API é **independente** do Streamlit: não há chamadas HTTP entre eles. Ambos leem/escrevem o **mesmo** `loterias.db`.

Rotas canônicas usam `lottery_key` (ex.: `megasena`, `lotofacil`, `quina`).  
`/verify/`, `/combinations/`, `/forecast/` e `/dataset/` permanecem como **aliases da Mega-Sena**.

### Passo 1: Instalar dependências da API

Se ainda não instalou tudo de uma vez:

```bash
pip install -e ".[api]"
```

Ou, via requirements legado:

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

Antes de usar verify/combinations de uma modalidade, popule o SQLite:

1. Acesse http://localhost:8000/docs
2. Liste modalidades: `GET /lotteries`
3. Atualize uma base, por exemplo `POST /lotteries/megasena/dataset` (ou o alias `POST /dataset/`)

Isso baixa o XLSX oficial via scraper e grava (de forma incremental) em **`app/data/loterias.db`**.

Para consultar metadados: `GET /lotteries/{key}/dataset`, `GET /dataset/` (Mega-Sena) ou `GET /health`.

### Endpoints disponíveis

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Status da API, banco e cache por modalidade |
| `GET` | `/lotteries` | Catálogo + status de cache de todas as modalidades |
| `POST` | `/lotteries/{key}/verify` | Verifica jogo (`{"numbers": [...], "extras": {...}?}`) contra a modalidade |
| `GET` | `/lotteries/{key}/combinations?n=10` | Combinações inéditas (sorteio aleatório) |
| `GET` | `/lotteries/{key}/forecast?n=10` | Alias semântico de combinations |
| `GET` | `/lotteries/{key}/dataset` | Metadados da modalidade no SQLite |
| `POST` | `/lotteries/{key}/dataset` | Baixa e atualiza a modalidade (rate limit: 3/h por padrão) |
| `POST` | `/verify/` | Alias Mega-Sena de verify |
| `GET` | `/combinations/`, `/forecast/` | Aliases Mega-Sena |
| `GET/POST` | `/dataset/` | Aliases Mega-Sena de dataset |

Keys válidas: as de `LOTTERIES_BY_KEY` (`megasena`, `lotofacil`, `quina`, `duplasena`, `lotomania`, `diadesorte`, `timemania`, `supersete`, `mais_milionaria`).

### Variáveis de ambiente (API)

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `LOTTERIAS_DB_PATH` | `app/data/loterias.db` | Caminho do SQLite compartilhado com o Streamlit |
| `LOG_LEVEL` | `INFO` | Nível de log (`DEBUG`, `INFO`, `WARNING`, …) |
| `ENVIRONMENT` | `development` | `production` restringe CORS se `CORS_ORIGINS` não estiver definido |
| `CORS_ORIGINS` | *(vazio)* | Origens permitidas separadas por vírgula (ex.: `http://localhost:8501`) |
| `MAX_BODY_BYTES` | `10240` | Tamanho máximo do corpo HTTP (bytes) |
| `MAX_FORECAST_N` | `100` | Limite máximo do parâmetro `n` em forecast/combinations |
| `RATE_LIMIT_DATASET` | `3/hour` | Rate limit do `POST .../dataset` |
| `RATE_LIMIT_FORECAST` | `30/minute` | Rate limit do forecast |
| `RATE_LIMIT_COMBINATIONS` | `60/minute` | Rate limit de combinations |

Respostas de erro seguem o formato JSON `{ "detail": "...", "code": "..." }` (ex.: `VALIDATION_ERROR`, `RATE_LIMIT_EXCEEDED`, `NOT_FOUND`).

---

## Dois caminhos de ingestão de dados

| Caminho | Onde | Como | Destino |
|---------|------|------|---------|
| **Upload manual (Streamlit)** | Barra lateral da Home | Download do XLSX no site da Caixa + upload | `app/data/loterias.db` (qualquer modalidade) |
| **Download automático (API)** | `POST /lotteries/{key}/dataset` | Scraper baixa a modalidade da Caixa | `app/data/loterias.db` |

O botão **"Atualizar Dataset"** **não existe** na interface Streamlit atual. Atualização automática via scraper está disponível **pela API**.

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

Dados em `app/data/` (incluindo `loterias.db`) persistem no volume Docker `apostas-data`. Ambos os serviços usam `LOTTERIAS_DB_PATH=/app/app/data/loterias.db`.

A imagem Streamlit inclui [`.streamlit/config.toml`](../.streamlit/config.toml) (tema de boot e porta). O seletor **Tema** na sidebar ajusta cores em runtime via CSS (`app/ui/theme_manager.py`). Secrets locais (`.streamlit/secrets.toml`) **não** entram na imagem.

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

### Smoke live da API

Com a API no ar (Compose ou `docker run`):

```bash
pip install -e ".[api]"
python scripts/smoke_api.py
```

Contra uma URL hospedada:

```bash
API_BASE_URL=https://sua-api.exemplo.com python scripts/smoke_api.py
```

O Community Cloud hospeda **apenas** o Streamlit; a API precisa de Docker/PaaS separado. O CI (workflow Docker) sobe o container da API e roda o mesmo smoke.

---

## 🧪 Executar testes

Com o extra `[dev]` instalado (`pip install -e ".[dev]"` ou `pip install -r requirements-dev.txt`):

```bash
pytest
```

Com cobertura (exige `pytest-cov`; limiar mínimo 60% em `[tool.coverage.report]`):

```bash
pytest --cov --cov-report=term-missing
```

Com mais detalhes:

```bash
pytest -v
```

### Lint e formatação

```bash
ruff check .
ruff format --check .
```

---

## ❓ Solução de problemas

### Erro: base/dataset não encontrado (Streamlit)

**Solução:** faça upload do XLSX oficial na barra lateral da Home (`app/Home.py`) para a loteria desejada. Verifique **"📂 Status das Bases"** e a existência de `app/data/loterias.db`.

### Erro: dataset não encontrado (API)

**Solução:** em http://localhost:8000/docs, use `POST /lotteries/{key}/dataset` (ex.: `megasena`, `lotofacil`) ou o alias Mega-Sena `POST /dataset/`. Confira `GET /health` e a existência de `app/data/loterias.db`.

### Erro: `ModuleNotFoundError`

**Solução:** ative `.venv`, instale dependências e execute os comandos a partir da **raiz** do projeto:

```bash
pip install -e ".[dev]"
```

### Erro: `pytest: error: unrecognized arguments: --cov` / falta `pytest-cov`

Cobertura **não** está no `addopts` padrão. Use `pytest` sem flags, ou instale o extra de desenvolvimento e rode com `--cov`:

```bash
pip install -r requirements-dev.txt   # ou: pip install -e ".[dev]"
pytest --cov --cov-report=term-missing
```

Confirme que o venv é `.venv` (não confunda com o arquivo `.env` de secrets).

### Erro: `pytest` falha na coleta de `test_api.py` (falta `httpx`/`fastapi`)

**Sintoma:** ao rodar `pytest`, a coleta de `tests/test_api.py` falha com `ModuleNotFoundError: No module named 'httpx'` (ou `fastapi`). Ocorre quando o ambiente tem apenas o núcleo instalado, sem as dependências da API.

**Solução:** instale o extra de desenvolvimento — ele **já inclui** o extra `[api]` (fastapi, httpx, …):

```bash
pip install -e ".[dev]"   # ou: pip install -r requirements-dev.txt
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

- **Persistência unificada:** Streamlit e API usam `app/data/loterias.db` (SQLite: `draws`, `lottery_metadata`, `user_games`).
- **XLSX:** formato de ingestão da Caixa (upload ou scraper); não é o store de leitura das páginas.
- **Sidebar Controles:** loteria (`selected_lottery`) e tema claro/escuro persistem entre páginas; upload usa key `upload_lottery` separada.
- **API:** multi-loteria (`/lotteries/{key}/...`) com aliases Mega-Sena; preferir rotas canônicas.
- O gerador de combinações inéditas usa sorteio **aleatório uniforme** — não há modelo de machine learning em produção.
- Projeto com finalidade **educacional**; sorteios são eventos aleatórios.
