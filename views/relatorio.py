import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import streamlit.components.v1 as components
import locale


##################### carregar dados ##############################

# Configuração de locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

st.set_page_config(
    page_title="Relatório de Obras",
    layout="wide",
    menu_items={
        'Get Help': 'https://www.google.com'
    }
)
# Função para carregar os dados
def carregar_dados():
    resultado_final = pd.read_csv("./assets/dados_obra.csv", sep=";", encoding="utf-8")
    return resultado_final

# Carregar os dados usando a função com cache
df = carregar_dados()

# Inicializar o DataFrame no estado da sessão, se ainda não estiver definido
if 'df_inicio' not in st.session_state:
    st.session_state.df_inicio = df.copy()
df_inicio = st.session_state.df_inicio


st.markdown("""
    <style>          
    /* Ocultar a barra superior do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Alterar o fundo da página */
    /* Alterar o fundo do elemento específico */
    .appview-container.st-emotion-cache-1yiq2ps.ea3mdgi9 {
        background-color: rgb(237, 237, 237); /* Cor de fundo desejada */
    }
    .st-cc.st-bn.st-ar.st-cd.st-ce.st-cf{
    color: rgb(0, 0, 0);  /* Cor do placeholder */
    }   
    .css-hhhz79 e1fqkh3o2 { 
        color: rgb(0, 0, 0);  /* Cor desejada para o subheader */
    }
    
    /* Ajustar o posicionamento do bloco vertical */
    [data-testid="stVerticalBlock"] {
        margin-top: 0 !important; /* Remove o espaço acima do bloco */
        padding-top: 0 !important; /* Remove o preenchimento acima do bloco */
        position: relative; /* Garante que o elemento se posicione de forma relativa */
        top: 0; /* Move para o topo */
    }
    [data-testid="stHeaderActionElements"] {
        visibility: hidden;
        display: none;
    }
    [data-testid="StyledFullScreenButton"]{
        visibility: hidden;
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)



############### cores ##############

def generate_colors(num_categorias, color_palette): 
    colors = color_palette * (num_categorias // len(color_palette)) + color_palette[:num_categorias % len(color_palette)]
    return colors
corazul = ['#052E59']
corverde =['#355e2a']
colors_base = ['#052E59','#517496', '#7A89B2', '#A0ADCC', '#C4D1E2']
def configurar_layout(fig):
    fig.update_layout(
     #   paper_bgcolor='rgb(237, 237, 237)',  # Cor de fundo do papel
     #   plot_bgcolor='rgb(237, 237, 237)',   # Cor de fundo do gráfico
        font=dict(color='rgb(0, 0, 0)'),     # Cor da fonte
        xaxis=dict(title_font=dict(color='rgb(0, 0, 0)')),  
        yaxis=dict(title_font=dict(color='rgb(0, 0, 0)')),
        legend=dict(
            itemclick=False,  # Desativa o clique na legenda
            itemdoubleclick=False  # Desativa o duplo clique na legenda
        )   
    )
    return fig
def converte_br(numero):
    suf = {
        1e3:"K",
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

    # Se não se encaixar em nenhum sufixo, retorna o número formatado como moeda
    return f"{'-' if negativo else ''}{locale.currency(numero, grouping=True, symbol='R$')}"

###################################### CRIAÇÃO DE GRÁFICOS ###################################
def grafico1(df):    
    # Agrupar e somar despesas por beneficiário, ordenando de forma decrescente
    graf1 = df.groupby('Empresa')["Despesas_empenhadas"].sum().nlargest(10)  # Obter os 10 maiores valores
    entidade_top_1 = graf1.index[0]
    
    # Calcular o total de adiantamentos da entidade top 1
    total_adiantamentos = graf1.values[0]  
    total_adiantamentos = converte_br(total_adiantamentos)

    # Gerar cores
    corgrafico1 = generate_colors(len(graf1), corazul)
    
    # Criar o gráfico
    fig = px.bar(
        x=graf1.values,              # Total de despesas no eixo X
        y=graf1.index,               # Nomes dos beneficiários no eixo Y
        orientation='h'
    )
    
    # Atualizar o layout do gráfico
    fig.update_layout(
        xaxis=dict(title=''),
        yaxis=dict(title='', autorange='reversed'),  # Inverte a ordem do eixo Y
        xaxis_fixedrange=True,
        yaxis_fixedrange=True
    )
    
    # Atualizar traços do gráfico
    fig.update_traces(
        marker=dict(color=corgrafico1),
        hovertemplate=("Nome: <b>%{y}</b><br>Total: <b>%{x}</b><br>"),
        hoverlabel=dict(font_size=13)
    )
    
    # Configurando o layout
    configurar_layout(fig)
    
    return fig, total_adiantamentos, entidade_top_1
# Gráfico 2 - Total de despesas empenhadas por ano
def grafico2(df):
    graf2 = df.groupby('Ano')["Despesas_empenhadas"].sum()
    total_adiantamentos = graf2.sum()
    total_adiantamentos = converte_br(total_adiantamentos)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
            x=graf2.index,
            y=graf2.values,
            mode='lines+markers',
            fill='tozeroy',  
            fillcolor='rgba(5, 46, 89, 0.35)',  
            line=dict(color='#052E59'),  
            marker=dict(color=corazul, size=6),
            name='',
            hovertemplate=("Ano: <b>%{x}</b><br>Total: <b>%{customdata}</b><br>"),
            customdata=[converte_br(valor) for valor in graf2.values]  # Adiciona o valor formatado
        ))


    
    fig.update_layout(
        xaxis_tickangle=0,
        yaxis=dict(title=None),
        xaxis_fixedrange=True,
        yaxis_fixedrange=True,
        height=360
    )
    
    configurar_layout(fig)
    return fig, total_adiantamentos


# Gráfico 3 - Notas de empenho distintas por unidade gestora
def grafico3(df):
    graf3 = df.groupby('sigla')['Nota_de_empenho'].nunique()
    top_5_categorias = graf3.sort_values(ascending=False)[:7]
    outros_valores_sum = graf3[~graf3.index.isin(top_5_categorias.index)].sum()
    linha_outros = pd.Series({'Outros': outros_valores_sum})
    df_agrupado2_ajustado = pd.concat([top_5_categorias, linha_outros])

    corgrafico3 = generate_colors(len(df_agrupado2_ajustado), colors_base)
    idx_outros = df_agrupado2_ajustado.index.get_loc('Outros')
    corgrafico3[idx_outros] = corverde

    fig = go.Figure(data=[go.Pie(
        labels=df_agrupado2_ajustado.index,
        values=df_agrupado2_ajustado.values,
        hole=0.5,
        textinfo='percent',
        hovertemplate='Total de notas de empenho:%{value}<extra></extra>',
        marker=dict(colors=corgrafico3, line=dict(color='black', width=0.2))
    )])
    fig.update_layout(margin=dict(t=75, b=30, l=0, r=0), height=350, title='')
    fig.update_traces(hoverlabel=dict(font_size=13))

    configurar_layout(fig)
    # Calcular a unidade gestora com mais notas de empenho
    unidade_gestora_com_maior_ne = top_5_categorias.idxmax()
    valor = top_5_categorias.max()

    return fig, unidade_gestora_com_maior_ne, valor  # Retornar o gráfico e as informações necessárias

# Gráfico 4 - Unidade gestora por total de despesas empenhadas
def grafico4(df):
    graf4 = df.groupby('sigla')[['Despesas_empenhadas', 'Despesas_liquidadas', 'Despesas_pagas']].sum().sort_values(by='Despesas_empenhadas', ascending=False).reset_index()[:5]
    
    # Capturando as informações das 3 unidades gestoras
    unidade_gestora_1 = graf4.iloc[0]['sigla']
    valor_empenhado_1 = graf4.iloc[0]['Despesas_empenhadas']
    valor_liquidado_1 = graf4.iloc[0]['Despesas_liquidadas']
    valor_pago_1 = graf4.iloc[0]['Despesas_pagas']
    
    unidade_gestora_2 = graf4.iloc[1]['sigla']
    valor_empenhado_2 = graf4.iloc[1]['Despesas_empenhadas']
    valor_liquidado_2 = graf4.iloc[1]['Despesas_liquidadas']
    valor_pago_2 = graf4.iloc[1]['Despesas_pagas']
    
    unidade_gestora_3 = graf4.iloc[2]['sigla']
    valor_empenhado_3 = graf4.iloc[2]['Despesas_empenhadas']
    valor_liquidado_3 = graf4.iloc[2]['Despesas_liquidadas']
    valor_pago_3 = graf4.iloc[2]['Despesas_pagas']

    # Gerar gráfico
    cor = ['#052E59', '#517496', '#7A89B2']
    corgrafico4 = cor * len(graf4)

    fig = px.bar(
        graf4,
        x='sigla',
        y=['Despesas_empenhadas', 'Despesas_liquidadas', 'Despesas_pagas'],
        color_discrete_sequence=corgrafico4,
        barmode='group'
    )
    fig.update_layout(
        xaxis=dict(title=''),
        yaxis=dict(title=''),  
        xaxis_fixedrange=True,
        yaxis_fixedrange=True
    )
    configurar_layout(fig)

    fig.for_each_trace(lambda trace: trace.update(name={
        'Despesas_empenhadas': 'Despesa Empenhada',
        'Despesas_liquidadas': 'Despesa Liquidada',
        'Despesas_pagas': 'Despesa Paga'
    }[trace.name]))

    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Total de despesas: R$%{y:,.2f}<extra></extra>",
        hoverlabel=dict(font_size=13)
    )
    configurar_layout(fig)

    return fig, unidade_gestora_1, valor_empenhado_1, valor_liquidado_1, valor_pago_1, \
           unidade_gestora_2, valor_empenhado_2, valor_liquidado_2, valor_pago_2, \
           unidade_gestora_3, valor_empenhado_3, valor_liquidado_3, valor_pago_3



# Gráfico 5 - Quantidade de Notas por Faixa de Valor
def grafico5(df):
    bins = [0, 1000, 5000, 10000, 50000, 100000, 1000000]
    labels = [
    'Abaixo de R$ 1.000',
    'R$ 1.000 a R$ 5.000',
    'R$ 5.000 a R$ 10.000',
    'R$ 10.000 a R$ 50.000',
    'R$ 50.000 a R$ 100.000',
    'R$ 100.000 a R$ 1.000.000']

    df['faixa'] = pd.cut(df['Despesas_empenhadas'], bins=bins, labels=labels, right=False)

    # Count the occurrences in each faixa
    contagem_faixa = df['faixa'].value_counts().reset_index()
    contagem_faixa.columns = ['faixa', 'quantidade']
    
    # Calculate total notes and percentage
    total_notas = contagem_faixa['quantidade'].sum()
    contagem_faixa['percentual'] = (contagem_faixa['quantidade'] / total_notas) * 100

    # Get the faixa with the largest quantity using nlargest
    maior_faixa_row = contagem_faixa.nlargest(1, 'quantidade').iloc[0]
    maior_faixa = maior_faixa_row['faixa']
    numero_maior_faixa = maior_faixa_row['quantidade']
    percentual_maior_faixa = maior_faixa_row['percentual']

    # Sort the entire DataFrame in descending order for the graph
    contagem_faixa = contagem_faixa.sort_values(by='quantidade')

    corgrafico5 = generate_colors(len(contagem_faixa), corazul)

    fig = px.bar(contagem_faixa, x='quantidade', y='faixa', orientation='h', 
                  labels={'quantidade': 'Quantidade de Notas', 'faixa': 'Faixa de Valores'})

    fig.update_layout(xaxis_title='Quantidade de Notas', yaxis_title='Faixa de Valores')
    fig.update_traces(marker=dict(color=corgrafico5), 
                      hovertemplate=("Faixa: <b>%{y}</b><br>Total de Notas de Empenho: <b>%{x}</b>"))
    
    # Remove text labels inside the bars
    fig.for_each_trace(lambda trace: trace.update(text=[]))

    configurar_layout(fig)
    
    return fig, maior_faixa, numero_maior_faixa, percentual_maior_faixa


################################################# LAYOUT ################################################
df_filtrado = df_inicio.copy()




st.markdown("<h1 style='text-align: center;'>Relatório de Obras</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align: left; font-family: Arial, sans-serif; font-size: 15px; font-weight: normal;'>
    
<p style="text-align: left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;">
    
</p>

""", unsafe_allow_html=True)

