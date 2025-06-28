import streamlit as st
import pandas as pd
import os
import plotly.express as px 
import plotly.graph_objects as go
#from aviso import send_email

# Configuração da página
st.set_page_config(layout="wide")

# Dados simulados de usuários com senhas fixas
data = {
    "Username": [f"user{i}" for i in range(1, 11)],
    "Email": [f"user{i}@empresa.com" for i in range(1, 11)],
    "Senha": ["password12345678901234" for _ in range(10)],
    "Cargo": ["Coordenador" if i % 2 == 0 else "Funcionário" for i in range(1, 11)]
}
df_usuarios = pd.DataFrame(data)

# Função para verificar credenciais
def autenticar_usuario(username, senha):
    user = df_usuarios[df_usuarios["Username"] == username]
    if not user.empty:
        stored_senha = user.iloc[0]["Senha"]
        if senha == stored_senha:
            return user.iloc[0]["Cargo"]
    return None

# Estado de autenticação
if "cargo" not in st.session_state:
    st.session_state.cargo = None

# Tela de login
if st.session_state.cargo is None:
    st.title("🔑 Login ")
    username = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        cargo = autenticar_usuario(username, senha)
        if cargo:
            st.session_state.cargo = cargo
            st.success(f"✅ Login bem-sucedido! Cargo: {cargo}")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos.")

    st.write("Nível coordenador: user2, senha: password12345678901234/" \
    "Nível funcionário: user1, senha: password12345678901234")
    st.stop()

# Caminho do arquivo de demandas
file_path = "demandas.csv"


