import streamlit as st
from forms.contact import contact_form
from aviso import send_email


@st.dialog("Contact Me")
def show_contact_form():
    contact_form()


# --- HERO SECTION ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.image("./assets/foto_perfil.png", width=230)

with col2:
    st.title("José Miguel Vieira", anchor=False)
    st.write(
        "Graduando em Estatística e Ciências Atuariais pela UERJ. Análise e Ciência de Dados na Controladoria Geral do Estado - RJ."
    )
    if st.button("✉️ Entre em Contato"):
        show_contact_form()
    
    pdf_file_path = r'assets/JOSEMIGUELVMESQUITA_CURRICULO.pdf'
    # Lendo o arquivo PDF para que o Streamlit possa oferecê-lo para download
    with open(pdf_file_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()
    # Adicionando o botão de download no Streamlit
    st.download_button(
        label="Baixar Currículo",  # Texto do botão
        data=pdf_data,  # O conteúdo do PDF
        file_name="JOSEMIGUELVMESQUITA_CURRICULO.pdf",  # Nome do arquivo para o usuário baixar
        mime="application/pdf"  # Tipo MIME do arquivo
    )


# --- EXPERIENCE & QUALIFICATIONS ---
st.write("\n")
st.subheader("Experiência e Qualificações", anchor=False)
st.write(
    """
    - 2 Anos de experiência retirando insights relevantes dos dados
    - Vasto conhecimento em criação de Dashboards e Relatórios com ferramentas de código aberto (Python: Streamlit, R:Shiny)
    - Ótimo nível de conhecimento de Estatística (Descritiva e Inferencial) e suas aplicações 
    - Rápido entendimento dos projetos e experiência em levantamento de requisitos 
    """
)

# --- SKILLS ---
st.write("\n")
st.subheader("Habilidades", anchor=False)
st.write(
    """
    - Programming: Python (Scikit-learn, Pandas, Streamlit, Numpy), SQL (MySQL), R
    - Data Visualization: PowerBi, Plotly, Matplotlib
    - Modeling: Logistic regression, linear regression, decision trees
    - Databases: Postgres, MongoDB, MySQL
    """
)