df['Atualizado_em'] = pd.to_datetime(df['Atualizado_em'], format='%Y-%m-%d %H:%M:%S')
ultima_atualizacao = df['Atualizado_em'].max().strftime('%d/%m/%Y %H:%M')


#df_inicio['Ano'] = df_inicio['Data_emissão_ne'].dt.year 

if 'Ano' not in st.session_state:
    st.session_state['Ano'] = []

# Filtro de ano
#ano = st.multiselect("",sorted(map(str, df_inicio['Ano'].unique().tolist())),placeholder="Selecione um ano")
ano = st.multiselect(
    "Ano",
    sorted(map(str, df_inicio['Ano'].unique().tolist())),
    placeholder="Selecione um ano",
    label_visibility="collapsed"
)

# Atualizar o DataFrame filtrado
if ano:
    df_filtrado = df_inicio[df_inicio['Ano'].isin(map(int, ano))]
    st.session_state['Ano'] = ano
else:
    df_filtrado = df_inicio


# Layout dos KPIs
# Cálculo dos valores KPI
kpi1_value = df_filtrado['Despesas_empenhadas'].sum()
kpi2_value = df_filtrado['Despesas_pagas'].sum()
kpi3_value = df_filtrado['Nota_de_empenho'].nunique()
kpi4_value = df_filtrado['Despesas_liquidadas'].sum()
# Layout das métricas no Streamlit
kpi1, kpi2,kpi3,kpi4 = st.columns(4)

