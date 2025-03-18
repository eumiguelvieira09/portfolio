import pandas as pd
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
# Nome do arquivo CSV
file_name = 'registro_diario.csv'


st.set_page_config(
    page_title="Registro Tarefas",
    layout="wide",
    menu_items={
        'Get Help': 'https://www.google.com'
    }
)
#Adição título

st.markdown("""
    <style>
    /* Ocultar a barra superior do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Remover margens e padding do corpo da página */
    .block-container {
        padding-top: 0;
        padding-left: 0;
        padding-right: 0;
        padding-bottom: 0;
    }

    /* Estilizar a barra de cabeçalho */
    .header-bar {
        background-color: #003366; /* Cor de fundo azul marinho */
        color: white; /* Cor do texto branco */
        padding: 20px 0; /* Espaçamento vertical */
        text-align: center;
        font-family: 'Arial', sans-serif; /* Fonte do texto */
        font-size: 36px; /* Tamanho do texto */
        font-weight: bold; /* Peso da fonte */
        width: 100%; /* Ocupa toda a largura da tela */
        margin: 0; /* Remove margens padrão */
        position: relative;
        top: 0;
        left: 0;
    }

    .main-content {
        margin-top: 15px; /* Espaço abaixo da barra para o conteúdo principal */
        margin-left: 10px
    }
            
    </style>
    <div class="header-bar">
        Registro de Atividades
    </div>
    <div class="main-content">
        <!-- O conteúdo do seu dashboard começa aqui -->
    </div>
    """, unsafe_allow_html=True)

# Função para carregar ou criar um DataFrame
def load_dataframe():
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        colunas = ['Exercicios', 'Agua', 'Comida', 'Estudo', 'Horas Estudo', 'Trabalho', 'Horas Trabalho',
                   'Exercicios Feitos', 'Dinheiro Gasto', 'Dinheiro Ganho', 'O que Estudou', 'No que Trabalhou']
        return pd.DataFrame(columns=colunas)

# Função para resetar o DataFrame
def reset_dataframe():
    if os.path.exists(file_name):
        os.remove(file_name)  # Remove o arquivo CSV
    return pd.DataFrame(columns=['Exercicios', 'Agua', 'Comida', 'Estudo', 'Horas Estudo', 'Trabalho', 'Horas Trabalho',
                                 'Exercicios Feitos', 'Dinheiro Gasto', 'Dinheiro Ganho', 'O que Estudou', 'No que Trabalhou'])



# Criação das abas
tab1, tab2, tab3 = st.tabs(["Formulário", "Análise", "Tabela de Dados"])

