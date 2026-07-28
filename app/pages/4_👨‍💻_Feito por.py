import sys
from pathlib import Path

# Adicionar o diretório raiz ao Python path
root_dir = Path(__file__).parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import requests
import streamlit as st

from app.author import DISPLAY_NAME, GITHUB_URL, GITHUB_USER, LINKEDIN_URL
from app.ui.shell import render_app_chrome
from app.ui.theme import card, page_title, responsible_gaming_footer, section

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Feito por", layout="wide")

render_app_chrome()

# =========================
# TÍTULO
# =========================
page_title("👨‍💻 Feito por", "Quem está por trás deste projeto")

# =========================
# PERFIL
# =========================
section("👋 Sobre mim")

st.markdown(
    f"""
    Sou **{DISPLAY_NAME}**, profissional de dados com forte atuação em:

    - 📊 **Engenharia de Dados**
    - 🧠 **Inteligência Artificial**
    - 📈 **Análise de Dados e BI**
    - ☁️ **Arquiteturas em Cloud (AWS & GCP)**

    Este projeto foi desenvolvido com foco **educacional, analítico e técnico**,
    aplicando conceitos reais usados no mercado.
    """
)

# =========================
# LINKS PROFISSIONAIS
# =========================
section("🔗 Conecte-se comigo")
st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    card(
        "🐙 GitHub",
        "Projetos, códigos e estudos técnicos",
    )
    st.link_button("Acessar GitHub", GITHUB_URL, use_container_width=True)

with col2:
    card(
        "💼 LinkedIn",
        "Experiência profissional e trajetória",
    )
    st.link_button("Acessar LinkedIn", LINKEDIN_URL, use_container_width=True)

# =========================
# DADOS DO GITHUB (API)
# =========================
section("📦 Atividade no GitHub")
st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

try:
    response = requests.get(f"https://api.github.com/users/{GITHUB_USER}", timeout=5)
    response.raise_for_status()
    gh = response.json()

    c1, c2, c3 = st.columns(3)

    with c1:
        card("📁 Repositórios Publicos", str(gh.get("public_repos", "—")))

    with c2:
        card("⭐ Seguidores", str(gh.get("followers", "—")))

    with c3:
        card("👥 Seguindo", str(gh.get("following", "—")))

except Exception:
    st.warning("Não foi possível carregar os dados do GitHub no momento.")

# =========================
# EXPERIÊNCIA RESUMIDA
# =========================
section("🧠 Experiência Profissional (Resumo)")

st.markdown(
    """
    **Principais áreas de atuação:**

    - 🏦 **Financeiro / Bancos**
      Análises de dados, regras de negócio, produtos financeiros e cartões.

    - 🛒 **Varejo & Logística**
      Engenharia de dados, pipelines, métricas operacionais e performance.

    - 🌱 **Agronegócio**
      Estruturação de dados, analytics e suporte à decisão.

    - 📊 **BI & Analytics**
      Power BI, DAX, modelagem dimensional e storytelling com dados.
    """
)

# =========================
# STACK TÉCNICA
# =========================
section("⚙️ Stack Técnica")

st.markdown(
    """
    - **Linguagens:** Python, SQL
    - **Dados:** Pandas, NumPy, Spark
    - **Orquestração:** Airflow
    - **Cloud:** AWS, GCP
    - **BI:** Power BI, DAX
    - **Apps & Dashboards:** Streamlit
    """
)

# =========================
# MENSAGEM FINAL
# =========================
section("🚀 Considerações finais")

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
st.info(
    """
    Este projeto reflete **boas práticas de engenharia**, foco em qualidade,
    organização de código e experiência do usuário.

    Fique à vontade para explorar, estudar e adaptar.
    """
)

responsible_gaming_footer()
