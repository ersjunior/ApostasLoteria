# ARCHITECTURE_NOTES — ApostasLoteria

Documento gerado por inspeção estática do repositório (sem alteração de lógica de negócio).
Data de referência: julho/2026.

---

## 1. Árvore de arquivos (real)

Ignorados: `.venv`, `__pycache__`, `.git`, `node_modules`, `.env` (venv local).

```
ApostasLoteria/
├── .dockerignore
├── .gitignore
├── .streamlit/
│   └── config.toml
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dataset.py
│   │   ├── forecast.py
│   │   └── verify.py
│   └── services/
│       ├── __init__.py
│       └── core.py
├── app/
│   ├── __init__.py
│   ├── Home.py
│   ├── core/
│   │   └── lotteries.py
│   ├── data/
│   │   ├── .gitkeep
│   │   ├── reports/
│   │   │   └── megasena_relatorio_estatistico.pdf
│   │   ├── +Milionária.xlsx
│   │   ├── Dia de Sorte.xlsx
│   │   ├── Dupla Sena.xlsx
│   │   ├── Lotofácil.xlsx
│   │   ├── Lotomania.xlsx
│   │   ├── Mega-Sena.xlsx
│   │   ├── Quina.xlsx
│   │   ├── Super Sete.xlsx
│   │   └── Timemania.xlsx          # *.xlsx existem localmente; .gitignore ignora *.xlsx
│   ├── ml/
│   │   ├── __init__.py
│   │   └── forecast.py
│   ├── pages/
│   │   ├── 1_📊_Estatísticas.py
│   │   ├── 2_🎯_Verificação.py
│   │   ├── 3_🔮_Forecast.py
│   │   └── 4_👨‍💻_Feito por.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── dataset.py
│   │   ├── exporter.py
│   │   ├── report.py
│   │   ├── scraper.py
│   │   ├── statistics.py
│   │   └── validator.py
│   └── ui/
│       ├── lottery_selector.py
│       ├── theme.py
│       └── theme_manager.py
├── docker/
│   ├── Dockerfile.api
│   └── Dockerfile.streamlit
├── docs/
│   ├── ARCHITECTURE_NOTES.md
│   ├── COMO_EXECUTAR.md
│   └── README.md
├── tests/
│   ├── __init__.py
│   ├── test_forecast.py
│   ├── test_statistics.py
│   └── test_validator.py
├── docker-compose.yml
├── LICENSE
├── pytest.ini
├── README.md
├── requirements.txt
└── requirements-api.txt
```

**Observações da árvore**

- Não existe `app/main.py`.
- Não existe `api/Home.py`.
- `requirements.txt` existe na raiz (contrário ao que alguns globs iniciais sugeriram).
- Pacotes `app/`, `api/`, `app/ml/`, `app/services/` têm `__init__.py` vazios.

---

## 2. Inventário por módulo

### `app/` (raiz do pacote)

| Arquivo | O que faz | Público | Dependências importadas |
|---------|-----------|---------|-------------------------|
| `__init__.py` | Marcador de pacote Python | — | — |
| `Home.py` | Página inicial Streamlit: hero, cards, upload manual de XLSX na sidebar, status das bases | execução top-level (`st.*`) | `sys`, `pandas`, `streamlit`, `pathlib`; `app.core.lotteries.LOTTERIES`; `app.ui.theme`; `app.ui.theme_manager`; `app.services.dataset.normalize_columns`, `enrich_dataset` |

### `app/core/`

| Arquivo | O que faz | Público | Dependências |
|---------|-----------|---------|--------------|
| `lotteries.py` | Catálogo `LOTTERIES`: metadados por loteria (bolas, universo, preços, `file_path`) | `LOTTERIES` (dict) | `app.services.dataset.load_dataset` (**importado mas não usado** no arquivo) |

### `app/services/`