# Aba do formulário
with tab1:
    # Pergunta ao usuário se quer resetar os dados
    resetar = st.radio("Você quer resetar os dados?", ('Não', 'Sim'))
    if resetar == 'Sim':
        df = reset_dataframe()
    else:
        df = load_dataframe()
    
    with st.form(key='input_form'):
        # Criação das colunas para cada seção
        col4,col1, col2, col3, col5 = st.columns([0.5,2,2,2,0.5])

        # Coluna 1: Saúde/aparência
        with col4:
            data_input = st.date_input("Escolha a data:", pd.to_datetime('today'))  # Padrão: hoje
        with col1:
            st.subheader("Saúde/Aparência")  # Título da coluna 1

            exercicios = st.number_input("Quanto tempo de exercício você fez hoje:", min_value=0, step=1)
            exercicios_feitos = st.multiselect(
                "Quais exercícios você fez hoje?",
                options=["Corrida", "Pull1", "Pull2", "Push1", "Push2", "Legs1", "Legs2", 'Musculação+Cardio']
            )
            cardio_tempo = st.number_input("Tempo do Cárdio")      
            cardio_distancia = st.number_input("Distância do Cárdio")      
            agua = st.number_input("Quantos copos de água você bebeu:", min_value=0, step=1)
            comida = st.number_input("Quantas refeições você fez:", min_value=0, step=1)
            R1 = st.text_input("R1")
            R2 = st.text_input("R2")
            R3 = st.text_input("R3")
            lavar_rosto = st.number_input("Lavou o rosto?", min_value=0, step=1)
            dentes = st.number_input("Escovou os dentes?", min_value=0, step=1)

        # Coluna 2: Trabalho/Carreira
        with col2:
            st.subheader("Trabalho/Carreira")  # Título da coluna 2
            estudo = st.selectbox("Você estudou hoje?", ['sim', 'não'])
            horas_estudo = st.number_input("Quantas horas você estudou:", min_value=0.0, step=0.5)
            o_que_estudou = st.text_input("O que você estudou hoje?")
            trabalho = st.selectbox("Você trabalhou hoje?", ['sim', 'não'])
            horas_trabalho = st.number_input("Quantas horas você trabalhou:", min_value=0.0, step=0.5)
            no_que_trabalhou = st.text_input("No que você trabalhou hoje?")
            aplicacoes = st.number_input("Número de Aplicações", min_value=0, step=1)
            tempo_projetos_pessoais = st.number_input("Tempo nos projetos pessoais (horas)", min_value=0.0, step=0.5)
            aprendizado_principal = st.text_input("Principal aprendizado do dia")

        # Coluna 3: Networking/Influência
        with col3:
            st.subheader("Networking/Influência")  # Título da coluna 3
            dinheiro_gasto = st.number_input("Quanto dinheiro você gastou hoje:", min_value=0.0, step=0.01)
            dinheiro_ganho = st.number_input("Quanto dinheiro você ganhou hoje:", min_value=0.0, step=0.01)
            pessoas_cumprimentadas = st.number_input("Quantas pessoas novas cumprimentou", min_value=0, step=1)
            pessoas_ajudadas = st.number_input("Quantas pessoas ajudou sem esperar nada em troca", min_value=0, step=1)
            frase_influencia = st.text_input("Frase do dia em relação a Influência")

        submit_button = st.form_submit_button(label='Adicionar Registro')

    if submit_button:
        nova_entrada = pd.DataFrame([{
            'Data': data_input,
            'Exercicios': exercicios,
            'Agua': agua,
            'Comida': comida,
            'Estudo': estudo,
            'Horas Estudo': horas_estudo,
            'Trabalho': trabalho,
            'Horas Trabalho': horas_trabalho,
            'Exercicios Feitos': exercicios_feitos,
            'Tempo Cárdio': cardio_tempo,
            'Distância Cárdio': cardio_distancia,
            'Dinheiro Gasto': dinheiro_gasto,
            'Dinheiro Ganho': dinheiro_ganho,
            'O que Estudou': o_que_estudou,
            'No que Trabalhou': no_que_trabalhou,
            'R1': R1,
            'R2': R2,
            'R3': R3,
            'Lavou o rosto': lavar_rosto,
            'Escovou os dentes': dentes,
            'Aplicações': aplicacoes,
            'Tempo Projetos Pessoais': tempo_projetos_pessoais,
            'Principal Aprendizado': aprendizado_principal,
            'Pessoas Cumprimentadas': pessoas_cumprimentadas,
            'Pessoas Ajudadas': pessoas_ajudadas,
            'Frase Influência': frase_influencia
        }])

        df = pd.concat([df, nova_entrada], ignore_index=True)
        df.to_csv(file_name, index=False)  # Salva o DataFrame em um arquivo CSV
        st.success("Registro adicionado com sucesso!")  
        with col5:
            st.write("")
#######################################################################################
#Criação dos gráficos 
estudo_ocorrencias = df['O que Estudou'].value_counts().reset_index()
estudo_ocorrencias.columns = ['O que Estudou', 'Contagem']
fig_estudo = px.bar(estudo_ocorrencias, x='O que Estudou', y='Contagem', 
                        title='Ocorrências do que Estudou',
                        labels={'O que Estudou': 'Tópico', 'Contagem': 'Número de Ocorrências'})

