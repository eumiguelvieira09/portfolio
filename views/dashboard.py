import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import plotly.graph_objects as go
import locale
import os
import io

######################################TRATAMENTO##########################################
config_graph = {
    "displayModeBar": True,
    "modeBarButtonsToRemove":[
        'zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d',
        'zoomOut2d', 'autoScale2d', 'resetScale2d',
        'hoverClosestCartesian', 'hoverCompareCartesian',
        'zoom3d', 'pan3d', 'orbitRotation', 'tableRotation',
        'resetCameraDefault3d', 'resetCameraLastSave3d',
        'hoverClosest3d', 'zoomInGeo', 'zoomOutGeo',
        'resetGeo', 'hoverClosestGeo',
        'hoverClosestGl2d',
        'toggleHover', 'resetViews',
        'sendDataToCloud', 'toggleSpikelines',
        'resetViewMapbox']
    ,
    "displaylogo": False
}

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Tenta UTF-8
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')  # Tenta sem UTF-8
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')  # Usa a configuração padrão do sistema

# Configuração da página
st.set_page_config(
    page_title="Obras",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://www.google.com',
    
    }
)

def generate_colors(num_categorias, color_palette): #paletas de cores pra graficos
    colors = color_palette * (num_categorias // len(color_palette)) + color_palette[:num_categorias % len(color_palette)]
    return colors
corazul = ['#052E59']
corverde =['#355e2a']
colors_base = ['#052E59','#517496', '#7A89B2', '#A0ADCC', '#C4D1E2', '#DAE4ED', '#EAF0F6']

def converte_br(numero):
    suf = {
        1e6: "M",    # milhão
        1e9: "B",    # bilhão
        1e12: "T"    # trilhão
    }
    negativo = numero < 0
    numero = abs(numero)
    for s in reversed(sorted(suf.keys())):
        if numero >= s:
            if numero % s == 0:
                valor_formatado = locale.format_string("%.0f", numero / s, grouping=True)
            else:
                valor_formatado = locale.format_string("%.2f", numero / s, grouping=True)
            return f"{'-' if negativo else ''}{valor_formatado}{suf[s]}"
    return locale.currency(numero, grouping=True, symbol=None)
def load_css():
    with open('./assets/styles.css') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
load_css()
def render_header(title):
    st.markdown(f"""
        <div class="header-bar">
            <span class="header-title">{title}</span>
        </div>
        """, unsafe_allow_html=True)
def show_warning():
    st.markdown(
        """
        <div class="warning-container">
            Nenhum dado disponível para o filtro selecionado. <br>
            Apague os filtros para o Painel voltar ao estado inicial.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# Chama o título diretamente após o CSS ser carregado
render_header('Obras')



############################# FILTROS ############
@st.cache_data
def carregar_dados():
    resultado_final = pd.read_csv("./assets/dados_obra.csv", sep=";", encoding="utf-8")

    return resultado_final

# Verifica se os dados já foram carregados, se não tiverem, carrega e armazena
if 'df_original' not in st.session_state:
    st.session_state.df_original = carregar_dados()
## Seu dataframe inicial
df_inicio = st.session_state.df_original.copy()

df_inicio['Data_emissão_ne'] = pd.to_datetime(df_inicio['Data_emissão_ne'], errors='coerce')

data_inicio = df_inicio['Data_emissão_ne'].min()
data_fim = df_inicio['Data_emissão_ne'].max()

df_inicio['Atualizado_em'] = pd.to_datetime(df_inicio['Atualizado_em'], format='%Y-%m-%d %H:%M:%S')
ultima_atualizacao = df_inicio['Atualizado_em'].max().strftime('%d/%m/%Y %H:%M')

# Inicializa o estado dos filtros se não estiverem no session_state
if 'data_inicial' not in st.session_state:
    st.session_state['data_inicial'] = data_inicio
if 'data_final' not in st.session_state:
    st.session_state['data_final'] = data_fim
if 'Nota_de_empenho' not in st.session_state:
    st.session_state['Nota_de_empenho'] = []
if 'Empresa' not in st.session_state:
    st.session_state['Empresa'] = []
if 'Cnpj' not in st.session_state:
    st.session_state['Cnpj'] = []
if 'sigla_ajustada' not in st.session_state:
    st.session_state['sigla_ajustada'] = []
if 'Processo_ne' not in st.session_state:
    st.session_state['Processo_ne'] = []

# Função para redefinir os filtros
def reset_filters():
    st.session_state['data_inicial'] = data_inicio
    st.session_state['data_final'] = data_fim
    st.session_state['Nota_de_empenho'] = []
    st.session_state['Empresa'] = []
    st.session_state['Cnpj'] = []
    st.session_state['sigla_ajustada'] = []
    st.session_state['Processo_ne'] = []


# Função para filtrar os dados
def filtra_dados(data_inicial,data_final,Nota_de_empenho,Empresa,Processo_ne,Cnpj,sigla_ajustada):
    df_filtrado = df_inicio.copy()
    # Filtra por data
    df_filtrado = df_filtrado[(df_filtrado['Data_emissão_ne'] >= pd.to_datetime(data_inicial)) &
                              (df_filtrado['Data_emissão_ne'] <= pd.to_datetime(data_final))]

    # Filtra por fornecedor
    if Nota_de_empenho:
        df_filtrado = df_filtrado[df_filtrado['Nota_de_empenho'].isin(Nota_de_empenho)]

    # Filtra por número da ata
    if Empresa:
        df_filtrado = df_filtrado[df_filtrado['Empresa'].isin(Empresa)]
    # Filtra por processo
    if Processo_ne:
        df_filtrado = df_filtrado[df_filtrado['Processo_(ne)'].isin(Processo_ne)]
    # Filtra por sigla
    if Cnpj:
        df_filtrado = df_filtrado[df_filtrado['Cnpj'].isin(Cnpj)]
    if sigla_ajustada:
        df_filtrado = df_filtrado[df_filtrado['sigla_ajustada'].isin(sigla_ajustada)]

     # Formata a data para exibição
    if df_filtrado.empty:
        show_warning()
    st.session_state.df_filtrado = df_filtrado
# coluna lateral
col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1, 1, 1, 1, 1, 1, 1,1,1])

with col1:
    data_inicial = st.date_input("Data inicial:", min_value=data_inicio, max_value=data_fim, format="DD/MM/YYYY", key="data_inicial")

with col2:
    data_final = st.date_input("Data final:", min_value=data_inicio, max_value=data_fim, format="DD/MM/YYYY", key="data_final")

with col3:
    Nota_de_empenho = st.multiselect("Nota de Empenho:", sorted(map(str, df_inicio['Nota_de_empenho'].unique().tolist())), placeholder="Selecione uma Nota de Empenho", key="Nota_de_empenho")

with col4:
    Empresa = st.multiselect("Empresa:", sorted(map(str, df_inicio['Empresa'].unique().tolist())), placeholder="Selecione uma Empresa", key="Empresa")

with col5:
    Processo_ne = st.multiselect("Número do Processo:", sorted(map(str, df_inicio['Processo_(ne)'].unique().tolist())), placeholder="Selecione um Processo", key="Processo_ne")

with col6:
    Cnpj = st.multiselect("Cnpj:", sorted(map(str, df_inicio['Cnpj'].unique().tolist())), placeholder="Selecione um CNPJ", key="Cnpj")
with col7:
    sigla_ajustada = st.multiselect("Unidade Gestora:", sorted(map(str, df_inicio['sigla_ajustada'].unique().tolist())), placeholder="Selecione uma Unidade Gestora", key="sigla_ajustada")
with col8:
    botao_filtro = st.button('Aplicar Filtros')
with col9:
    completo = st.button(":red[Apagar Filtros]", on_click=reset_filters)
    # Filtros utilizados
    filters_used = {
        "Data inicial": [str(data_inicial)],
        "Data final": [str(data_final)],
        "Nota_de_empenho": Nota_de_empenho,
        "Empresa": Empresa,
        "Processo_(ne)": Processo_ne,
        "sigla_ajustada": sigla_ajustada
    }



    if botao_filtro:
        filtra_dados(data_inicial,data_final,Nota_de_empenho,Empresa,Processo_ne,Cnpj,sigla_ajustada)

    if completo:
        # reseta o df_filtrado
        # foi necessario colocar a transformação aqui tbm para quando o botão for apertado
        # antes, carregava o df completo mas o gráfico nao alterava
        df_aux = df_inicio.copy()
        df_aux['Data_emissão_ne'] = pd.to_datetime(df_aux['Data_emissão_ne'])
        df_aux['Data_emissão_ne'] = df_aux['Data_emissão_ne'].dt.date

        st.session_state.df_filtrado = df_aux


# Se o df_filtrado não existir ou se o botão para limpar os filtros for pressionado,
# inicializa (ou reinicializa) st.session_state.df_filtrado com o dataframe original.
if 'df_filtrado' not in st.session_state or completo:
    data_filtro_inicial = data_inicio
    data_filtro_final = data_fim
    df_aux = df_inicio.copy()
    df_aux['Data_emissão_ne'] = pd.to_datetime(df_aux['Data_emissão_ne'])
    df_aux['Data_emissão_ne'] = df_aux['Data_emissão_ne'].dt.date

    st.session_state.df_filtrado = df_aux

# df recebe o dataframe da sessão
df = st.session_state.df_filtrado
######################### CONSTRUÇAO DOS GRAFICOS ###########################################
if not df.empty:
    # grafico 1
    graf1 = df.groupby('Empresa')["Despesas_empenhadas"].sum().sort_values(ascending=True).tail(10)
    if not graf1.empty:
        num_categorias1 = len(graf1)
        corgrafico1 = generate_colors(num_categorias1, corazul)
        grafico1 = px.bar(graf1, y=graf1.index, x=graf1.values, orientation='h')
        grafico1.update_layout(title='Total de Despesas Empenhadas por Empresa', xaxis=dict(title=None), yaxis=dict(title=None), xaxis_fixedrange=True, yaxis_fixedrange=True)
        grafico1.update_traces(marker=dict(color=corgrafico1), hovertemplate=("Nome: <b>%{y}</b><br>Total: <b>%{x}</b><br>"), hoverlabel=dict(font_size=13))
    else:
        grafico1 = None

    # grafico 2
    graf2 = df.groupby('Ano')["Despesas_empenhadas"].sum()
    if not graf2.empty:
        grafico2 = go.Figure()
        grafico2.add_trace(go.Scatter(
            x=graf2.index,
            y=graf2.values,
            mode='lines+markers',
            fill='tozeroy',  
            fillcolor='rgba(5, 46, 89, 0.35)',  
            line=dict(color='#052E59'),  
            marker=dict(color=corazul, size=6),
            name='',
            hovertemplate=("Ano: <b>%{x}</b><br>Total: <b>%{y}</b><br>")
        ))
        grafico2.update_layout(title='Total de Despesas Empenhadas por Ano', xaxis_tickangle=0, yaxis=dict(title=None), xaxis_fixedrange=True, yaxis_fixedrange=True, height=360)
        grafico2.update_xaxes(type='category')
    else:
        grafico2 = None

    # grafico 3
    graf3 = df.groupby('sigla_ajustada')['Nota_de_empenho'].nunique()
    if not graf3.empty:
        top_5_categorias = graf3.sort_values(ascending=False)[:7]
        outros_valores_sum = graf3[~graf3.index.isin(top_5_categorias.index)].sum()
        linha_outros = pd.Series({'Outros': outros_valores_sum})
        df_agrupado2_ajustado = pd.concat([top_5_categorias, linha_outros])

        num_categorias3 = len(df_agrupado2_ajustado)
        corgrafico3 = generate_colors(num_categorias3, colors_base)

        # Replace color for "Outros"
        idx_outros = df_agrupado2_ajustado.index.get_loc('Outros')
        corgrafico3[idx_outros] = corverde

        grafico3 = go.Figure(data=[
            go.Pie(
                labels=df_agrupado2_ajustado.index,
                values=df_agrupado2_ajustado.values,
                hole=0.5,
                textinfo='percent',
                hovertemplate='Total de notas de empenho:%{value}<extra></extra>',
                marker=dict(colors=corgrafico3, line=dict(color='black', width=0.2))
            )
        ])
        grafico3.update_layout(margin=dict(t=75, b=30, l=0, r=0), legend=dict(font=dict(size=11)), height=350, title='Notas de Empenho Distintas por Unidade Gestora')
        grafico3.update_traces(hoverlabel=dict(font_size=13))
    else:
        grafico3 = None

    # grafico 4
    graf4 = df.groupby('sigla_ajustada')[['Despesas_empenhadas','Despesas_liquidadas','Despesas_pagas']].sum().sort_values(by='Despesas_empenhadas', ascending=False).reset_index()[:10]
    if not graf4.empty:
        cor = ['#052E59', '#517496', '#7A89B2']
        num_categorias4 = len(graf4)
        corgrafico4 = cor * num_categorias4

        grafico4 = px.bar(
            graf4,
            x='sigla_ajustada',
            y=['Despesas_empenhadas', 'Despesas_liquidadas', 'Despesas_pagas'],
            title='Unidade Gestora por Total de Despesas Empenhadas',
            labels={'value': 'Valor', 'variable': 'Tipo', 'sigla_ajustada': 'sigla_ajustada'},
            color_discrete_sequence=corgrafico4,
            barmode='group'
        )
        grafico4.update_layout(xaxis=dict(title=None), yaxis=dict(title=None), xaxis_fixedrange=True, yaxis_fixedrange=True)
        grafico4.for_each_trace(lambda trace: trace.update(name={
            'Despesas_empenhadas': 'Total Despesa Empenhada',
            'Despesas_liquidadas': 'Total Despesa Liquidada',
            'Despesas_pagas': 'Total Despesa Paga'
        }[trace.name]))

        grafico4.update_traces(
            hovertemplate="<b>%{x}</b><br>Total de despesas empenhadas: R$%{y:,.2f}<extra></extra>",
            selector=dict(name='Total Despesa Empenhada'),
            hoverlabel=dict(font_size=13)
        )
        grafico4.update_traces(
            hovertemplate="<b>%{x}</b><br>Total de despesas liquidadas: R$%{y:,.2f}<extra></extra>",
            selector=dict(name='Total Despesa Liquidada'),
            hoverlabel=dict(font_size=13)
        )
        grafico4.update_traces(
            hovertemplate="<b>%{x}</b><br>Total de despesas pagas: R$%{y:,.2f}<extra></extra>",
            selector=dict(name='Total Despesa Paga'),
            hoverlabel=dict(font_size=13)
        )
    else:
        grafico4 = None

    # grafico 5
    bins = [0, 1000, 5000, 10000, 50000, 100000, 1000000]
    labels = ['Menor que 1000', 'Entre 1000 e 5000', 'Entre 5000 e 10000', 'Entre 10000 e 50000', 'Entre 50000 e 100000', 'Entre 100000 e 1000000']
    df['faixa'] = pd.cut(df['Despesas_empenhadas'], bins=bins, labels=labels, right=False)

    contagem_faixa = df['faixa'].value_counts().reset_index()
    contagem_faixa.columns = ['faixa', 'quantidade']

    faixa_order = ['Menor que 1000', 'Entre 1000 e 5000', 'Entre 5000 e 10000', 'Entre 10000 e 50000', 'Entre 50000 e 100000', 'Entre 100000 e 1000000']
    contagem_faixa['faixa'] = pd.Categorical(contagem_faixa['faixa'], categories=faixa_order, ordered=True)
    contagem_faixa = contagem_faixa.sort_values(by='faixa', ascending=False)

    if not contagem_faixa.empty:
        num_categorias5 = len(contagem_faixa)
        corgrafico5 = generate_colors(num_categorias5, corazul)

        grafico5 = px.bar(contagem_faixa, x='quantidade', y='faixa', orientation='h', title='Quantidade de Notas por Faixa de Valor', labels={'quantidade': 'Quantidade de Notas', 'faixa': 'Faixa de Valores'})
        grafico5.update_layout(xaxis_title='Quantidade de Notas', yaxis_title='Faixa de Valores')
        grafico5.update_traces(marker=dict(color=corgrafico5), hovertemplate=("Intervalo: <b>%{y}</b><br>Quantidade: <b>%{x}</b><br>"))
    else:
        grafico5 = None

else:
    grafico1 = grafico2 = grafico3 = grafico4 = grafico5 = None
####################################### LAYOUT ##################
# criando paginas
tab1, tab2 = st.tabs(["📈 Análises", "🗓️ Tabela Geral"])

with tab1:
    # KPI:numero estagiario, quantidade curso, publico, privado
    # Layout dos KPIs
    # Cálculo dos valores KPI
    kpi1_value = df['Despesas_empenhadas'].sum()
    kpi2_value = df['Despesas_pagas'].sum()
    kpi3_value = df['Nota_de_empenho'].nunique()
    kpi4_value = df['Despesas_liquidadas'].sum()
    # Layout das métricas no Streamlit
    kpi1, kpi2,kpi3,kpi4 = st.columns(4)

    # Exibir as métricas
    kpi1.metric("Total de Despesas Empenhadas", f"R$ {converte_br(kpi1_value)}")
    kpi2.metric("Total de Despesas Pagas", f"R$ {converte_br(kpi2_value)}")
    kpi3.metric("Nota de Empenho Distintas", f"{kpi3_value}")
    kpi4.metric("Total de Despesas Liquidadas", f"R$ {converte_br(kpi4_value)}")

    # Layout dos gráficos
    col1, col2,col3 = st.columns([1, 1, 1])
    with col1:
        st.plotly_chart(grafico1, use_container_width=True, config=config_graph)

    with col2:
        st.plotly_chart(grafico3, use_container_width=True, config=config_graph)

    with col3:
       st.plotly_chart(grafico4, use_container_width=True, config=config_graph)


    col4, col5 = st.columns([1, 1])  
    
    with col4:  
        st.plotly_chart(grafico2, use_container_width=True, config=config_graph)
    with  col5:
        st.plotly_chart(grafico5, use_container_width=True, config=config_graph)

def tabela_geral(df):
    # Verifica se todas as colunas desejadas estão no DataFrame
    colunas_desejadas = [
        'Data_emissão_ne', 'Unidade_orçamentária','Empresa','sigla','Despesas_empenhadas', 
        'Despesas_liquidadas', 'Despesas_pagas','Subelemento', 'Cnpj', 'Nota_de_empenho', 
        'Histórico/objeto', 'Processo_(ne)'
    ]
    df_tab = df[colunas_desejadas].copy()
    return df_tab

# Tab 2 - Cria layout e configurações da tabela
with tab2:
    df_tab = tabela_geral(df)

    # Configura as colunas da tabela para exibição
    column_config = {
        "Data_emissão_ne": st.column_config.DateColumn(label="Data de Emissão do NE", format="DD/MM/YYYY"),
        "Nota_de_empenho": st.column_config.TextColumn(label="Nota de Empenho"),
        "sigla": st.column_config.TextColumn(label="Unidade Gestora"),
        "Unidade_orçamentária": st.column_config.TextColumn(label="Unidade Orçamentária"),
        "Despesas_empenhadas": st.column_config.NumberColumn(label="Valor das Despesas Empenhadas"),
        "Despesas_liquidadas": st.column_config.NumberColumn(label="Valor das Despesas Liquidadas"),
        "Despesas_pagas": st.column_config.NumberColumn(label="Valor das Despesas Pagas")
    }

    # Exibe a tabela no Streamlit
    st.dataframe(
        df_tab,
        column_config=column_config,
        hide_index=True,
        width=1600,
        height=600,
        use_container_width=True
    )

     # Crie um buffer para armazenar o arquivo Excel
    buffer = io.BytesIO()

    # Salve o DataFrame no buffer no formato Excel
    df.to_excel(buffer, index=False, engine='openpyxl')

    # Rewind the buffer to the beginning before serving it
    buffer.seek(0)

    # Crie o botão de download com o arquivo .xls
    st.download_button(
        label="Baixar Tabela",
        data=buffer,
        file_name="Obras.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