| Arquivo | O que faz | Público | Dependências |
|---------|-----------|---------|--------------|
| `dataset.py` | Leitura/normalização/enriquecimento de XLSX; handlers especiais (Lotomania, Super Sete, +Milionária, Dupla Sena); cache Streamlit | `normalize_columns`, `enrich_dataset`, `handle_lotomania`, `handle_supersete`, `handle_mais_milionaria`, `load_dataset_internal`, `load_dataset`, `save_dataset` | `os`, `pandas`, `streamlit`, `pathlib`, `openpyxl` |
| `validator.py` | Verifica se combinação já existe no histórico (com suporte a campos extras) | `check_game` | — |
| `statistics.py` | Frequência e probabilidade empírica por dezena | `frequency`, `empirical_probability`, `frequency_by_period` | `pandas` |
| `forecast.py` (em `app/ml/`) | — | — | — |
| `scraper.py` | Download do XLSX oficial da Mega-Sena via URL estática | `download_megasena_data` | `pandas`, `requests`, `io.BytesIO` |
| `exporter.py` | Serializa lista de jogos para CSV (bytes UTF-8) | `export_csv` | `pandas` |
| `report.py` | Gera PDF estatístico com ReportLab + gráficos Plotly | `generate_statistics_pdf`, `_plotly_to_image` | `io`, `tempfile`, `reportlab.*`, `plotly`, `app.services.statistics` |
| `cache.py` | Wrapper cacheado de `load_dataset` (sem parâmetros) | `load_dataset_cached` | `streamlit`, `app.services.dataset.load_dataset` |

**Módulos aparentemente não referenciados por outras partes do app:** `cache.py`, `report.py` (`save_dataset` em `dataset.py` também não é chamado — `Home.py` grava com `df.to_excel` direto).

### `app/ml/`

| Arquivo | O que faz | Público | Dependências |
|---------|-----------|---------|--------------|
| `forecast.py` | Gera N combinações aleatórias inéditas (não usa scikit-learn) | `generate_forecast_games` | `random` |

### `app/ui/`

| Arquivo | O que faz | Público | Dependências |
|---------|-----------|---------|--------------|
| `theme.py` | Componentes visuais HTML (título, seção, cards, métricas) | `page_title`, `section`, `metric_card` (definido 2×), `game_card`, `card`, `status_message` | `streamlit`, `app.ui.theme_manager.get_theme` |
| `theme_manager.py` | Tema claro/escuro via CSS injetado | `THEMES`, `init_theme`, `toggle_theme`, `get_theme`, `apply_theme` | `streamlit` |
| `lottery_selector.py` | Selectbox de loteria reutilizável | `lottery_selector` | `streamlit`, `app.core.lotteries.LOTTERIES` (**não importado em nenhuma página**) |

### `app/pages/`

| Arquivo | O que faz | Público | Dependências |
|---------|-----------|---------|--------------|
| `1_📊_Estatísticas.py` | Dashboard estatístico: KPIs, probabilidade combinatória, gráficos Plotly | execução top-level | `sys`, `math.comb`, `pathlib`, `streamlit`, `pandas`, `plotly`; `app.core.lotteries`; `app.services.dataset`, `statistics`; `app.ui.*` |
| `2_🎯_Verificação.py` | Entrada de até 3 jogos e verificação contra histórico | execução top-level | `sys`, `streamlit`, `pathlib`; `app.core.lotteries`; `app.services.dataset`, `validator`; `app.ui.*` |
| `3_🔮_Forecast.py` | Gera 10 jogos inéditos e exporta CSV | execução top-level | `sys`, `pathlib`, `streamlit`; `app.core.lotteries`; `app.services.dataset`, `exporter`; `app.ml.forecast`; `app.ui.*` |
| `4_👨‍💻_Feito por.py` | Página “sobre”; busca perfil GitHub via HTTP | execução top-level | `sys`, `pathlib`, `streamlit`, `requests`; `app.ui.*` |

### `api/`