# Criar abas
if st.session_state.cargo == "Coordenador":
    tab1, tab2, tab3 = st.tabs(["Controle de Demanda", "Visão Geral", "Análise dos Dados"])
    
    with tab1:
        st.subheader("📊 Controle de Demanda")
        st.write("Preencha as informações para registrar ou editar uma demanda.")
        
        # Carregar demandas existentes
        df = pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame()
        
        # Seleção de demanda para edição
        demanda_selecionada = None
        if not df.empty:
            codigos = df["Código da Tarefa"].astype(str).tolist()
            codigo_tarefa = st.selectbox("Selecione uma demanda para editar ou registre uma nova", ["Nova"] + codigos)
            if codigo_tarefa != "Nova":
                demanda_selecionada = df[df["Código da Tarefa"].astype(str) == codigo_tarefa].iloc[0]
        else:
            codigo_tarefa = "Nova"
        
        # Formulário
        novo_codigo = st.text_input("Código da Tarefa", value=str(demanda_selecionada["Código da Tarefa"]) if demanda_selecionada is not None else "")
        projeto = st.text_input("Projeto", value=demanda_selecionada["Projeto"] if demanda_selecionada is not None else "")
        produto = st.text_input("Produto", value=demanda_selecionada["Produto"] if demanda_selecionada is not None else "")
        responsavel1 = st.text_input("Responsável 1", value=demanda_selecionada["Responsável 1"] if demanda_selecionada is not None else "")
        responsavel2 = st.text_input("Responsável 2", value=demanda_selecionada["Responsável 2"] if demanda_selecionada is not None else "")
        responsavel3 = st.text_input("Responsável 3", value=demanda_selecionada["Responsável 3"] if demanda_selecionada is not None else "")
        empresa = st.text_input("Empresa", value=demanda_selecionada["Empresa"] if demanda_selecionada is not None else "")
        prazo = st.date_input("Prazo")
        descricao = st.text_area("Descrição", value=demanda_selecionada["Descrição"] if demanda_selecionada is not None else "")
        status = st.multiselect("Status", ["A iniciar", "Em Andamento", "Aguardando Resposta", "Aguardando Aprovação", "Finalizado"],
                                default=demanda_selecionada["Status"].split(", ") if demanda_selecionada is not None else [])
        observacao = st.text_area("Observação", value=demanda_selecionada["Observação"] if demanda_selecionada is not None else "")
        
        # Botão para salvar/editar a demanda
        if st.button("Salvar Demanda"):
            nova_demanda = pd.DataFrame([{ 
                "Código da Tarefa": novo_codigo,
                "Projeto": projeto,
                "Produto": produto,
                "Responsável 1": responsavel1,
                "Responsável 2": responsavel2,
                "Responsável 3": responsavel3,
                "Empresa": empresa,
                "Prazo": prazo.strftime("%d/%m/%Y"),
                "Descrição": descricao,
                "Status": ", ".join(status),
                "Observação": observacao
            }])
            
            if os.path.exists(file_path):
                df_existente = pd.read_csv(file_path)
                df_existente = df_existente[df_existente["Código da Tarefa"].astype(str) != novo_codigo]  # Remove a versão antiga
                df_final = pd.concat([df_existente, nova_demanda], ignore_index=True)
 #               send_email
            else:
                df_final = nova_demanda
            
            
            df_final.to_csv(file_path, index=False)
            st.success("✅ Demanda salva com sucesso!")
            st.rerun()

    with tab2:
        st.subheader("📈 Visão Geral")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
                    # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                responsaveis = st.multiselect("Filtrar por Responsável", df[["Responsável 1", "Responsável 2", "Responsável 3"]].values.flatten())
            with col2:

                empresas = st.multiselect("Filtrar por Empresa", df["Empresa"].unique())
            with col3:

                projetos = st.multiselect("Filtrar por Projeto", df["Projeto"].unique())
            
            # Aplicação dos filtros
            if responsaveis:
                df = df[df[["Responsável 1", "Responsável 2", "Responsável 3"]].apply(lambda x: any(r in responsaveis for r in x), axis=1)]
            if empresas:
                df = df[df["Empresa"].isin(empresas)]
            if projetos:
                df = df[df["Projeto"].isin(projetos)]


            for status in ["A iniciar", "Em Andamento", "Aguardando Resposta", "Aguardando Aprovação", "Finalizado"]:
                df_status = df[df["Status"].str.contains(status, na=False)]
                if not df_status.empty:
                    st.subheader(f"📌 {status}")
                    st.dataframe(df_status)
                else:
                    st.write(f"Nenhuma demanda encontrada para o status: {status}")
        else:
            st.write("Nenhuma demanda registrada ainda.")
    
    with tab3: 
        
        #Criação dos gráficos 
        estudo_ocorrencias = df['Projeto'].value_counts().reset_index()
        estudo_ocorrencias.columns = ['Projeto', 'Contagem']
        fig_estudo = px.bar(estudo_ocorrencias, x='Projeto', y='Contagem', 
                                title='Contagem de Tarefas por Projeto',
                                labels={'Projeto': 'Projeto', 'Contagem': 'Número de Ocorrências'})

        # Gráfico 2: Ocorrências da coluna 'No que Trabalhou'
        trabalho_ocorrencias = df['Responsável 1'].value_counts().reset_index()
        trabalho_ocorrencias.columns = ['Responsável 1', 'Contagem']
        fig_trabalho = px.bar(trabalho_ocorrencias, x='Responsável 1', y='Contagem', 
                                title='Ocorrências de Responsável 1',
                                labels={'Responsável 1': 'Tópico', 'Contagem': 'Número de Ocorrências'})

        # Gráfico 3: Gráfico de pizza para R3
        r3_ocorrencias = df['Empresa'].value_counts().nlargest(5).reset_index()
        r3_ocorrencias.columns = ['Empresa', 'Contagem']
        fig_r3 = px.pie(r3_ocorrencias, names='Empresa', values='Contagem', 
                        title='Top 5 ocorrências de Empresa')



        # # Gráfico 4: Gráfico de linhas para Horas de Estudo vs. Horas de Trabalho
        # fig_horas = go.Figure()
        # fig_horas.add_trace(
        #     go.Scatter(
        #         x=df.index,
        #         y=df['Horas Estudo'],
        #         mode='lines+markers',
        #         name='Horas de Estudo',
        #         hovertemplate='Dia %{x}: %{y} horas de estudo'
        #     )
        # )
        # fig_horas.add_trace(
        #     go.Scatter(
        #         x=df.index,
        #         y=df['Horas Trabalho'],
        #         mode='lines+markers',
        #         name='Horas de Trabalho',
        #         hovertemplate='Dia %{x}: %{y} horas de trabalho'
        #     )
        # )
        # fig_horas.update_layout(
        #     title='Comparação: Horas de Estudo vs. Horas de Trabalho',
        #     xaxis_title='Dia',
        #     yaxis_title='Horas'
        # )

        # # Gráfico 5: Gráfico de linhas para Dinheiro Gasto vs. Dinheiro Ganho
        # fig_dinheiro = go.Figure()
        # fig_dinheiro.add_trace(
        #     go.Scatter(
        #         x=df.index,
        #         y=df['Dinheiro Gasto'],
        #         mode='lines+markers',
        #         name='Dinheiro Gasto',
        #         hovertemplate='Dia %{x}: R$%{y} gastos'
        #     )
        # )
        # fig_dinheiro.add_trace(
        #     go.Scatter(
        #         x=df.index,
        #         y=df['Dinheiro Ganho'],
        #         mode='lines+markers',
        #         name='Dinheiro Ganho',
        #         hovertemplate='Dia %{x}: R$%{y} ganhos'
        #     )
        # )
        # fig_dinheiro.update_layout(
        #     title='Comparação: Dinheiro Gasto vs. Dinheiro Ganho',
        #     xaxis_title='Dia',
        #     yaxis_title='Valor (R$)'
        # )
        if not df.empty:
            # Configuração dos KPIs no topo 
            kpi1_value = len(df['Projeto'])
            kpi2_value = len(df['Empresa'])
            kpi3_value = df['Projeto'].iloc[0]
            # kpi4_value = df['Dinheiro Ganho'].sum()
            # kpi5_value = df['Dinheiro Gasto'].sum()

            # # Exemplo de KPIs
            kpi1, kpi2, kpi3 = st.columns(3)            
            kpi1.metric("Quantidade de Projetos", f"{kpi1_value}")
            kpi2.metric("Quantidade de Empresas", f"{kpi2_value}")
            kpi3.metric("Último Projeto", f"{kpi3_value}")
            # kpi4.metric("Total de Dinheiro Entrando", f"{kpi4_value}")
            # kpi5.metric("TTotal de Dinheiro Saindo", f"{kpi5_value}")

            # Configuração das colunas para gráficos
            col1, col2, col3 = st.columns(3)

            # Gráfico 1: Gráfico de barras para contagem dos tópicos em "O que Estudou"
            with col1:
                st.plotly_chart(fig_estudo)

            with col2:
                st.plotly_chart(fig_trabalho)

            with col3:
                st.plotly_chart(fig_r3)

            # col7,col8 = st.columns(2)
            # with col7:
            #     st.plotly_chart(fig_horas)
            # with col8:
            #     st.plotly_chart(fig_dinheiro)