# Exibir as métricas
kpi1.metric("Total de despesas empenhadas", f"R$ {converte_br(kpi1_value)}")
kpi2.metric("Total de despesas pagas", f"R$ {converte_br(kpi2_value)}")
kpi3.metric("Nota de empenho distintas", f"{kpi3_value}")
kpi4.metric("Total de despesas liquidadas", f"R$ {converte_br(kpi4_value)}")


#Gráfico 1
st.subheader("Total de despesa empenhada por fornecedor")

# Obter os dados do gráfico e as variáveis necessárias
fig1,total_adiantamentos,entidade_top_1 = grafico1(df_filtrado)

# Texto descritivo para o gráfico
if ano:
    st.markdown(f"""
        <p style='text-align:left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;'>
            No ano de  <b>{', '.join(ano)}</b>, o fornecedor com maior valor empenhado  foi <b>{entidade_top_1}</b>, 
             com um total de <b>{total_adiantamentos}</b>.
        </p>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <p style='text-align:left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;'>
            o fornecedor com maior valor empenhado  foi <b>{entidade_top_1}</b>, 
             com um total de <b>{total_adiantamentos}</b>.
        </p>
    """, unsafe_allow_html=True)


st.plotly_chart(fig1, use_container_width=True)

#Grafico 2
st.subheader("Total de despesas empenhadas por ano")