| Arquivo | O que faz | Público | Dependências |
|---------|-----------|---------|--------------|
| `main.py` | Instancia FastAPI e monta routers | `app` (instância FastAPI) | `fastapi`; `api.routes.verify`, `forecast`, `dataset` |
| `routes/verify.py` | `POST /verify/` — validação Mega-Sena hardcoded | `router`, `Game` (Pydantic), `verify` | `fastapi`, `pydantic`; `api.services.core.load_dataset`; `app.services.validator.check_game` |
| `routes/forecast.py` | `GET /forecast/` — gera jogos inéditos Mega-Sena | `router`, `forecast` | `fastapi`; `api.services.core.load_dataset`; `app.ml.forecast.generate_forecast_games` |
| `routes/dataset.py` | `GET/POST /dataset/` — info e atualização do dataset | `router`, `get_dataset_info`, `update_dataset_endpoint` | `fastapi`; `api.services.core.load_dataset`, `update_dataset` |
| `services/core.py` | Loader/atualizador CSV Mega-Sena; wrappers legados | `DATASET_PATH`, `load_dataset`, `update_dataset`, `verify_game`, `forecast_games` | `pandas`, `os`; `app.services.scraper`; `app.services.validator`; `app.ml.forecast` |

---

## 3. Respostas às 6 perguntas obrigatórias

### 3.1 Entrypoint do Streamlit: `app/main.py`, `app/Home.py`, ou ambos?

**Somente `app/Home.py`.** `app/main.py` **não existe**.

Evidências:

```22:22:docker/Dockerfile.streamlit
CMD ["streamlit", "run", "app/Home.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

O multipage do Streamlit usa `app/Home.py` como script principal e descobre páginas em `app/pages/`.

`COMO_EXECUTAR.md` documenta os entrypoints corretos (`streamlit run app/Home.py`, `uvicorn api.main:app`), venv `.venv` e os dois fluxos de ingestão (upload XLSX vs `POST /dataset/` da API).

---

### 3.2 O Streamlit consome a API (HTTP) ou reimplementa localmente?

**Reimplementa localmente.** As páginas importam diretamente `app.services.*` e `app.ml.*`.

Exemplo — verificação:

```12:13:app/pages/2_🎯_Verificação.py
from app.services.dataset import load_dataset
from app.services.validator import check_game
```

Exemplo — forecast:

```12:13:app/pages/3_🔮_Forecast.py
from app.services.dataset import load_dataset
from app.ml.forecast import generate_forecast_games
```

**Única chamada HTTP no app Streamlit:** API pública do GitHub na página “Feito por” (`requests.get("https://api.github.com/users/...")`), não a FastAPI local.

A API FastAPI, por sua vez, **reutiliza** módulos de `app/` (`check_game`, `generate_forecast_games`), mas o Streamlit **não** chama `localhost:8000`.

---

### 3.3 Onde e com que nome o dataset é gravado em disco?

Há **dois modelos de persistência distintos**:

#### Streamlit (fluxo principal, multi-loteria)

Caminhos definidos em `LOTTERIES` — um XLSX por loteria em `app/data/`:

```15:15:app/core/lotteries.py
        "file_path": "app/data/Mega-Sena.xlsx",
```

```45:45:app/core/lotteries.py
        "file_path": "app/data/Lotofácil.xlsx",
```

Upload manual em `Home.py` grava no `file_path` da loteria selecionada:

```204:204:app/Home.py
        df.to_excel(config["file_path"], index=False)