else:
    tab2,tab3, = st.tabs(["Visão Geral", "Análise dos Dados"])
    with tab2:
        st.subheader("📈 Visão Geral")
        
        # Carregar demandas
        file_path = "demandas.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                responsaveis = st.multiselect("Filtrar por Responsável", df[["Responsável 1", "Responsável 2", "Responsável 3"]].values.flatten())
            with col2:

                empresas = st.multiselect("Filtrar por Empresa", df["Empresa"].unique())
            with col3:

                projetos = st.multiselect("Filtrar por Projeto", df["Projeto"].unique())
            st.divider()

            # Criar tabelas para cada status
            status_list = ["A iniciar", "Em Andamento", "Aguardando Resposta", "Aguardando Aprovação", "Finalizado"]
            for status in status_list:
                df_status = df[df["Status"].str.contains(status, na=False)]
                if not df_status.empty:
                    st.subheader(f"📌 {status}")
                    st.dataframe(df_status)
                else:
                    st.write(f"Nenhuma demanda encontrada para o status: {status}")
        else:
            st.write("Nenhuma demanda registrada ainda.")


        st.divider()
        st.subheader("🔄 Atualizar Status da Demanda")

        if os.path.exists("demandas.csv"):
            df = pd.read_csv("demandas.csv")

            if not df.empty:
                demanda_selecionada = st.selectbox("Selecione a demanda para atualizar o status", df["Código da Tarefa"].astype(str))

                # Pega a demanda selecionada
                demanda_atual = df[df["Código da Tarefa"].astype(str) == demanda_selecionada].iloc[0]

                # Apenas campo de status editável
                novo_status = st.multiselect("Novo Status", ["A iniciar", "Em Andamento", "Aguardando Resposta", "Aguardando Aprovação", "Finalizado"], 
                                            demanda_atual["Status"].split(", "))

                if st.button("Atualizar Status"):
                    df.loc[df["Código da Tarefa"].astype(str) == demanda_selecionada, "Status"] = ", ".join(novo_status)
                    df.to_csv("demandas.csv", index=False)
 #                   send_email
                    st.success("✅ Status atualizado com sucesso!")
                    st.rerun()
            else:
                st.warning("Nenhuma demanda registrada ainda.")
    with tab3:
                #Criação dos gráficos 
        estudo_ocorrencias = df['Projeto'].value_counts().reset_index()
        estudo_ocorrencias.columns = ['Projeto', 'Contagem']
        fig_estudo = px.bar(estudo_ocorrencias, x='Projeto', y='Contagem', 
                                title='Contagem de Tarefas por Projeto',
                                labels={'Projeto': 'Projeto', 'Contagem': 'Número de Ocorrências'})

        # Gráfico 2: Ocorrências da coluna 'No que Trabalhou'
        trabalho_ocorrencias = df['Responsável 1'].value_counts().reset_index()
        trabalho_ocorrencias.columns = ['Responsável 1', 'Contagem']
        fig_trabalho = px.bar(trabalho_ocorrencias, x='Responsável 1', y='Contagem', 
                                title='Ocorrências de Responsável 1',
                                labels={'Responsável 1': 'Tópico', 'Contagem': 'Número de Ocorrências'})

        # Gráfico 3: Gráfico de pizza para R3
        r3_ocorrencias = df['Empresa'].value_counts().nlargest(5).reset_index()
        r3_ocorrencias.columns = ['Empresa', 'Contagem']
        fig_r3 = px.pie(r3_ocorrencias, names='Empresa', values='Contagem', 
                        title='Top 5 ocorrências de Empresa')



        # # Gráfico 4: Gráfico de linhas para Horas de Estudo vs. Horas de Trabalho
        # fig_horas = go.Figure()
        # fig_horas.add_trace(
        #     go.Scatter(
        #         x=df.index,
        #         y=df['Horas Estudo'],
        #         mode='lines+markers',
        #         name='Horas de Estudo',
        #         hovertemplate='Dia %{x}: %{y} horas de estudo'
        #     )
        # )
        # fig_horas.add_trace(
        #     go.Scatter(
        #         x=df.index,
        #         y=df['Horas Trabalho'],
        #         mode='lines+markers',
        #         name='Horas de Trabalho',
        #         hovertemplate='Dia %{x}: %{y} horas de trabalho'
        #     )
        # )
        # fig_horas.update_layout(
        #     title='Comparação: Horas de Estudo vs. Horas de Trabalho',
        #     xaxis_title='Dia',
        #     yaxis_title='Horas'
        # )

        # # Gráfico 5: Gráfico de linhas para Dinheiro Gasto vs. Dinheiro Ganho
        # fig_dinheiro = go.Figure()
        # fig_dinheiro.add_trace(
        #     go.Scatter(
        #         x=df.index,
        #         y=df['Dinheiro Gasto'],
        #         mode='lines+markers',
        #         name='Dinheiro Gasto',
        #         hovertemplate='Dia %{x}: R$%{y} gastos'
        #     )
        # )
        # fig_dinheiro.add_trace(
        #     go.Scatter(
        #         x=df.index,
        #         y=df['Dinheiro Ganho'],
        #         mode='lines+markers',
        #         name='Dinheiro Ganho',
        #         hovertemplate='Dia %{x}: R$%{y} ganhos'
        #     )
        # )
        # fig_dinheiro.update_layout(
        #     title='Comparação: Dinheiro Gasto vs. Dinheiro Ganho',
        #     xaxis_title='Dia',
        #     yaxis_title='Valor (R$)'
        # )
        if not df.empty:
            # Configuração dos KPIs no topo 
            kpi1_value = len(df['Projeto'])
            kpi2_value = len(df['Empresa'])
            kpi3_value = df['Projeto'].iloc[0]
            # kpi4_value = df['Dinheiro Ganho'].sum()
            # kpi5_value = df['Dinheiro Gasto'].sum()

            # # Exemplo de KPIs
            kpi1, kpi2, kpi3 = st.columns(3)            
            kpi1.metric("Quantidade de Projetos", f"{kpi1_value}")
            kpi2.metric("Quantidade de Empresas", f"{kpi2_value}")
            kpi3.metric("Último Projeto", f"{kpi3_value}")
            # kpi4.metric("Total de Dinheiro Entrando", f"{kpi4_value}")
            # kpi5.metric("TTotal de Dinheiro Saindo", f"{kpi5_value}")

            # Configuração das colunas para gráficos
            col1, col2, col3 = st.columns(3)

            # Gráfico 1: Gráfico de barras para contagem dos tópicos em "O que Estudou"
            with col1:
                st.plotly_chart(fig_estudo)

            with col2:
                st.plotly_chart(fig_trabalho)

            with col3:
                st.plotly_chart(fig_r3)

            # col7,col8 = st.columns(2)
            # with col7:
            #     st.plotly_chart(fig_horas)
            # with col8:
            #     st.plotly_chart(fig_dinheiro)