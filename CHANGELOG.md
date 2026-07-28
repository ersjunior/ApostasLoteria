# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [1.0.0] - 2026-07-28

Release inicial completo: plataforma de análise estatística, verificação de jogos
e geração de combinações inéditas para as loterias brasileiras (Streamlit + API
FastAPI + núcleo de domínio `loterias_core` sobre SQLite).

### Added

- Persistência em **SQLite** (`app/data/loterias.db`) compartilhada entre Streamlit e API — elimina condição de corrida entre XLSX/CSV.
- Módulos `loterias_core/storage.py` e `loterias_core/repository.py` com cache incremental por modalidade (último concurso, última atualização).
- Import de XLSX oficial para popular o banco (upload manual mantido).
- Metadados de cache expostos em `GET /health` (`database`, `lotteries`) e na UI (Home — Status das Bases).
- Preparação para **Streamlit Community Cloud**: `.streamlit/secrets.toml.example`, `app/config.py` e seção Deploy no README.
- Testes de persistência SQLite e cache incremental (`tests/test_storage.py`).
- Exportação de relatório estatístico **PDF** na página Estatísticas (Gerar → Baixar).
- **Histórico de jogos do usuário** (tabela `user_games` no SQLite local): salvar em Verificação/Combinações, página **📜 Histórico**.
- Smoke live da API: `scripts/smoke_api.py` + job `api-smoke` no workflow Docker (container + `GET /health` / `GET /lotteries`).
- Análises específicas na página Estatísticas (+Milionária/trevos, Dupla Sena/sorteios, Super Sete/colunas, Timemania/Time do Coração) via `extra_field_frequency`, `frequency_by_draw` e `frequency_by_position` em `loterias_core.statistics`.
- Sidebar global (`app/ui/shell.py`): seletor de loteria e tema claro/escuro compartilhados entre as páginas Streamlit.

### Changed

- `persist_dataset()` e `update_dataset()` gravam no SQLite; API deixa de usar `megasena.csv`.
- Docker Compose: `LOTTERIAS_DB_PATH` e volume persistente para `loterias.db`.
- Páginas Streamlit carregam dados por `lottery_key` em vez de `file_path` XLSX.
- Ingestão de XLSX: `process_raw_dataset` processa DataFrame em memória (`build_dataset_from_dataframe`); sem staging Excel nem leitura duplicada em `load_dataset`.
- Cobertura pytest deixa de ser `addopts` obrigatório; use `pytest --cov` (CI e local com `[dev]`). Limiar em `[tool.coverage.report] fail_under = 60`.
- Atalho `requirements-dev.txt` (`-e ".[dev]"`).
- Componentes de UI (`card`, `status_message`, métricas) respeitam o tema ativo; CSS de sidebar/inputs no modo claro.
- Documentação alinhada ao estado atual: README, `docs/COMO_EXECUTAR.md`, `docs/ARCHITECTURE_NOTES.md`, `docs/README.md` e `.env.example` (API multi-loteria, SQLite, shell/tema, smoke).

### Fixed

- Imagem Docker Streamlit passa a incluir `.streamlit/config.toml` (tema/server); `secrets.toml` permanece fora do build via `.dockerignore`.
- Relatório PDF nas Estatísticas: geração continua com tabelas se Kaleido/Chrome estiver ausente (ex.: Docker slim).
- Removida leitura duplicada de Excel no caminho padrão de `load_dataset` e o round-trip `to_excel`/`read_excel` do upload.
- `pytest` local sem `pytest-cov` não falha mais por flags `--cov` injetadas no `addopts`.
- Link GitHub residual `eliezerjunior` no README alinhado a `ersjunior` (mesmo usuário da página Feito por / CI); identidade centralizada em `app/author.py`.

### Added (anterior)

- Pacote `loterias_core/` como fonte única de domínio (combinatória, estatística, validação, scraper, schema).
- API FastAPI com rotas `/health`, `/verify/`, `/combinations/`, `/forecast/` e `/dataset/`.
- Health check em `GET /health` com status do dataset Mega-Sena.
- CORS configurável via `CORS_ORIGINS`, rate limiting (SlowAPI) e validação Pydantic com erros `{detail, code}`.
- Logging estruturado da API (`LOG_LEVEL`, `ENVIRONMENT`).
- `pyproject.toml` com dependências pinadas, ruff, mypy, pytest-cov e pre-commit.
- CI GitHub Actions: lint (ruff), type-check (mypy), testes e cobertura (Python 3.11 e 3.12).
- Workflow Docker para build das imagens API e Streamlit.
- Healthchecks nos containers, usuário não-root e imagens slim.
- Testes ampliados: dataset, scraper, schema, cache, exporter, report, combinatorics e rotas da API.
- Rigor estatístico: teste qui-quadrado de uniformidade, valor esperado, combinatória correta por modalidade.
- Scraper com retry, timeout e fallback; validação de schema no upload e ingestão de dataset.
- Documentação open-source: `CONTRIBUTING.md`, templates GitHub, `.env.example` e nota de jogo responsável.

### Changed

- Refatoração: `app/` e `api/` passam a consumir `loterias_core/` em vez de duplicar lógica.
- Página Streamlit renomeada para **Combinações Inéditas** (sorteio aleatório, sem ML em produção).
- README e `docs/COMO_EXECUTAR.md` alinhados aos entrypoints e fluxos de dados atuais.
- Docker Compose: Streamlit e API independentes, volume compartilhado `apostas-data` em `app/data/`.

### Fixed

- Inconsistências de documentação (venv `.env` vs `.venv`, caminhos de dataset, endpoints).

### Security

- Limite de tamanho de payload HTTP (`MAX_BODY_BYTES`).
- CORS restrito em `ENVIRONMENT=production` quando `CORS_ORIGINS` não está definido.

## [0.1.0] - 2026-07-28

Versão inicial publicada: Streamlit, API FastAPI básica e Docker Compose.

[Unreleased]: https://github.com/ersjunior/ApostasLoteria/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ersjunior/ApostasLoteria/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/ersjunior/ApostasLoteria/releases/tag/v0.1.0