# Gráfico 2: Ocorrências da coluna 'No que Trabalhou'
trabalho_ocorrencias = df['No que Trabalhou'].value_counts().reset_index()
trabalho_ocorrencias.columns = ['No que Trabalhou', 'Contagem']
fig_trabalho = px.bar(trabalho_ocorrencias, x='No que Trabalhou', y='Contagem', 
                        title='Ocorrências do que Trabalhou',
                        labels={'No que Trabalhou': 'Tópico', 'Contagem': 'Número de Ocorrências'})

# Gráfico 3: Gráfico de pizza para R3
r3_ocorrencias = df['R3'].value_counts().nlargest(5).reset_index()
r3_ocorrencias.columns = ['R3', 'Contagem']
fig_r3 = px.pie(r3_ocorrencias, names='R3', values='Contagem', 
                title='Top 5 ocorrências de R3')



# Gráfico 4: Gráfico de linhas para Horas de Estudo vs. Horas de Trabalho
fig_horas = go.Figure()
fig_horas.add_trace(
    go.Scatter(
        x=df.index,
        y=df['Horas Estudo'],
        mode='lines+markers',
        name='Horas de Estudo',
        hovertemplate='Dia %{x}: %{y} horas de estudo'
    )
)
fig_horas.add_trace(
    go.Scatter(
        x=df.index,
        y=df['Horas Trabalho'],
        mode='lines+markers',
        name='Horas de Trabalho',
        hovertemplate='Dia %{x}: %{y} horas de trabalho'
    )
)
fig_horas.update_layout(
    title='Comparação: Horas de Estudo vs. Horas de Trabalho',
    xaxis_title='Dia',
    yaxis_title='Horas'
)

# Gráfico 5: Gráfico de linhas para Dinheiro Gasto vs. Dinheiro Ganho
fig_dinheiro = go.Figure()
fig_dinheiro.add_trace(
    go.Scatter(
        x=df.index,
        y=df['Dinheiro Gasto'],
        mode='lines+markers',
        name='Dinheiro Gasto',
        hovertemplate='Dia %{x}: R$%{y} gastos'
    )
)
fig_dinheiro.add_trace(
    go.Scatter(
        x=df.index,
        y=df['Dinheiro Ganho'],
        mode='lines+markers',
        name='Dinheiro Ganho',
        hovertemplate='Dia %{x}: R$%{y} ganhos'
    )
)
fig_dinheiro.update_layout(
    title='Comparação: Dinheiro Gasto vs. Dinheiro Ganho',
    xaxis_title='Dia',
    yaxis_title='Valor (R$)'
)
#################################################################

#################################################################3
# Aba dos gráficos
with tab2:
    if not df.empty:
        # Configuração dos KPIs no topo 
        kpi1_value = df['Agua'].mean()
        kpi2_value = df['Horas Estudo'].mean()
        kpi3_value = df['Horas Trabalho'].mean()
        kpi4_value = df['Dinheiro Ganho'].sum()
        kpi5_value = df['Dinheiro Gasto'].sum()

        # Exemplo de KPIs
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)            
        kpi1.metric("Média de Água", f"{kpi1_value}")
        kpi2.metric("Média de Tempo de Estudo", f"{kpi2_value}")
        kpi3.metric("Média de Tempo de Trabalho", f"{kpi3_value}")
        kpi4.metric("Total de Dinheiro Entrando", f"{kpi4_value}")
        kpi5.metric("TTotal de Dinheiro Saindo", f"{kpi5_value}")

        # Configuração das colunas para gráficos
        col1, col2, col3 = st.columns(3)

        # Gráfico 1: Gráfico de barras para contagem dos tópicos em "O que Estudou"
        with col1:
            st.plotly_chart(fig_estudo)

        with col2:
            st.plotly_chart(fig_estudo)

        with col3:
            st.plotly_chart(fig_r3)

        col7,col8 = st.columns(2)
        with col7:
            st.plotly_chart(fig_horas)
        with col8:
            st.plotly_chart(fig_dinheiro)



# Aba da tabela de dados
with tab3:
    if not df.empty:
        st.write("Dados coletados:")
        st.dataframe(df)
    else:
        st.write("Nenhum dado disponível.")
