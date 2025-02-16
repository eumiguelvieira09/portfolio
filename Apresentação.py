import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# José Miguel Vieira 👋")

#st.sidebar.success("Select a demo above.")

st.markdown(
    """
    Me chamo José Miguel graduando em Estatística e Ciências Atuariais pela Universidade do Estado do Rio de Janeiro
    e trabalho com Ciência e Análise de Dados (atualmente na Controladoria Geral do Estado do Rio de Janeiro)
    **👈 Selecione na barra lateral** algum tópico para conferir
    alguns projetos que realizei recentemente. 
    ### Quer saber mais?
    - Confira meu Github [streamlit.io](https://streamlit.io)
    - Último projeto realizado em funcionamento [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### Contato
    - Email [Entre em contato caso queira conversar sobre algum projeto](https://github.com/streamlit/demo-self-driving)
    - Telefone [Pode falar comigo no whatsapp também](https://github.com/streamlit/demo-uber-nyc-pickups)
    - LinkedIn [LinkedIn](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)