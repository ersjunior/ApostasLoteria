
# 🎰 Loterias Analyzer

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Status](https://img.shields.io/badge/Status-Ativo-success)
![License](https://img.shields.io/badge/License-MIT-green)

> **Análise estatística, verificação de jogos e geração de combinações inéditas para loterias brasileiras**, utilizando dados oficiais da Caixa Econômica Federal.

Uma plataforma **educacional e analítica** para estudo de loterias brasileiras, baseada em dados oficiais da Caixa Econômica Federal.

> ⚠️ **Aviso:** Este projeto **não garante prêmios**. Todos os sorteios são eventos aleatórios.

---

## 📌 Visão Geral

O **Loterias Analyzer** é uma aplicação **educacional e analítica**, desenvolvida em **Python + Streamlit**, projetada para estudar jogos de loteria de forma estruturada, clara e extensível.

O projeto oferece:

- 🔍 Verificação de jogos históricos  
- 🔮 Geração de combinações inéditas (forecast)  
- 📊 Estatísticas interativas com gráficos  
- 💰 Simulação de custos e probabilidades reais  
- 📄 Exportação de relatórios e dados  

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

### 🔮 Forecast (combinações inéditas)
- Geração de jogos nunca sorteados
- Respeita regras específicas de cada loteria
- Exportação em CSV

### 📊 Estatísticas Interativas
- Frequência histórica das dezenas
- Probabilidade empírica
- Top & Bottom dezenas (dinâmico)
- Gráficos interativos com Plotly
- Simulação de custos e probabilidades

### 📄 Relatórios
- Exportação de jogos em CSV (página Forecast)

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
3. Confira **"📂 Status das Bases"** na Home (✅ = base carregada)

Cada loteria é salva em `app/data/<Nome da Loteria>.xlsx` (ex.: `app/data/Mega-Sena.xlsx`).

⚠️ Use apenas arquivos oficiais da Caixa.

---

### 2️⃣ bis — Atualização via API (opcional, só Mega-Sena)

Se você usar a **API FastAPI** em vez da interface, o dataset é outro arquivo: `app/data/megasena.csv`. Execute `POST /dataset/` em http://localhost:8000/docs para baixar a Mega-Sena automaticamente. Esse fluxo **não** substitui o upload XLSX do Streamlit.

---

### 3️⃣ Verificação
- Vá até **🎯 Verificação**
- Selecione a loteria e insira seus jogos
- Veja se já foram sorteados

---

### 4️⃣ Forecast
- Vá até **🔮 Forecast**
- Gere combinações inéditas
- Exporte os resultados em CSV

---

### 5️⃣ Estatísticas
- Vá até **📊 Estatísticas**
- Explore gráficos, probabilidades e custos

---

## 🏗️ Estrutura do Projeto

```
├── api/                            # API REST (FastAPI)
│   ├── routes/
│   └── services/
├── app/                            # Aplicação Streamlit
│   ├── core/
│   │   └── lotteries.py
│   ├── data/                       # Bases XLSX (upload) e CSV da API
│   │   ├── .gitkeep
│   │   ├── Mega-Sena.xlsx          # um XLSX por loteria (gerado no upload)
│   │   ├── Lotofácil.xlsx
│   │   └── …
│   ├── ml/
│   │   └── forecast.py
│   ├── pages/
│   │   ├── 1_📊_Estatísticas.py
│   │   ├── 2_🎯_Verificação.py
│   │   ├── 3_🔮_Forecast.py
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
├── docker/                         # Dockerfiles
│        ├── Dockerfile.api
│        └── Dockerfile.streamlit
├── docker-compose.yml              # Orquestra Streamlit + API
├── tests/                          # Testes automatizados
|        ├── test_forecast.py
|        ├── test_statistics.py
|        └── test_validator.py
├── pytest.ini
├── docs/                           # Documentação complementar
│        ├── ARCHITECTURE_NOTES.md
│        ├── COMO_EXECUTAR.md
│        └── README.md
├── requirements.txt
├── requirements-api.txt
└── README.md
```

---

## ⚙️ Tecnologias

- 🐍 Python 3.11+
- 🎨 Streamlit
- 📊 Pandas & NumPy
- 📈 Plotly
- 📄 ReportLab
- 📁 XLSX oficiais da Caixa

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

# instalar dependências
pip install -r requirements.txt

# interface web
streamlit run app/Home.py
```

Para a API localmente, instale também `pip install -r requirements-api.txt` e execute `uvicorn api.main:app --reload` a partir da raiz do projeto. Detalhes adicionais em [docs/COMO_EXECUTAR.md](docs/COMO_EXECUTAR.md).

Mais documentação em [docs/](docs/README.md) (arquitetura, guias complementares).

---

## ⚠️ Aviso Legal

Este projeto é **educacional**.  
Jogos de loteria são eventos **aleatórios**.  
Nenhuma análise estatística garante prêmio.

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
- [ ] Histórico de jogos do usuário
- [ ] Cache avançado por loteria
- [ ] Deploy em cloud (Streamlit Cloud / cloud provider)

---

⭐ Se este projeto foi útil, deixe uma estrela no GitHub!