# Obter os dados do gráfico e as variáveis necessárias
fig2, total_adiantamentos = grafico2(df_filtrado)

# Texto descritivo para o gráfico
if ano:
    st.markdown(f"""
    <p style='text-align:left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;'>
        No ano de <b>{', '.join(ano)}</b>, o valor total empenhado  foi de <b>{total_adiantamentos}</b>.
    </p>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <p style='text-align:left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;'>
        o valor total empenhado  foi de <b>{total_adiantamentos}</b>.
    </p>
    """, unsafe_allow_html=True)

st.plotly_chart(fig2, use_container_width=True)

#Gráfico 3
st.subheader("Notas de Empenho Distintas por Unidade Gestora")
fig3,unidade_gestora_com_maior_ne,valor= grafico3(df_filtrado)

# Texto descritivo para o gráfico
if ano:
    st.markdown(f"""
    <p style='text-align:left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;'>
        No ano de <b>{', '.join(ano)}</b>, a unidade gestora com o maior número de notas de empenho foi <b>{unidade_gestora_com_maior_ne}</b>, 
        totalizando <b>{valor}</b> notas de empenho distintas. 
    </p>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <p style='text-align:left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;'>
        A unidade gestora com o maior número de notas de empenho foi <b>{unidade_gestora_com_maior_ne}</b>, 
        totalizando <b>{valor}</b> notas de empenho distintas. 
    </p>
    """, unsafe_allow_html=True)