```

Lotérias configuradas (todas sob `app/data/`): `Mega-Sena.xlsx`, `Lotofácil.xlsx`, `Quina.xlsx`, `Dupla Sena.xlsx`, `Lotomania.xlsx`, `Dia de Sorte.xlsx`, `Timemania.xlsx`, `Super Sete.xlsx`, `+Milionária.xlsx`.

`.gitignore` ignora `app/data/*.xlsx` (mantém só `.gitkeep`).

**Não existe** `app/data/dfs.xlsx` nem `datasets.xlsx` no código — isso aparece apenas como documentação incorreta em `COMO_EXECUTAR.md` (linha 185).

#### API FastAPI (fluxo legado Mega-Sena)

```15:15:api/services/core.py
DATASET_PATH = "app/data/megasena.csv"
```

`POST /dataset/` baixa XLSX via scraper, transforma e salva CSV:

```50:51:api/services/core.py
    os.makedirs(os.path.dirname(DATASET_PATH), exist_ok=True)
    df.to_csv(DATASET_PATH, index=False)
```

**Inconsistência:** UI trabalha com XLSX por loteria; API espera `megasena.csv` com colunas `bola_1`…`bola_6` e coluna `jogo` derivada — formato diferente do pipeline `load_dataset` do Streamlit.

---

### 3.4 Entrypoint da API e rotas existentes

**Entrypoint:** `api/main.py`, executado como `uvicorn api.main:app` (ver `docker/Dockerfile.api` e `COMO_EXECUTAR.md`).

```1:8:api/main.py
from fastapi import FastAPI
from api.routes import verify, forecast, dataset

app = FastAPI()

app.include_router(verify.router, prefix="/verify")
app.include_router(forecast.router, prefix="/forecast")
app.include_router(dataset.router, prefix="/dataset")
```

| Método | Rota | Handler | Comportamento resumido |
|--------|------|---------|------------------------|
| `POST` | `/verify/` | `verify.verify` | Body JSON `{ "numbers": [int, ...] }`; exige 6 números entre 1–60 (Mega-Sena fixa) |
| `GET` | `/forecast/` | `forecast.forecast` | Query `n` (1–100); gera jogos inéditos Mega-Sena (`total_bolas=6`, `universo=60`) |
| `GET` | `/dataset/` | `dataset.get_dataset_info` | Retorna `total_records`, `columns` do CSV |
| `POST` | `/dataset/` | `dataset.update_dataset_endpoint` | Baixa Mega-Sena e regrava `app/data/megasena.csv` |

Não há rota raiz `/` nem health check explícito. Docs automáticas: `/docs`, `/redoc`.

---

### 3.5 Lógica de domínio duplicada entre `app/` e `api/`

| Área | Situação |
|------|----------|
| **Verificação (`check_game`)** | **Compartilhada** — `api/routes/verify.py` importa `app.services.validator.check_game`. Sem duplicação da função core. Porém a **validação de entrada** na rota (6 dezenas, 1–60) está duplicada conceitualmente em relação à UI genérica multi-loteria em `2_🎯_Verificação.py`. |
| **Forecast (`generate_forecast_games`)** | **Compartilhada** — rota e página Streamlit usam `app.ml.forecast.generate_forecast_games`. A rota fixa parâmetros Mega-Sena; a UI passa `config` da loteria. |
| **Estatística** | **Só em `app/`** — `app/services/statistics.py` usado pela página Estatísticas e por `report.py`. API não expõe estatísticas. |
| **Carga de dataset** | **Duplicada / divergente** — Streamlit: `app/services/dataset.py` (XLSX, multi-loteria, handlers especiais, `@st.cache_data`). API: `api/services/core.py` (`pd.read_csv` de `megasena.csv`, pipeline de download separado). |
| **Wrappers em `api/services/core.py`** | `verify_game` e `forecast_games` repetem o que as rotas já fazem; comentário no arquivo admite possível obsolescência. |
| **Scraper** | Usado só pela API (`update_dataset` → `download_megasena_data`). Streamlit orienta upload manual em `Home.py`. |

**Testes desalinhados com o código atual (não é duplicação, mas dívida técnica):**

- `tests/test_forecast.py` importa `train_model`, `predict_games` — **não existem** em `app/ml/forecast.py`.
- `tests/test_statistics.py` chama `frequency(df)` sem `total_bolas`, mas a assinatura exige `total_bolas: int`.

---

### 3.6 Dependências pinadas e conflitos

| Arquivo | Pinagem | Conteúdo relevante |
|---------|---------|-------------------|
| `requirements.txt` | **Sim** — versões fixas (estilo `pip freeze`, 73 pacotes) | Inclui `streamlit==1.53.0`, `fastapi==0.128.0`, `pandas==2.3.3`, `scikit-learn==1.8.0`, etc. |
| `requirements-api.txt` | **Não** — apenas nomes de pacotes, sem versão | `fastapi`, `uvicorn[standard]`, `pydantic`, `pandas`, `numpy`, `scikit-learn`, `requests` |

**Sobreposição:** `fastapi`, `pydantic`, `pandas`, `numpy`, `scikit-learn`, `requests` aparecem nos dois arquivos.

**Conflito potencial:** `Dockerfile.api` instala **ambos** (`pip install -r requirements.txt -r requirements-api.txt`). Como `requirements-api.txt` não fixa versão, na prática as versões de `requirements.txt` prevalecem para pacotes já listados — mas `uvicorn[standard]` só está em `requirements-api.txt` (não pinado).

**Observação:** `scikit-learn` está nas dependências e nos testes antigos, mas `app/ml/forecast.py` atual usa apenas `random` (sem ML).

`requirements.txt` **não lista** `uvicorn` explicitamente (embora `fastapi` esteja presente).

---

## 4. Diagrama textual — fluxo de dados

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FONTE: Caixa Econômica Federal                        │
│              https://loterias.caixa.gov.br/ (XLSX por loteria)           │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
   [Upload manual]      [Scraper API]          (arquivos já
   Home.py sidebar      scraper.py              em app/data/)
   st.file_uploader     download_megasena_data
          │                     │
          ▼                     ▼
   app/data/*.xlsx       app/data/megasena.csv
   (por loteria,          (só Mega-Sena,
    paths em LOTTERIES)    só via API POST /dataset/)
          │                     │
          ▼                     │
   app/services/dataset.py      │
   normalize_columns           │
   enrich_dataset              │
   handlers especiais          │
   load_dataset (@cache)       │
          │                     │
          ├──────────┬──────────┤
          ▼          ▼          ▼
    validator   statistics   ml/forecast
    check_game  frequency    generate_forecast_games
                empirical_probability
          │          │          │
          ▼          ▼          ▼
   ┌──────────────────────────────────┐
   │     STREAMLIT (app/Home.py +      │
   │     app/pages/*.py)               │
   │  • Estatísticas (Plotly)          │
   │  • Verificação                    │
   │  • Forecast + export CSV          │
   │  • Feito por (GitHub API)         │
   └──────────────────────────────────┘

   ┌──────────────────────────────────┐
   │     FASTAPI (api/main.py)         │
   │  GET/POST /dataset/  ──► core.py │
   │  POST /verify/       ──► check_game (app)
   │  GET /forecast/      ──► generate_forecast_games (app)
   │  (Mega-Sena only, CSV)            │
   └──────────────────────────────────┘

          ▲
          │  NÃO há chamadas HTTP
          │  Streamlit → API
          └──────────────── (processos independentes)
```

**Docker Compose:** serviços `streamlit` (8501) e `api` (8000) compartilham volume `apostas-data` montado em `/app/app/data`.

---

## 5. Resumo executivo para refatoração

1. **Entrypoints canônicos:** Streamlit → `app/Home.py`; API → `api/main.py` (`uvicorn api.main:app`).
2. **Dois pipelines de dados** (XLSX multi-loteria vs CSV Mega-Sena) são a principal fonte de inconsistência.
3. **Domínio compartilhado** (`validator`, `forecast`) já vive em `app/`; API deveria alinhar loader de dataset ao mesmo módulo.
4. **Código morto / órfão:** `lottery_selector.py`, `cache.py`, `report.py`, `save_dataset`, wrappers em `api/services/core.py`.
5. **Documentação:** `README.md` e `COMO_EXECUTAR.md` alinhados aos entrypoints (`app/Home.py`, `uvicorn api.main:app`), venv `.venv`, Python 3.11+ e caminhos reais de dataset.
6. **Testes** não refletem implementação atual de forecast e statistics.
