# Contribuindo com o Loterias Analyzer

Obrigado por considerar contribuir com este projeto. Este guia descreve como configurar o ambiente, rodar testes, seguir o padrão de commits e abrir pull requests.

## Código de conduta

Seja respeitoso e construtivo. Este é um projeto **educacional** sobre loterias — não promovemos estratégias de “garantia de prêmio” nem conteúdo que incentive jogo irresponsável.

## Pré-requisitos

- Python **3.11** ou superior
- [Git](https://git-scm.com/)
- (Opcional) [Docker](https://docs.docker.com/get-docker/) e Docker Compose v2

## Configurar o ambiente

1. **Clone o repositório**

   ```bash
   git clone https://github.com/ersjunior/ApostasLoteria.git
   cd ApostasLoteria
   ```

2. **Crie e ative o ambiente virtual**

   ```powershell
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\activate
   ```

   ```bash
   # Linux/macOS
   python -m venv .venv
   source .venv/bin/activate
   ```

   > Use `.venv` para o ambiente virtual. O arquivo `.env` (copiado de `.env.example`) é reservado para variáveis de ambiente locais.

3. **Instale as dependências**

   ```bash
   pip install -e ".[dev,api]"
   ```

4. **Configure variáveis de ambiente (opcional)**

   ```bash
   cp .env.example .env
   ```

   Edite `.env` conforme necessário. A API lê essas variáveis em tempo de execução; o Streamlit não exige `.env` para uso básico.

5. **Instale os hooks de qualidade (recomendado)**

   ```bash
   pre-commit install
   ```

## Executar o projeto

### Streamlit (interface web)

```bash
streamlit run app/Home.py
```

Acesse http://localhost:8501. Na primeira execução, faça upload dos XLSX oficiais da Caixa pela barra lateral.

### API FastAPI

```bash
uvicorn api.main:app --reload
```

- Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Docker Compose

```bash
docker compose up --build
```

| Serviço   | URL                     |
|-----------|-------------------------|
| Streamlit | http://localhost:8501   |
| API       | http://localhost:8000   |

## Rodar testes e qualidade de código

Execute na raiz do repositório:

```bash
# Lint
ruff check .

# Formatação (verificar sem alterar)
ruff format --check .

# Testes com cobertura (mínimo 60%)
pytest

# Type-check gradual
mypy app api loterias_core
```

Para formatar automaticamente:

```bash
ruff format .
```

## Estrutura relevante para contribuições

| Pasta / módulo      | Responsabilidade                                      |
|---------------------|-------------------------------------------------------|
| `loterias_core/`    | Domínio puro (combinatória, estatística, validação)   |
| `app/`              | Interface Streamlit                                   |
| `api/`              | API REST FastAPI                                      |
| `tests/`            | Testes automatizados                                  |
| `docs/`             | Documentação complementar                             |

Regra geral: lógica de negócio nova deve ir em `loterias_core/`; `app/` e `api/` consomem esse módulo.

## Padrão de commit

Use [Conventional Commits](https://www.conventionalcommits.org/) em português ou inglês, no imperativo:

| Prefixo    | Uso                                      |
|------------|------------------------------------------|
| `feat:`    | Nova funcionalidade                      |
| `fix:`     | Correção de bug                          |
| `docs:`    | Documentação                             |
| `test:`    | Testes                                   |
| `refactor:`| Refatoração sem mudança de comportamento |
| `chore:`   | Manutenção (deps, CI, Docker)            |
| `ci:`      | Pipelines GitHub Actions                 |

Exemplos:

```
feat(api): adiciona endpoint de estatísticas por loteria
fix(app): corrige validação de Dupla Sena com dois sorteios
docs: atualiza README com variáveis de ambiente
test: cobre scraper com retry e timeout
```

## Abrir um Pull Request

1. Crie um branch a partir de `main`:

   ```bash
   git checkout -b feat/minha-contribuicao
   ```

2. Faça alterações focadas e inclua testes quando aplicável.

3. Garanta que passam localmente:

   ```bash
   ruff check .
   ruff format --check .
   pytest
   ```

4. Commit e push:

   ```bash
   git push -u origin feat/minha-contribuicao
   ```

5. Abra o PR no GitHub. O template pedirá descrição, tipo de mudança e plano de teste.

6. Aguarde o **CI** (lint, format, mypy, pytest com cobertura em Python 3.11 e 3.12).

### Checklist do revisor

- [ ] Código segue convenções do projeto (ruff, estrutura de pastas)
- [ ] Testes cobrem o comportamento alterado
- [ ] Documentação atualizada se necessário
- [ ] Sem credenciais ou dados sensíveis no diff
- [ ] Mensagens mantêm tom educacional e responsável

## Reportar bugs ou sugerir features

Use os templates em [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/):

- **Bug report** — passos para reproduzir, comportamento esperado vs. atual
- **Feature request** — problema que resolve, proposta e alternativas

## Dúvidas

Consulte também:

- [README.md](README.md) — visão geral e execução
- [docs/COMO_EXECUTAR.md](docs/COMO_EXECUTAR.md) — guia detalhado
- [docs/ARCHITECTURE_NOTES.md](docs/ARCHITECTURE_NOTES.md) — mapa do repositório
