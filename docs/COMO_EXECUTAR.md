# 🚀 Guia de Execução do Projeto

## Pré-requisitos

- Python 3.11 ou superior instalado
- pip (geralmente vem com Python)

## Passo 1: Ativar o Ambiente Virtual

Se você já tem um ambiente virtual criado:

**Windows:**
```powershell
.env\Scripts\activate
```

**Linux/Mac:**
```bash
source .env/bin/activate
```

Se ainda não criou o ambiente virtual:
```bash
python -m venv .env
```
E depois ative conforme acima.

## Passo 2: Instalar Dependências

Instale todas as dependências necessárias:

```bash
pip install -r requirements.txt
```

## Passo 3: Executar a Aplicação Streamlit

```bash
streamlit run app/main.py
```

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`

### Primeira Execução - Importante! ⚠️

Na primeira vez que executar:

1. A aplicação vai abrir mostrando um aviso de que o dataset não foi encontrado
2. Na **barra lateral esquerda**, clique no botão **"🔄 Atualizar Dataset"**
3. Aguarde alguns segundos enquanto os dados são baixados da Caixa Econômica Federal
4. Após o download, você verá a mensagem "Base atualizada com sucesso!"
5. Agora você pode navegar pelas páginas:
   - **🎯 Verificação de Jogos** - Verifica se um jogo já foi sorteado
   - **🔮 Previsão de Jogos** - Gera previsões usando ML
   - **📊 Estatísticas** - Visualiza frequências e probabilidades

---

## Opção 2: API REST (FastAPI)

### Passo 1: Instalar Dependências da API

```bash
pip install -r requirements-api.txt
```

### Passo 2: Executar a API

**A partir da raiz do projeto:**
```bash
uvicorn api.main:app --reload
```

**Ou se preferir, a partir do diretório api:**
```bash
cd api
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`

### Passo 3: Acessar a Documentação Interativa

Abra no navegador:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Primeira Execução da API ⚠️

Antes de usar os endpoints, você precisa criar o dataset:

1. Acesse: http://localhost:8000/docs
2. Encontre o endpoint `POST /dataset/`
3. Clique em "Try it out" e depois em "Execute"
4. Isso vai baixar e criar o arquivo CSV necessário

### Endpoints Disponíveis:

- **POST /verify/** - Verificar se um jogo foi sorteado
  ```json
  {
    "numbers": [1, 5, 12, 23, 34, 56]
  }
  ```

- **GET /forecast/?n=10** - Gerar previsões (n = número de jogos)

- **GET /dataset/** - Informações sobre o dataset

- **POST /dataset/** - Atualizar o dataset

---

## 🐳 Opção 3: Usando Docker

### Streamlit:

```bash
docker build -f docker/Dockerfile.streamlit -t megasena-streamlit .
docker run -p 8501:8501 megasena-streamlit
```

### API:

```bash
docker build -f docker/Dockerfile.api -t megasena-api .
docker run -p 8000:8000 megasena-api
```

---

## 🧪 Executar Testes

Para executar os testes unitários:

```bash
pytest
```

Ou com mais detalhes:

```bash
pytest -v
```

---

## ❓ Solução de Problemas

### Erro: "Dataset não encontrado"

**Solução:** Clique no botão "🔄 Atualizar Dataset" na barra lateral (Streamlit) ou execute `POST /dataset/` (API)

### Erro: "ModuleNotFoundError"

**Solução:** Verifique se todas as dependências foram instaladas:
```bash
pip install -r requirements.txt
```

### Erro ao executar Streamlit

**Solução:** Certifique-se de estar na raiz do projeto:
```bash
streamlit run app/Home.py
```

### Porta já em uso

**Solução:** Use outra porta:
```bash
streamlit run app/Home.py --server.port 8502
```

Ou para a API:
```bash
uvicorn api.Home:app --reload --port 8001
```

---

## 📝 Notas Importantes

- O dataset é armazenado em `app/data/dfs.xlsx`
- O dataset é atualizado automaticamente quando você clica em "Atualizar Dataset"
- As previsões são baseadas em machine learning e **NÃO garantem resultados reais**
- Este projeto é apenas para fins educacionais
