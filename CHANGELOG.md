# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added

- Persistência em **SQLite** (`app/data/loterias.db`) compartilhada entre Streamlit e API — elimina condição de corrida entre XLSX/CSV.
- Módulos `loterias_core/storage.py` e `loterias_core/repository.py` com cache incremental por modalidade (último concurso, última atualização).
- Import de XLSX oficial para popular o banco (upload manual mantido).
- Metadados de cache expostos em `GET /health` (`database`, `lotteries`) e na UI (Home — Status das Bases).
- Preparação para **Streamlit Community Cloud**: `.streamlit/secrets.toml.example`, `app/config.py` e seção Deploy no README.
- Testes de persistência SQLite e cache incremental (`tests/test_storage.py`).

### Changed

- `persist_dataset()` e `update_dataset()` gravam no SQLite; API deixa de usar `megasena.csv`.
- Docker Compose: `LOTTERIAS_DB_PATH` e volume persistente para `loterias.db`.
- Páginas Streamlit carregam dados por `lottery_key` em vez de `file_path` XLSX.

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

[Unreleased]: https://github.com/ersjunior/ApostasLoteria/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ersjunior/ApostasLoteria/releases/tag/v0.1.0
