import streamlit as st
from aviso import send_email



# --- PAGE SETUP ---
about_page = st.Page(
    "views/about_me.py",
    title="Perfil",
    icon=":material/account_circle:",
    default=True,
)
project_1_page = st.Page(
    "views/dashboard.py",
    title="Dashboard",
    icon=":material/bar_chart:",
)
project_2_page = st.Page(
    "views/relatorio.py",
    title="Relatório",
    icon=":material/smart_toy:",
)
project_3_page = st.Page(
    "views/bayes.py",
    title="Naive Bayes - Movimentação Mercado",
    icon=":material/bar_chart:",
)
project_4_page = st.Page(
    "views/biblioteca_ml.py",
    title="Biblioteca de Machine Learning",
    icon=":material/smart_toy:",
)
project_5_page = st.Page(
    "views/biblioteca.py",
    title="Criação de Biblioteca",
    icon=":material/bar_chart:",
)
project_6_page = st.Page(
    "views/sisgrad.py",
    title="Sistema Selfservice gerador Relatório",
    icon=":material/smart_toy:",
)
project_7_page = st.Page(
    "views/alocacao.py",
    title="Modelo de alocação para Investimento",
    icon=":material/bar_chart:",
)
project_8_page = st.Page(
    "views/central_financas.py",
    title="Distribuição de Tarefas/Demandas",
    icon=":material/smart_toy:",
)
project_9_page = st.Page(
    "views/calculadora_inflacao.py",
    title="Calculadora de Rendimento com Inflação",
    icon=":material/bar_chart:",
)
project_10_page = st.Page(
    "views/agenda.py",
    title="Habit Tracker - Agenda",
    icon=":material/smart_toy:",
)
project_11_page = st.Page(
    "views/referencias.py",
    title="Referências",
    icon=":material/bar_chart:",
)




# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Info": [about_page],
        "Análise Descritiva": [project_1_page, project_2_page],
        "Análise Preditiva": [project_3_page, project_4_page],
        "Sistemas": [project_5_page, project_6_page,project_7_page, project_8_page],
        "Outros": [project_9_page, project_10_page],
        "Referências": [project_11_page],

    }
)


# --- SHARED ON ALL PAGES ---
#st.logo("assets/codingisfun_logo.png")
#st.sidebar.markdown("Made with ❤️ by [Sven](https://youtube.com/@codingisfun)")


# --- RUN NAVIGATION ---
pg.run()


#Análise Descritiva: Dashboard, Relatorio
#Análise Preditiva: TEOREMA BAYES MERCADO, BIBLIOTECA ML
#Sistemas:CRIAÇÃO DE BIBLIOTECA PARA REDUZIR LINHAS CÓDIGO,  SISGRAD, MODELO ALOCAÇÃO, CENTRAL FINANÇAS
#OUTROS: CALCULADORA JUROS COM INFLAÇÃO,  HABIT TRACKER
#MATERIAIS: CANAIS YOUTUBE, ARTIGOS MEDIUM, CONTAS INSTAGRAM, NEWSLETTER, CONTAS TT, GITHUB


#3 ULTIMOS GRANDES PROJETOS: TRANSFERENCIA DE TECNOLOGIA DE BI DA CGE-RJ PARA CÓDIGO ABERTO 
#SISSGRAD - SISTEMA GERADOR DE RELATORIO PARA ANALISE DE DADOS
#CRIAÇÃO DE BIBLIOTECA 