st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4
st.subheader("Unidade Gestora por Total de Despesas Empenhada")
# Chamar a função e armazenar o gráfico e as variáveis
fig4, unidade_gestora_1, valor_empenhado_1, valor_liquidado_1, valor_pago_1, \
    unidade_gestora_2, valor_empenhado_2, valor_liquidado_2, valor_pago_2, \
    unidade_gestora_3, valor_empenhado_3, valor_liquidado_3, valor_pago_3 = grafico4(df_filtrado)
if ano:
    st.markdown(f"""
    <p style='text-align:left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;'>
        No ano de <b>{', '.join(ano)}</b>, a unidade gestora com o maior valor destinado foi <b>{unidade_gestora_1}</b>. Este órgão empenhou um total impressionante de <b>{converte_br(valor_empenhado_1)}</b>, dos quais <b>{converte_br(valor_liquidado_1)}</b> foram efetivamente liquidadas e <b>{converte_br(valor_pago_1)}</b> já foram pagos. 
        Em segundo lugar, a unidade gestora <b>{unidade_gestora_2}</b> se destacou com um empenho de <b>{converte_br(valor_empenhado_2)}</b>, resultando em <b>{converte_br(valor_liquidado_2)}</b> liquidado e <b>{converte_br(valor_pago_2)}</b> pago. 
        Por fim, a terceira posição ficou com <b>{unidade_gestora_3}</b>, que registrou <b>{converte_br(valor_empenhado_3)}</b> empenhados, com <b>{converte_br(valor_liquidado_3)}</b> já liquidadas e <b>{converte_br(valor_pago_3)}</b> pagos.
    </p>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <p style='text-align:left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;'>
        A unidade gestora que mais se destacou em termos de valores destinados foi <b>{unidade_gestora_1}</b>, com um total de <b>{converte_br(valor_empenhado_1)}</b> empenhados, dos quais <b>{converte_br(valor_liquidado_1)}</b> foram liquidadas e <b>{converte_br(valor_pago_1)}</b> pagos. 
        Em segundo lugar, encontramos a unidade gestora <b>{unidade_gestora_2}</b>, que alcançou um empenho de <b>{converte_br(valor_empenhado_2)}</b>, resultando em <b>{converte_br(valor_liquidado_2)}</b> liquidadas e <b>{converte_br(valor_pago_2)}</b> pagos. 
         Por fim, a terceira posição ficou com <b>{unidade_gestora_3}</b>, que registrou <b>{converte_br(valor_empenhado_3)}</b> empenhados, com <b>{converte_br(valor_liquidado_3)}</b> já liquidadas e <b>{converte_br(valor_pago_3)}</b> pagos.
    </p>
    """, unsafe_allow_html=True)

st.plotly_chart(fig4, use_container_width=True)


#Gráfico 5
st.subheader("Quantidade de Notas por Faixa de Valor")
fig5, maior_faixa, numero_maior_faixa, percentual_maior_faixa = grafico5(df_filtrado)

if ano:
    st.markdown(f"""
    <p style='text-align:left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;'>
        No ano de <b>{', '.join(ano)}</b>, as notas de empenho estavam predominantemente concentradas na faixa de <b>{maior_faixa}</b>, representando um total de <b>{numero_maior_faixa}</b> notas, o que corresponde a <b>{percentual_maior_faixa:.2f}%</b> do total.
    </p>
    """, unsafe_allow_html=True)

else:
    st.markdown(f"""
    <p style='text-align:left; font-family: Arial, sans-serif; font-size: 17px; font-weight: normal;' >
         as notas de empenho estão predominantemente concentradas na faixa de <b>{maior_faixa}</b>, representando um total de <b>{numero_maior_faixa}</b> notas, o que corresponde a <b>{percentual_maior_faixa:.2f}%</b> do total.

    </p>
    """, unsafe_allow_html=True)
st.plotly_chart(fig5, use_container_width=True)

