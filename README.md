
# 🎰 Loterias Analyzer

![CI](https://github.com/ersjunior/ApostasLoteria/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Status](https://img.shields.io/badge/Status-Ativo-success)
![License](https://img.shields.io/badge/License-MIT-green)

> **Análise estatística, verificação de jogos e geração de combinações inéditas para loterias brasileiras**, utilizando dados oficiais da Caixa Econômica Federal.

Uma plataforma **educacional e analítica** para estudo de loterias brasileiras, baseada em dados oficiais da Caixa Econômica Federal.

> ⚠️ **Aviso:** Este projeto **não garante prêmios**. Todos os sorteios são eventos aleatórios.
> Se você ou alguém próximo tem dificuldade com jogo compulsivo, busque apoio em [Jogadores Anônimos](https://jogadoresanonimos.com.br/).

---

## 📌 Visão Geral

O **Loterias Analyzer** é uma aplicação **educacional e analítica**, desenvolvida em **Python + Streamlit**, projetada para estudar jogos de loteria de forma estruturada, clara e extensível.

O projeto oferece:

- 🔍 Verificação de jogos históricos
- 🔮 Geração de combinações inéditas (sorteio aleatório, sem ML)
- 📊 Estatísticas interativas com gráficos
- 💰 Simulação de custos e probabilidades reais
- 📄 Exportação de relatórios e dados
- 🌐 API REST (FastAPI) para Mega-Sena

---

## 🎲 Loterias Suportadas

| Loteria | Suporte |
|------|------|
| 🎰 Mega-Sena | ✅ |
| 🍀 Lotofácil | ✅ |
| 🎯 Quina | ✅ |
| 🔁 Dupla Sena (2 sorteios) | ✅ |
| 🌞 Dia de Sorte | ✅ |
| ⚽ Timemania | ✅ |
| 7️⃣ Super Sete | ✅ |
| 💎 +Milionária (dezenas + trevos) | ✅ |
| 🎲 Lotomania | ⚠️ Estrutura especial |

---

## 🧠 Funcionalidades

### 🎯 Verificação de Jogos
- Verificação de múltiplos jogos
- Validação correta por tipo de loteria
- Suporte a campos extras e múltiplos sorteios
- Resultados exibidos em cards organizados

### 🔮 Gerador de Combinações Inéditas
- Sorteio aleatório uniforme de combinações nunca sorteadas
- Respeita regras específicas de cada loteria
- **Sem modelo preditivo** — não há machine learning em produção
- Exportação em CSV

### 📊 Estatísticas Interativas
- Frequência histórica das dezenas
- Teste qui-quadrado de uniformidade (hot/cold é ruído)
- Valor esperado e vantagem da casa
- Probabilidade empírica e combinatória C(n,k) por modalidade
- Top & Bottom dezenas (dinâmico)
- Gráficos interativos com Plotly
- Simulação de custos e probabilidades

### 🌐 API REST (Mega-Sena)
- `GET /health` — health check, status do banco SQLite e cache por modalidade
- `POST /verify/` — verificação de jogos
- `GET /combinations/` e `GET /forecast/` — combinações inéditas
- `GET` / `POST /dataset/` — metadados e atualização via scraper
- CORS, rate limiting, validação Pydantic e logging configuráveis

### 📄 Relatórios
- Exportação de jogos em CSV

---

## 🧭 Como Utilizar

### 1️⃣ Obter a base oficial
Acesse o site da Caixa Econômica Federal:

https://loterias.caixa.gov.br/

Faça o download do arquivo **XLSX** da loteria desejada (link também disponível na barra lateral da Home).

---

### 2️⃣ Upload do XLSX (Streamlit)
Na página **Home** (`app/Home.py`), barra lateral **"📤 Upload Manual do XLSX"**:
1. Selecione a loteria correspondente ao arquivo
2. Envie o XLSX oficial
3. Confira **"📂 Status das Bases"** na Home (✅ = base carregada no SQLite)

Os dados são persistidos em **`app/data/loterias.db`** (SQLite), compartilhado entre Streamlit e API no Docker.

⚠️ Use apenas arquivos oficiais da Caixa.

---

### 2️⃣ bis — Atualização via API (opcional, Mega-Sena)

Com a **API FastAPI** em execução, use `POST /dataset/` em http://localhost:8000/docs para baixar a Mega-Sena automaticamente. A atualização é **incremental por concurso** — só novos sorteios são inseridos no banco.

---

### 3️⃣ Verificação
- Vá até **🎯 Verificação**
- Selecione a loteria e insira seus jogos
- Veja se já foram sorteados

---

### 4️⃣ Combinações Inéditas
- Vá até **🔮 Combinações Inéditas**
- Gere combinações inéditas por sorteio aleatório
- Exporte os resultados em CSV

---

### 5️⃣ Estatísticas
- Vá até **📊 Estatísticas**
- Explore gráficos, probabilidades e custos

---

## 🏗️ Estrutura do Projeto

```
├── .github/
│   ├── ISSUE_TEMPLATE/             # Templates de bug e feature
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── ci.yml                  # Lint, mypy, pytest, cobertura
│       └── docker.yml              # Build das imagens Docker
├── api/                            # API REST (FastAPI)
│   ├── config.py                   # Variáveis de ambiente
│   ├── main.py
│   ├── routes/
│   │   ├── combinations.py
│   │   ├── dataset.py
│   │   ├── forecast.py
│   │   ├── health.py               # GET /health
│   │   └── verify.py
│   └── services/
│       └── core.py
├── loterias_core/                  # Domínio puro (app + api consomem)
│   ├── combinatorics.py
│   ├── dataset.py
│   ├── expected_value.py
│   ├── generator.py
│   ├── lotteries.py
│   ├── schema.py
│   ├── scraper.py
│   ├── statistics.py
│   └── validator.py
├── app/                            # Aplicação Streamlit
│   ├── core/
│   │   └── lotteries.py
│   ├── data/                       # Bases XLSX/CSV (gitignored)
│   ├── pages/
│   │   ├── 1_📊_Estatísticas.py
│   │   ├── 2_🎯_Verificação.py
│   │   ├── 3_🔮_Combinações_Inéditas.py
│   │   └── 4_👨‍💻_Feito por.py
│   ├── services/
│   │   ├── cache.py
│   │   ├── dataset.py
│   │   ├── exporter.py
│   │   ├── report.py
│   │   ├── scraper.py
│   │   ├── statistics.py
│   │   └── validator.py
│   ├── ui/
│   │   ├── lottery_selector.py
│   │   ├── theme_manager.py
│   │   └── theme.py
│   └── Home.py                     # entrypoint Streamlit
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.streamlit
│   └── entrypoint.sh
├── tests/
│   ├── fixtures/                   # XLSX/CSV de teste por loteria
│   ├── test_api.py
│   ├── test_cache.py
│   ├── test_combinatorics.py
│   ├── test_dataset.py
│   ├── test_exporter.py
│   ├── test_generator.py
│   ├── test_report.py
│   ├── test_schema.py
│   ├── test_scraper.py
│   ├── test_statistics.py
│   └── test_validator.py
├── .env.example                    # Variáveis de ambiente (copie para .env)
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docker-compose.yml
├── docs/
│   ├── ARCHITECTURE_NOTES.md
│   ├── COMO_EXECUTAR.md
│   └── README.md
├── pyproject.toml                  # Dependências e config (ruff, mypy, pytest)
├── requirements.txt                # Atalho: pip install -e .
├── requirements-api.txt            # Atalho: pip install -e .[api]
└── README.md
```

---

## ⚙️ Tecnologias

- 🐍 Python 3.11+
- 🎨 Streamlit
- ⚡ FastAPI + Uvicorn
- 📊 Pandas & NumPy
- 📈 Plotly
- 📄 ReportLab
- 📁 XLSX oficiais da Caixa
- 🔧 Ruff, mypy, pytest, pre-commit

---

## 🔧 Variáveis de ambiente

Copie o exemplo e ajuste conforme necessário:

```bash
cp .env.example .env          # Linux/macOS
copy .env.example .env        # Windows
```

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `LOG_LEVEL` | `INFO` | Nível de log da API |
| `ENVIRONMENT` | `development` | `production` restringe CORS se `CORS_ORIGINS` vazio |
| `CORS_ORIGINS` | *(vazio)* | Origens permitidas, separadas por vírgula |
| `MAX_BODY_BYTES` | `10240` | Limite de payload HTTP (bytes) |
| `MAX_FORECAST_N` | `100` | Máximo do parâmetro `n` em forecast/combinations |
| `RATE_LIMIT_DATASET` | `3/hour` | Rate limit do `POST /dataset/` |
| `RATE_LIMIT_FORECAST` | `30/minute` | Rate limit do `GET /forecast/` |
| `RATE_LIMIT_COMBINATIONS` | `60/minute` | Rate limit do `GET /combinations/` |

> O Streamlit **não** consome a API por HTTP; `API_BASE_URL` não se aplica na arquitetura atual. Detalhes em [`.env.example`](.env.example) e [docs/COMO_EXECUTAR.md](docs/COMO_EXECUTAR.md).

---

## 🚀 Como executar (Docker — recomendado)

**Pré-requisito:** [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/) (Compose v2 vem com Docker Desktop).

Na raiz do repositório:

```bash
docker compose up --build
```

Para encerrar os containers: `docker compose down`.

Isso sobe:

| Serviço    | URL                         |
|-----------|-----------------------------|
| Streamlit | http://localhost:8501       |
| API (FastAPI) | http://localhost:8000   |
| Documentação Swagger | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

Os dados em `app/data/` (arquivos enviados ou gerados pela app) ficam no volume Docker `apostas-data` e persistem entre reinícios dos containers.

### Apenas a interface Streamlit

```bash
docker compose up --build streamlit
```

### Apenas a API

```bash
docker compose up --build api
```

### Build manual (sem Compose)

**Streamlit:**

```bash
docker build -f docker/Dockerfile.streamlit -t loterias-analyzer-streamlit .
docker run --rm -p 8501:8501 -v loterias-data:/app/app/data loterias-analyzer-streamlit
```

**API:**

```bash
docker build -f docker/Dockerfile.api -t loterias-analyzer-api .
docker run --rm -p 8000:8000 -v loterias-data:/app/app/data loterias-analyzer-api
```

---

## 💻 Execução local (sem Docker)

```bash
# criar ambiente virtual
python -m venv .venv

# ativar
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# instalar dependências (app + API + ferramentas de dev)
pip install -e ".[dev,api]"

# variáveis de ambiente (opcional, principalmente para a API)
cp .env.example .env

# hooks de qualidade (opcional, recomendado)
pre-commit install

# interface web
streamlit run app/Home.py
```

Para a API localmente:

```bash
uvicorn api.main:app --reload
```

A API expõe `GET /health` para health check, CORS configurável via `CORS_ORIGINS`, rate limiting em rotas sensíveis e validação Pydantic com respostas de erro `{detail, code}`. Detalhes em [docs/COMO_EXECUTAR.md](docs/COMO_EXECUTAR.md).

### Qualidade de código

```bash
ruff check .
ruff format --check .
pytest
mypy app api loterias_core
```

---

## 🔄 CI (GitHub Actions)

O badge no topo aponta para o workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml):

| Job | O que faz |
|-----|-----------|
| **lint-test** | Ruff lint + format, mypy (continue-on-error), pytest com cobertura mínima 60% |
| Matriz | Python **3.11** e **3.12** |
| Artefato | `coverage.xml` (Python 3.11) |

Workflow adicional [`.github/workflows/docker.yml`](.github/workflows/docker.yml) valida o build das imagens API e Streamlit em cada PR/push.

---

## 🤝 Contribuindo

Leia [CONTRIBUTING.md](CONTRIBUTING.md) para configurar o ambiente, rodar testes, padrão de commits e abrir PRs. Use os templates em [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) para bugs e features.

Histórico de mudanças: [CHANGELOG.md](CHANGELOG.md).

---

## ⚠️ Aviso Legal e Jogo Responsável

Este projeto é **estritamente educacional e analítico**.
Jogos de loteria são eventos **aleatórios**.
Nenhuma análise estatística garante prêmio.

Se você ou alguém próximo tem dificuldade com **jogo compulsivo**, procure apoio gratuito em [Jogadores Anônimos](https://jogadoresanonimos.com.br/). Para apoio emocional imediato, ligue **188** (CVV — Centro de Valorização da Vida).

A interface Streamlit exibe uma nota de jogo responsável no rodapé de todas as páginas.

---

## 👨‍💻 Feito por

**Eliezer Junior**
- 💼 LinkedIn: https://www.linkedin.com/in/eliezer-junior/
- 🐙 GitHub: https://github.com/eliezerjunior

Especialista em Dados, Engenharia e Inteligência Artificial.

---

## 📌 Roadmap

- [x] API REST (FastAPI)
- [x] Docker / Compose
- [x] CI (lint, testes, cobertura)
- [x] Pacote `loterias_core` compartilhado
- [ ] Histórico de jogos do usuário
- [x] Cache avançado por loteria (SQLite + atualização incremental)
- [x] Deploy em cloud (Streamlit Community Cloud)

---

## 🚀 Deploy (Streamlit Community Cloud)

### Pré-requisitos

- Repositório no GitHub (público ou privado com plano compatível)
- Conta em [share.streamlit.io](https://share.streamlit.io/)

### Passo a passo

1. **Fork / push** do repositório para o GitHub.
2. Acesse [Streamlit Community Cloud](https://share.streamlit.io/) → **New app**.
3. Selecione o repositório, branch e defina:
   - **Main file path:** `app/Home.py`
   - **Python version:** 3.11+
4. Em **Advanced settings → Secrets**, configure (veja [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example)):

```toml
LOTTERIAS_DB_PATH = "app/data/loterias.db"
```

5. Clique em **Deploy**. O app sobe sem dados — na primeira visita, faça **upload do XLSX** oficial na barra lateral ou popule via API em outro ambiente e copie o `loterias.db`.

### Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `LOTTERIAS_DB_PATH` | `app/data/loterias.db` | Caminho do banco SQLite |

No Cloud, secrets em `st.secrets` são lidos na inicialização via `app/config.py`.

### Banco vazio no primeiro boot

Se nenhuma modalidade estiver carregada, a Home exibe aviso e instruções. Faça upload do XLSX oficial ou use `POST /dataset/` (API) para a Mega-Sena.

### Docker local (produção)

```bash
docker compose up --build
```

Volume `apostas-data` persiste `loterias.db` entre reinícios. Ambos os serviços usam `LOTTERIAS_DB_PATH=/app/app/data/loterias.db`.

---

⭐ Se este projeto foi útil, deixe uma estrela no GitHub!
