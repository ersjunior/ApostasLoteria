# Loterias Analyzer

![CI](https://github.com/ersjunior/ApostasLoteria/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![FastAPI](https://img.shields.io/badge/FastAPI-multi--loteria-teal)
![License](https://img.shields.io/badge/License-MIT-green)

> Análise estatística, verificação de jogos e geração de combinações inéditas para loterias brasileiras — com dados oficiais da Caixa Econômica Federal.

Plataforma **educacional e analítica** em **Python**: interface **Streamlit** e **API REST (FastAPI)** compartilhando o mesmo domínio (`loterias_core`) e o mesmo banco **SQLite**.

> **Aviso:** este projeto **não garante prêmios**. Sorteios são eventos aleatórios.
> Se você ou alguém próximo tem dificuldade com jogo compulsivo, busque apoio em [Jogadores Anônimos](https://jogadoresanonimos.com.br/).

---

## Visão geral

| Camada | Papel |
|--------|--------|
| **Streamlit** (`app/`) | UI multipágina: estatísticas, verificação, combinações, histórico, upload de XLSX |
| **FastAPI** (`api/`) | REST multi-loteria + aliases Mega-Sena; scraper; health/cache |
| **loterias_core/** | Domínio puro: catálogo, ingestão, estatística, gerador, storage SQLite |
| **SQLite** | Store único: `app/data/loterias.db` (sorteios, metadados e histórico local) |

O Streamlit **não** chama a API por HTTP. Em Docker, ambos serviços montam o mesmo volume e a mesma `LOTTERIAS_DB_PATH`.

---

## Loterias suportadas

Nove modalidades no catálogo (`loterias_core/lotteries.py`):

| Loteria | Key | Particularidades |
|---------|-----|------------------|
| Mega-Sena | `megasena` | 6 dezenas / universo 60 |
| Lotofácil | `lotofacil` | 15 / 25 |
| Quina | `quina` | 5 / 80 |
| Dupla Sena | `duplasena` | 2 sorteios por concurso (`draw_index`) |
| Lotomania | `lotomania` | Handler especial (50 / 100) |
| Dia de Sorte | `diadesorte` | 7 / 31 |
| Timemania | `timemania` | Time do Coração (`timecoração`) |
| Super Sete | `supersete` | 7 colunas posicionais (dígitos 0–9) |
| +Milionária | `mais_milionaria` | 6 dezenas + 2 trevos (1–6) |

---

## Funcionalidades

### Interface Streamlit

- **Controles na sidebar** — loteria e tema claro/escuro compartilhados entre páginas (`app/ui/shell.py`)
- **Home** — visão do produto, status das bases no SQLite, upload do XLSX oficial
- **Estatísticas** — frequência, qui-quadrado, valor esperado, C(n,k), Plotly, PDF; análises específicas (trevos, Dupla Sena, Super Sete, Timemania)
- **Verificação** — 1–20 jogos com extras; salvamento no histórico local
- **Combinações inéditas** — sorteio aleatório uniforme (**sem ML**); CSV + histórico
- **Histórico** — listar, filtrar, exportar, apagar e verificar novamente (`user_games`)
- **Feito por** — perfil e links (`app/author.py` → GitHub `ersjunior`)

### API REST (multi-loteria)

Rotas canônicas usam `lottery_key`. Aliases sem path key continuam apontando para a **Mega-Sena**.

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Status da API, banco e cache |
| `GET` | `/lotteries` | Catálogo + cache por modalidade |
| `POST` | `/lotteries/{key}/verify` | Verificar jogo |
| `GET` | `/lotteries/{key}/combinations?n=` | Combinações inéditas |
| `GET` | `/lotteries/{key}/forecast?n=` | Alias de combinations |
| `GET` / `POST` | `/lotteries/{key}/dataset` | Metadados / atualizar via scraper |
| `POST` | `/verify/` | Alias Mega-Sena |
| `GET` | `/combinations/`, `/forecast/` | Aliases Mega-Sena |
| `GET` / `POST` | `/dataset/` | Aliases Mega-Sena |

Swagger: http://localhost:8000/docs · CORS, rate limit e validação Pydantic configuráveis.

### Persistência

| Item | Valor |
|------|--------|
| Arquivo padrão | `app/data/loterias.db` |
| Env | `LOTTERIAS_DB_PATH` |
| Tabelas | `draws`, `lottery_metadata`, `user_games` |

O **XLSX da Caixa** é só formato de **ingestão** (upload na Home ou `POST .../dataset`). A leitura operacional é sempre pelo SQLite.

---

## Como utilizar (caminho feliz)

1. **Obtenha o XLSX oficial** em https://loterias.caixa.gov.br/ (ou use o scraper da API).
2. **Home → sidebar** — upload do arquivo na loteria correta; confira **Status das Bases**.
3. **Controles (sidebar)** — escolha modalidade e tema; a preferência permanece ao navegar.
4. Explore **Estatísticas**, **Verificação**, **Combinações** e **Histórico**.

Alternativa API: `POST /lotteries/{key}/dataset` (ou `POST /dataset/` para Mega-Sena) popula o mesmo banco.

Guia completo: [docs/COMO_EXECUTAR.md](docs/COMO_EXECUTAR.md).

---

## Estrutura do projeto

```
├── .github/workflows/          # ci.yml (lint/testes) · docker.yml (build + smoke API)
├── .streamlit/                 # config.toml (tema de boot) · secrets.toml.example
├── api/                        # FastAPI multi-loteria
│   ├── main.py
│   ├── deps.py · config.py · schemas.py · limiter.py
│   ├── routes/                 # health, lotteries, verify, combinations, forecast, dataset
│   └── services/core.py
├── loterias_core/              # Domínio compartilhado
│   ├── lotteries.py · dataset.py · repository.py · storage.py
│   ├── statistics.py · generator.py · validator.py · scraper.py
│   ├── combinatorics.py · expected_value.py · schema.py · user_history.py
├── app/                        # Streamlit
│   ├── Home.py · author.py · config.py
│   ├── pages/                  # Estatísticas · Verificação · Combinações · Feito por · Histórico
│   ├── services/               # Camada fina sobre o core (+ report PDF)
│   ├── ui/                     # shell · lottery_selector · theme · theme_manager
│   ├── combinations/           # Wrapper do gerador
│   └── data/                   # loterias.db em runtime (gitignored)
├── docker/                     # Dockerfile.api · Dockerfile.streamlit · entrypoint.sh
├── docs/                       # COMO_EXECUTAR · ARCHITECTURE_NOTES
├── scripts/smoke_api.py
├── tests/                      # fixtures + cobertura de domínio/API/UI services
├── docker-compose.yml
├── pyproject.toml
└── requirements*.txt           # Atalhos: -e . / .[api] / .[dev]
```

Arquitetura detalhada: [docs/ARCHITECTURE_NOTES.md](docs/ARCHITECTURE_NOTES.md).

---

## Tecnologias

Python 3.11+ · Streamlit · FastAPI / Uvicorn · Pandas / NumPy · Plotly · ReportLab · SQLite · Ruff / mypy / pytest / pre-commit · Docker Compose

---

## Variáveis de ambiente

```bash
cp .env.example .env          # Linux/macOS
copy .env.example .env        # Windows
```

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `LOTTERIAS_DB_PATH` | `app/data/loterias.db` | SQLite compartilhado (Streamlit + API) |
| `LOG_LEVEL` | `INFO` | Nível de log da API |
| `ENVIRONMENT` | `development` | `production` restringe CORS se `CORS_ORIGINS` vazio |
| `CORS_ORIGINS` | *(vazio)* | Origens permitidas, separadas por vírgula |
| `MAX_BODY_BYTES` | `10240` | Limite de payload HTTP |
| `MAX_FORECAST_N` | `100` | Máximo de `n` em forecast/combinations |
| `RATE_LIMIT_DATASET` | `3/hour` | Rate limit de `POST .../dataset` |
| `RATE_LIMIT_FORECAST` | `30/minute` | Rate limit de forecast |
| `RATE_LIMIT_COMBINATIONS` | `60/minute` | Rate limit de combinations |

No Streamlit Community Cloud, use secrets (veja [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example)); `app/config.py` aplica `LOTTERIAS_DB_PATH` na inicialização.

---

## Execução

### Docker (recomendado)

```bash
docker compose up --build
```

| Serviço | URL |
|---------|-----|
| Streamlit | http://localhost:8501 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

Volume `apostas-data` persiste `loterias.db`. Tema de boot vem de `.streamlit/config.toml` embutido na imagem Streamlit; o seletor de tema na sidebar ajusta cores em runtime via CSS.

```bash
docker compose up --build streamlit   # só UI
docker compose up --build api         # só API
```

### Local (sem Docker)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate  ·  Linux/macOS: source .venv/bin/activate
pip install -e ".[dev,api]"
cp .env.example .env                  # opcional
pre-commit install                    # opcional
streamlit run app/Home.py
```

API:

```bash
uvicorn api.main:app --reload
```

### Qualidade

```bash
ruff check .
ruff format --check .
pytest
pytest --cov --cov-report=term-missing   # limiar 60%
mypy app api loterias_core
```

### Smoke da API

```bash
python scripts/smoke_api.py
API_BASE_URL=https://sua-api.exemplo.com python scripts/smoke_api.py
```

Exige `GET /health` (`status=ok`) e `GET /lotteries` (lista não vazia). O workflow Docker executa o mesmo smoke após subir o container.

---

## CI

| Workflow | Função |
|----------|--------|
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Ruff, mypy, pytest + cobertura (Python 3.11 e 3.12) |
| [`.github/workflows/docker.yml`](.github/workflows/docker.yml) | Build das imagens + smoke live da API |

---

## Deploy

### Streamlit Community Cloud (somente UI)

1. Publique o repositório no GitHub.
2. Em [share.streamlit.io](https://share.streamlit.io/) → **New app** → main file `app/Home.py`, Python 3.11+.
3. Secrets (exemplo):

```toml
LOTTERIAS_DB_PATH = "app/data/loterias.db"
```

4. No primeiro acesso, faça upload do XLSX na sidebar da Home.

A **API FastAPI não sobe** no Community Cloud — use Docker Compose ou um PaaS separado.

### API (Docker / PaaS)

```bash
docker compose up --build api
# ou a stack completa:
docker compose up --build
```

---

## Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md). Templates de issue/PR em [`.github/`](.github/). Histórico: [CHANGELOG.md](CHANGELOG.md).

---

## Aviso legal e jogo responsável

Projeto **estritamente educacional**. Loterias são jogos de azar; estatística histórica **não prevê** o próximo sorteio.

Apoio: [Jogadores Anônimos](https://jogadoresanonimos.com.br/) · CVV **188**.

Todas as páginas Streamlit exibem o rodapé de jogo responsável.

---

## Feito por

**Eliezer Junior**

- LinkedIn: https://www.linkedin.com/in/eliezer-junior/
- GitHub: https://github.com/ersjunior

Identidade centralizada em [`app/author.py`](app/author.py).

---

## Roadmap (estado atual)

- [x] API REST multi-loteria (FastAPI) + aliases Mega-Sena
- [x] Docker Compose + smoke live da API
- [x] CI (lint, testes, cobertura)
- [x] Domínio `loterias_core` + SQLite unificado
- [x] Histórico local de jogos (`user_games`)
- [x] Sidebar global (loteria + tema) e análises específicas por modalidade
- [x] PDF nas Estatísticas (com fallback sem Kaleido)
- [x] Scaffolding Streamlit Community Cloud (UI)

Ideias futuras (não comprometidas): mês da sorte no Dia de Sorte, seções especiais no PDF, PaaS da API documentado ponta a ponta.

---

Se este projeto foi útil, deixe uma estrela no GitHub.
