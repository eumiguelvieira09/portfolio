#Versão 1.1

import streamlit as st
import pandas as pd
import plotly.express as px
import io
import reportlab
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
import tempfile
import os
from PIL import Image, ImageEnhance
#import openpyxl
import traceback
import sys


logo = Image.open(r'assets/Adidas_Logo.png')
logo = Image.open("assets/Adidas_Logo.png").convert("RGBA")
white_background = Image.new("RGBA", logo.size, (255, 255, 255, 255))
white_background.paste(logo, (0, 0), mask=logo)

final_logo = white_background.convert("RGB")

# # Salva a imagem corrigida em um arquivo temporário
with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
    final_logo.save(tmpfile.name, format="PNG")  # Salva sem transparência
    logo_path = tmpfile.name


# watermark_img = Image.open(r'static/marca.png')
# watermark_img = Image.open("static/marca.png").convert("RGBA")
# white_background = Image.new("RGBA", watermark_img.size, (255, 255, 255, 255))
# white_background.paste(watermark_img, (0, 0), mask=watermark_img)

# final_watermark_img = white_background.convert("RGB")

# # # Salva a imagem corrigida em um arquivo temporário
# with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
#     watermark_img.save(tmpfile.name, format="PNG")  # Salva sem transparência
#     watermark_img_path = tmpfile.name


#icone = Image.open("./static/favicon-cge.ico")
dash = "fabrica-de-relatorio"

#VERSAO COM DUAS ABAS 
# APARECE UM AVISO PARA SELECIONAR TODOS OS KPIS
#FUNÇÃO PARA CRIAR UM RELATÓRIO NA SEGUNDA ABA TAMBÉM 
#VERSÃO 0.6

st.set_page_config(
    page_title="Fábrica de Relatório",
    layout="wide",
    initial_sidebar_state="collapsed"

    )

def load_css():
    with open('assets/styles.css') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Renderizar o título de maneira estática
def render_header(title):
    st.markdown(f"""
        <div class="header-bar">
            <span class="header-title">{title}</span>
        </div>
        """, unsafe_allow_html=True)

load_css()
render_header('SISGRAD - Sistema Gerador de Relatórios para Análise de Dados')

corazul = ['#052E59']
corverde =['#355e2a']

graficos = {}
kpis = {}


def show_warning():
    st.markdown(
    """
    <div class="warning-container">
        Alguma coluna do seu documento possui formato inválido. <br>
        Por favor, verifique se as colunas estão no formato do tipo de variável. <br>
        Por exemplo: Se as datas estão no formato de data.
    </div>
    """,
    unsafe_allow_html=True
    )


# def erro():
#     st.markdown(
#         """
#         <div class="erro">
#             Algo deu errado. Tente novamente! <br>
#             Em caso de persistência, entre em contato com o time de dados através dos canais <a href="http://10.11.82.21:3500/" target="_blank" style="color: white;">Help Desk </a> ou 
#             helpdesk@cge.rj.gov.br <br>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )
#     st.stop()

# def main():

def truncar_legenda(legenda, max_char=10):
    if len(legenda) > max_char:
        return legenda[:max_char] + "..."  # Trunca e adiciona "..."
    return legenda

def create_graph(graph_num, df):
    st.subheader(f"Gráfico {graph_num}")
    
    var1 = st.selectbox(f"Selecione a variável 1", [""] + list(df.columns), key=f"graph{graph_num}_var1")
    
    if var1:
        if df[var1].dtype in ['float64', 'int64']:  # Variável 1 numérica
            var2 = st.selectbox(f"Selecione a variável 2 ", [""] + list(df.select_dtypes(include=['float64', 'int64', 'object', 'category']).columns), key=f"graph{graph_num}_var2")
        else:  # Variável 1 categórica
            var2 = st.selectbox(f"Selecione a variável 2 ", [""] + list(df.select_dtypes(include=['float64', 'int64']).columns), key=f"graph{graph_num}_var2")
        
    graph_type = st.selectbox(f"Tipo de Gráfico ", [""] + ['Histograma', 'Dispersão', 'Linha', 'Barras', 'Pizza'], key=f"graph{graph_num}_type")
    comentario = st.text_area(f"Comentário sobre o Gráfico ", key=f"graph{graph_num}_comment")
    
    if var1 and graph_type:
        titulo = f"Relação entre {var1} e {var2}" if var2 else f"Distribuição de {var1}"
        
        if graph_type == 'Histograma':
            top_10_values = df[var1].value_counts().nlargest(10).index
            df_filtered_hist = df[df[var1].isin(top_10_values)]
            df_filtered_hist[var1] = df_filtered_hist[var1].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)
            fig = px.histogram(df_filtered_hist, x=var1, color=var2 if var2 else None, title=titulo)
            fig.update_traces(marker=dict(color="blue"))  # Define a cor azul para todos os pontos

        
        elif graph_type == 'Dispersão' and var2:
            df_sample = df.sample(frac=0.3, random_state=42) if df[var1].dtype in ['float64', 'int64'] and df[var2].dtype in ['float64', 'int64'] else df
            fig = px.scatter(df_sample, x=var1, y=var2, title=titulo)
            fig.update_traces(marker=dict(color="blue"))  # Define a cor azul para todos os pontos

        elif graph_type == 'Linha' and var2:
            # Se var1 for categórica
            if df[var1].dtype in ['object', 'category']:
                # Se var2 for fornecida (e for numérica), agrupar por var1 e somar os valores de var2
                if df[var2].dtype in ['float64', 'int64']:
                    # Agrupar por var1 e somar os valores de var2
                    df_grouped = df.groupby(var1, as_index=False)[var2].sum()
                    # Ordenar pela soma de var2 de forma decrescente e pegar as 10 mais altas
                    df_grouped = df_grouped.sort_values(by=var2, ascending=False).head(10)
                    # Criar gráfico de linha com as 10 categorias top
                    df_grouped[var1] = df_grouped[var1].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)

                    fig = px.line(df_grouped, x=var1, y=var2, title=f"Top 10 Categorias de {var1} - {var2}")
                else:
                    # Se var2 não for fornecida, realizar apenas a contagem das 10 categorias mais frequentes de var1
                    df_grouped = df[var1].value_counts().head(10).reset_index()
                    df_grouped.columns = [var1, 'Contagem']
                    # Ordenar para garantir que o eixo x esteja correto
                    df_grouped = df_grouped.sort_values(by=var1)
                    # Criar gráfico de linha com as 10 categorias mais frequentes
                    df_grouped[var1] = df_grouped[var1].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)

                    fig = px.line(df_grouped, x=var1, y='Contagem', title=f"Top 10 Categorias de {var1}")
            
            # Se var1 for numérica
            elif df[var1].dtype in ['float64', 'int64']:
                # Se var2 for fornecida (e for numérica), agrupar var1 e somar var2
                if df[var2].dtype in ['float64', 'int64']:
                    # Agrupar var1 em intervalos (ou usar outra lógica de agrupamento) e somar os valores de var2
                    df_grouped = df.groupby(var1, as_index=False)[var2].sum()
                    # Ordenar para garantir a sequência correta no eixo X
                    df_grouped = df_grouped.sort_values(by=var1)
                    # Criar gráfico de linha com var1 no eixo X (numérico) e a soma de var2
                    df_grouped[var1] = df_grouped[var1].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)
                    fig = px.line(df_grouped, x=var1, y=var2, title=f"Gráfico de Linha - {var1} x {var2}")
                else:
                    # Se var2 não for fornecida, realizar apenas a contagem das ocorrências de var1
                    df_grouped = df[var1].value_counts().reset_index()
                    df_grouped.columns = [var1, 'Contagem']
                    # Ordenar para garantir a sequência correta no eixo X
                    df_grouped = df_grouped.sort_values(by=var1)
                    # Criar gráfico de linha com as contagens de var1
                    df_grouped[var1] = df_grouped[var1].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)
                    fig = px.line(df_grouped, x=var1, y='Contagem', title=f"Contagem de {var1}")

            fig.update_traces(marker=dict(color="blue"))  # Definir a cor azul para todos os pontos




        
        elif graph_type == 'Barras':
            if df[var1].dtype in ['object', 'category']:  # Quando var1 é categórica
                # Obter as 10 categorias mais frequentes de var1
                
                #top_10_categories = df[var1].value_counts().nlargest(10).index
                #df_filtered = df[df[var1].isin(top_10_categories)]
                
                if var2:  # Se var2 for fornecida
                    # Agrupar por var1 e somar os valores de var2
                    df_filtered = df.groupby(var1, as_index=False)[var2].sum()  # Agrupar e somar
                    df_filtered = df_filtered.sort_values(by=var2, ascending=False)  # Ordenar pela soma de var2 de forma decrescente
                    df_filtered = df_filtered.head(10)  # Selecionar as 10 primeiras categorias com maior soma de var2
                    # Ordenar os dados pela soma de var2 de forma decrescente
                    #df_filtered = df_filtered.sort_values(by=var2, ascending=False)
                    df_filtered[var1] = df_filtered[var1].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)
                    fig = px.bar(df_filtered, x=var1, y=var2, title=f"Top 10 Categorias de {var1} - {var2}")
                    fig.update_traces(marker=dict(color="blue"))  # Define a cor azul para todos os pontos

                else:  # Quando var2 não for fornecida
                    # Apenas contar as ocorrências das 10 categorias mais frequentes
                    top_10_counts = df[var1].value_counts().nlargest(10)
                    top_10_df = top_10_counts.reset_index()
                    top_10_df.columns = [var1, 'Contagem']
                    top_10_df[var1] = top_10_df[var1].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)
                    fig = px.bar(top_10_df, x=var1, y='Contagem', title=f"Top 10 Categorias de {var1}", labels={var1: f"Contagem de {var1}"})
                    fig.update_traces(marker=dict(color="blue"))  # Define a cor azul para todos os pontos

            else:  # Se var1 não for categórica, só criar o gráfico de barras normal
                df[var1] = df[var1].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)
                fig = px.bar(df, x=var1, y=var2, title=titulo)
                fig.update_traces(marker=dict(color="blue"))  # Define a cor azul para todos os pontos



        elif graph_type == 'Pizza':
            if var2:  # Categórica + Numérica
                top_5_categories = df.groupby(var1, as_index=False)[var2].sum().nlargest(5, var2)
                top_5_categories[var1] = top_5_categories[var1].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)
                fig = px.pie(top_5_categories, values=var2, names=var1, title=f"Top 5 {var1} baseado em {var2}", color_discrete_sequence=["blue"])
            else:  # Apenas Categórica
                top_5_counts = df[var1].value_counts().nlargest(5)
                top_5_df = top_5_counts.reset_index()
                top_5_df.columns = [var1, 'Contagem']
                top_5_df[var1] = top_5_df[var1].apply(lambda x: x[:15] + '...' if len(x) > 15 else x)

                fig = px.pie(top_5_df, values='Contagem', names=var1, title=f"Top 5 Categorias de {var1}", color_discrete_sequence=["blue"])



        else:
            fig = None



        if fig:
            st.plotly_chart(fig)
            temp_img_path = os.path.join(tempfile.gettempdir(), f"grafico_{graph_num}.png")
            fig.write_image(temp_img_path)
            graficos[f"Gráfico {graph_num}"] = {"fig": fig, "img_path": temp_img_path, "comentario": comentario}


def calcular_kpi(df, metrica, variavel):
    if not variavel:
        return None
    
    if metrica == "Média":
        return round(df[variavel].mean(), 2)
    elif metrica == "Soma":
        return round(df[variavel].sum(), 2)
    elif metrica == "Contagem de Valores Únicos":
        return df[variavel].nunique()
    elif metrica == "Máximo":
        return round(df[variavel].max(), 2)
    elif metrica == "Mínimo":
        return round(df[variavel].min(), 2)
    elif metrica == "Moda":
        return df[variavel].mode().values[0] if not df[variavel].mode().empty else None
    else:
        return None


###################################################################################

def upload_data():
    st.subheader("Escolha um arquivo CSV ou Excel")
    uploaded_file = st.file_uploader(" ", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')  # Detecta automaticamente o separador
        else:
            df = pd.read_excel(uploaded_file)
        
        st.write(f"Conjunto de dados carregado: {uploaded_file.name}")
        st.dataframe(df.head())
        return df, uploaded_file.name
    
    return None, None

def create_filters(df):
    st.sidebar.header("Filtros")

    # Selecione as colunas para filtrar (limite de 5 filtros)
    selected_columns = st.sidebar.multiselect("Selecione até 5 colunas para filtrar", df.columns.tolist(), max_selections=5)

    # Para cada coluna selecionada, adicione um filtro
    filters = {}
    for col in selected_columns:
        unique_values = df[col].unique().tolist()
        filter_value = st.sidebar.selectbox(f"Selecione um valor para filtrar a coluna {col}", options=["Todos"] + unique_values)
        filters[col] = filter_value
    
    return filters

def apply_filters(df, filters):
    filtered_df = df
    for col, filter_value in filters.items():
        if filter_value != "Todos":
            filtered_df = filtered_df[filtered_df[col] == filter_value]
    return filtered_df

# Carregar dados
df, file_name = upload_data()

if df is not None:
    # Criar filtros com base nas colunas selecionadas pelo usuário
    filters = create_filters(df)

    # Aplicar os filtros ao dataframe
    filtered_df = apply_filters(df, filters)



##################################################################################

st.divider() 

if df is not None:
    st.markdown("""
            <style>
            /* Estilos do texto principal */
            .hover-text {
                font-family: 'Roboto', sans-serif; /* Fonte para o texto principal */
                font-size: 32px; /* Tamanho da fonte */
                color: #000000; /* Cor do texto */
                font-weight: bold; /* Negrito */
            }

            /* Estilos da tooltip (texto que aparece ao passar o mouse) */
            .hover-text .tooltip {
                font-family: 'Roboto'; /* Fonte da tooltip */
                font-size: 14px; /* Tamanho da fonte da tooltip */
                font-weight: normal;
            }

            .hover-text {
                position: relative;
                display: inline-block;
                cursor: pointer;
            }

            .hover-text .tooltip {
                visibility: hidden;
                width: 200px;
                background-color: #6c757d;
                color: #fff;
                text-align: center;
                border-radius: 5px;
                padding: 5px;
                position: absolute;
                z-index: 1;
                bottom: 100%;
                left: 50%;
                margin-left: -100px;
                opacity: 0;
                transition: opacity 0.3s;
            }

            .hover-text:hover .tooltip {
                visibility: visible;
                opacity: 1;
            }
            </style>

            <div class="hover-text">
                Dados do Relatório
                <div class="tooltip">Nessa sessão do Sistema, você adicionará as Inforções do Responsável pelo Relatório.</div>
            </div>
        """, unsafe_allow_html=True)
    nome_relatorio = st.text_input("Nome do Relatório")
    nome_responsavel = st.text_input("Nome do Responsável")
    setor = st.text_input("Setor")
    tab1, tab2, tab3 = st.tabs(["Aba relatório", "Aba Visão Dashboard", "Tabela Geral"])
    with tab1:

        st.markdown("""
            <style>
            /* Estilos do texto principal */
            .hover-text {
                font-family: 'Roboto', sans-serif; /* Fonte para o texto principal */
                font-size: 32px; /* Tamanho da fonte */
                color: #000000; /* Cor do texto */
                font-weight: bold; /* Negrito */
            }

            /* Estilos da tooltip (texto que aparece ao passar o mouse) */
            .hover-text .tooltip {
                font-family: 'Roboto'; /* Fonte da tooltip */
                font-size: 14px; /* Tamanho da fonte da tooltip */
                font-weight: normal;
            }

            .hover-text {
                position: relative;
                display: inline-block;
                cursor: pointer;
            }

            .hover-text .tooltip {
                visibility: hidden;
                width: 200px;
                background-color: #6c757d;
                color: #fff;
                text-align: center;
                border-radius: 5px;
                padding: 5px;
                position: absolute;
                z-index: 1;
                bottom: 100%;
                left: 50%;
                margin-left: -100px;
                opacity: 0;
                transition: opacity 0.3s;
            }

            .hover-text:hover .tooltip {
                visibility: visible;
                opacity: 1;
            }
            </style>

            <div class="hover-text">
                Criação de Indicadores
                <div class="tooltip">Nessa sessão do Sistema, você criará os Indicadores e Métricas que estarão no seu relatório.</div>
            </div>
        """, unsafe_allow_html=True)

        
        col1, col2, col3, col4 = st.columns(4)
        metricas_disponiveis = ["Média", "Soma", "Contagem de Valores Únicos", "Máximo", "Mínimo", "Moda"]

# Criar KPIs dinamicamente
        def criar_kpi(col, df, key):
            with col:
                variavel = st.selectbox(f"Variável para {key}", [""] + list(df.select_dtypes(include=['number']).columns), key=f"var_{key}")
                metrica = st.selectbox(f"Métrica para {key}", metricas_disponiveis, key=f"metric_{key}")
                comentario = st.text_area(f"Comentário sobre {key}", key=f"comment_{key}")
                
                if variavel and metrica:
                    valor_kpi = calcular_kpi(df, metrica, variavel)
                    if valor_kpi is not None:
                        st.metric(label=f"{metrica} de {variavel}", value=valor_kpi)
                        return {key: {"descricao": f"{metrica} de {variavel}: {valor_kpi}", "valor_kpi": valor_kpi, "comentario": comentario}}
            return {}

        # Dicionário para armazenar KPIs
        kpis = {}
        kpis.update(criar_kpi(col1, df, "Indicador1"))
        kpis.update(criar_kpi(col2, df, "Indicador2"))
        kpis.update(criar_kpi(col3, df, "Indicador3"))
        kpis.update(criar_kpi(col4, df, "Indicador4"))

        st.divider() 


        st.markdown("""
            <style>
            /* Estilos do texto principal */
            .hover-text {
                font-family: 'Roboto', sans-serif; /* Fonte para o texto principal */
                font-size: 32px; /* Tamanho da fonte */
                color: #000000; /* Cor do texto */
                font-weight: bold; /* Negrito */
            }

            /* Estilos da tooltip (texto que aparece ao passar o mouse) */
            .hover-text .tooltip {
                font-family: 'Roboto'; /* Fonte da tooltip */
                font-size: 14px; /* Tamanho da fonte da tooltip */
                font-weight: normal;
            }

            .hover-text {
                position: relative;
                display: inline-block;
                cursor: pointer;
            }

            .hover-text .tooltip {
                visibility: hidden;
                width: 200px;
                background-color: #6c757d;
                color: #fff;
                text-align: center;
                border-radius: 5px;
                padding: 5px;
                position: absolute;
                z-index: 1;
                bottom: 100%;
                left: 50%;
                margin-left: -100px;
                opacity: 0;
                transition: opacity 0.3s;
            }

            .hover-text:hover .tooltip {
                visibility: visible;
                opacity: 1;
            }
            </style>

            <div class="hover-text">
                Criação de Gráficos
                <div class="tooltip">Nessa sessão do Sistema, você criará os gráficos que estarão no seu relatório.</div>
            </div>
        """, unsafe_allow_html=True)


        col1, col2, col3 = st.columns(3)
        with col1: create_graph(1, df)
        with col2: create_graph(2, df)
        with col3: create_graph(3, df)

        col1, col2, col3 = st.columns(3)
        with col1: create_graph(4, df)
        with col2: create_graph(5, df)
        with col3: create_graph(6, df)

        comentario_geral = st.text_area(f"Considerações sobre o Relatório")

        def add_watermark(pdf, watermark_path, width=700, height=800):
                    """ Adiciona marca d'água semi-transparente em todas as páginas """
                    pdf.saveState()  # Salva estado atual do canvas
                    pdf.drawImage(watermark_path, 0, 0, width=width, height=height, mask="auto")
                    pdf.restoreState()  # Restaura estado após a marca d'água

        if st.button("Gerar Relatório em PDF"):
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)


            # Salvar imagem temporária
   #         watermark_img.save(watermark_img_path)

            # Primeira página
    #        add_watermark(pdf, watermark_img_path)  # Marca d'água na página

            # Adicionar logo no topo
            pdf.drawImage(logo_path, 200, 720, width=170, height=60)

            # Título e Informações
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, 620, f"Relatório de Análise Sobre: {nome_relatorio}")
            pdf.drawString(50, 600, f"Responsável: {nome_responsavel}")
            pdf.drawString(50, 580, f"Setor: {setor}")

            # Indicadores
            y = 500
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, y, "Indicadores:")
            pdf.setFont("Helvetica", 10)
            y -= 20
        
            styles = getSampleStyleSheet()

            for kpi, dados in kpis.items():
                descricao = dados["descricao"]  # Acessa a métrica + variável + valor
                comentario = dados["comentario"]  # Acessa o comentário

                pdf.drawString(50, y, descricao)  # Escreve a descrição do KPI no PDF
                y -= 30  # Ajusta a posição para o comentário

                # Usando Paragraph para formatar o comentário corretamente
                comentario_paragraph = Paragraph(f"Comentário: {comentario}", style=styles["Normal"])
                comentario_paragraph.wrapOn(pdf, 500, 100)  # Define a área para a quebra de linha
                comentario_paragraph.drawOn(pdf, 50, y)  # Adiciona o comentário ao PDF

                y -= 40  # Ajusta a posição para o próximo KPI


            pdf.showPage()  # Nova página para gráficos

            # Adicionar marca d'água na nova página
    #        add_watermark(pdf, watermark_img_path)
            pdf.drawImage(logo_path, 200, 720, width=170, height=60)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, 720, "Gráficos")

            for nome, dados in graficos.items():
                img_path = dados["img_path"]
                comentario = dados["comentario"]
                pdf.drawImage(logo_path, 200, 720, width=170, height=60)

                pdf.drawInlineImage(img_path, 50, 300, width=500, height=400)
                # Usando Paragraph para o comentário do gráfico
                comentario_paragraph = Paragraph(f"Comentário: {comentario}", style=styles["Normal"])
                comentario_paragraph.wrapOn(pdf, 500, 100)  # Ajuste o tamanho da área para o texto
                comentario_paragraph.drawOn(pdf, 50, 280)  # Desenha o comentário no PDF
                pdf.showPage()

       #         add_watermark(pdf, watermark_img_path)

            # Verificar se o comentário geral foi preenchido
            if comentario_geral:
                pdf.showPage()  # Adiciona uma nova página para o comentário geral
    #            add_watermark(pdf, watermark_img_path)  # Marca d'água
                pdf.drawImage(logo_path, 200, 720, width=170, height=60)
                pdf.setFont("Helvetica-Bold", 20)
                pdf.drawString(50, 680, "Considerações Finais")
                
                # Adicionar o comentário geral na nova página
                comentario_paragraph = Paragraph(f"{comentario_geral}", style=styles["Normal"])
                comentario_paragraph.wrapOn(pdf, 500, 100)  # Ajuste o tamanho da área para o texto
                comentario_paragraph.drawOn(pdf, 50, 620)


            pdf.save()
            buffer.seek(0)


            # Botão de download do PDF
            nome_arquivo = f"Relatorio_{nome_relatorio}.pdf".replace(" ", "_")
            st.download_button("📥 Baixar Relatório", buffer, nome_arquivo, "application/pdf")

            # Remover a imagem Zztemporária da marca d'água
            #os.remove(watermark_img_path)

    with tab2:


        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if "Indicador1" in kpis:
                st.metric(label=kpis["Indicador1"]["descricao"], value=kpis["Indicador1"]["valor_kpi"])

        with col2:
            if "Indicador2" in kpis:
                st.metric(label=kpis["Indicador2"]["descricao"], value=kpis["Indicador2"]["valor_kpi"])

        with col3:
            if "Indicador3" in kpis:
                st.metric(label=kpis["Indicador3"]["descricao"], value=kpis["Indicador3"]["valor_kpi"])

        with col4:
            if "Indicador4" in kpis:
                st.metric(label=kpis["Indicador4"]["descricao"], value=kpis["Indicador4"]["valor_kpi"])
        

        # Definir a quantidade de gráficos
        num_graficos = len(graficos)

        # Lógica para definir as colunas e o tamanho dos gráficos de acordo com o número de gráficos
        if num_graficos == 1:
            st.plotly_chart(graficos["Gráfico 1"]["fig"], use_container_width=True, key="grafico_numero_1")

        elif num_graficos == 2:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.plotly_chart(graficos["Gráfico 1"]["fig"], use_container_width=True, key="grafico_numero_1")
            with col2:
                st.plotly_chart(graficos["Gráfico 2"]["fig"], use_container_width=True, key="grafico_numero_2")

        elif num_graficos == 3:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.plotly_chart(graficos["Gráfico 1"]["fig"], use_container_width=True, key="grafico_numero_1")
            with col2:
                st.plotly_chart(graficos["Gráfico 2"]["fig"], use_container_width=True, key="grafico_numero_2")
            with col3:
                st.plotly_chart(graficos["Gráfico 3"]["fig"], use_container_width=True, key="grafico_numero_3")

        elif num_graficos == 4:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.plotly_chart(graficos["Gráfico 1"]["fig"], use_container_width=True, key="grafico_numero_1")
            with col2:
                st.plotly_chart(graficos["Gráfico 2"]["fig"], use_container_width=True, key="grafico_numero_2")
            
            col3, col4 = st.columns([1, 1])
            with col3:
                st.plotly_chart(graficos["Gráfico 3"]["fig"], use_container_width=True, key="grafico_numero_3")
            with col4:
                st.plotly_chart(graficos["Gráfico 4"]["fig"], use_container_width=True, key="grafico_numero_4")

        elif num_graficos == 5:
            col1, col2 = st.columns([1, 1])
            with col1:
                st.plotly_chart(graficos["Gráfico 1"]["fig"], use_container_width=True, key="grafico_numero_1")
            with col2:
                st.plotly_chart(graficos["Gráfico 2"]["fig"], use_container_width=True, key="grafico_numero_2")
            
            col3, col4, col5 = st.columns([1, 1, 1])
            with col3:
                st.plotly_chart(graficos["Gráfico 3"]["fig"], use_container_width=True, key="grafico_numero_3")
            with col4:
                st.plotly_chart(graficos["Gráfico 4"]["fig"], use_container_width=True, key="grafico_numero_4")
            with col5:
                st.plotly_chart(graficos["Gráfico 5"]["fig"], use_container_width=True, key="grafico_numero_5")

        elif num_graficos == 6:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.plotly_chart(graficos["Gráfico 1"]["fig"], use_container_width=True, key="grafico_numero_1")
            with col2:
                st.plotly_chart(graficos["Gráfico 2"]["fig"], use_container_width=True, key="grafico_numero_2")
            with col3:
                st.plotly_chart(graficos["Gráfico 3"]["fig"], use_container_width=True, key="grafico_numero_3")

            col4, col5, col6 = st.columns([1, 1, 1])
            with col4:
                st.plotly_chart(graficos["Gráfico 4"]["fig"], use_container_width=True, key="grafico_numero_4")
            with col5:
                st.plotly_chart(graficos["Gráfico 5"]["fig"], use_container_width=True, key="grafico_numero_5")
            with col6:
                st.plotly_chart(graficos["Gráfico 6"]["fig"], use_container_width=True, key="grafico_numero_6")


    
        if st.button("Gerar Dashboard em PDF"):
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=landscape(letter))
            width, height = landscape(letter)

        #   pdf.drawImage(logo_path, 50, 530,width=150, height=50)
            # Título centralizado no topo
            pdf.drawCentredString(width / 2, height - 50, f"{nome_relatorio}")

   #         add_watermark(pdf, watermark_img_path, 900)  # Marca d'água na página
            pdf.drawImage(logo_path, 50, 530,width=150, height=50)
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawCentredString(width / 2, height - 50, f"{nome_relatorio}")

            # Linha de KPIs
            pdf.setFont("Helvetica-Bold", 12)
            y_kpi = height - 130  # Ajuste fino para os KPIs
            x_kpi = 50
            kpi_width = (width - 100) / 4

            for i, (kpi, dados) in enumerate(kpis.items()):  
                descricao = dados["descricao"]  # Acessa diretamente a descrição desejada
                descricao_cortada = descricao.split(":")[0]  # Pega a parte antes dos dois pontos
                valor = dados["valor_kpi"]  # Supondo que você tenha o valor para exibir
                pdf.drawCentredString(x_kpi + kpi_width / 2, y_kpi + 10, descricao_cortada)  # Desenha a descrição cortada
                pdf.drawCentredString(x_kpi + kpi_width / 2, y_kpi - 10, str(valor))  # Desenha o valor abaixo
                x_kpi += kpi_width  # Ajusta a posição do próximo KPI
            # Ajusta a posição do próximo KPI



            # 🔹 Aumentamos a distância entre KPIs e gráficos 🔹
            y_graph = y_kpi - 200  # Antes estava -250, agora mais abaixo
            x_graph = 50
            graph_width = (width - 150) / 3
            graph_height = 150

            for i, (nome, dados) in enumerate(graficos.items()):
                img_path = dados["img_path"]

                if i % 3 == 0 and i != 0:
                    y_graph -= 200  # Move para a linha de baixo
                    x_graph = 50

                pdf.drawImage(img_path, x_graph, y_graph, width=graph_width, height=graph_height)
                x_graph += graph_width + 25

            # Informações no canto inferior direito
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawRightString(width - 50, 50, f"Responsável: {nome_responsavel}")
            pdf.drawRightString(width - 50, 35, f"Setor: {setor}")

            pdf.save()
            buffer.seek(0)


            nome_arquivo2 = f"Dashboard_{nome_relatorio}.pdf".replace(" ", "_")
            st.download_button("📥 Baixar Dashboard", buffer, nome_arquivo2, "application/pdf")


    with tab3:
        st.dataframe(df)

# if __name__ == "__main__":
# if 'error' not in st.session_state:
#     try:
#         main()
#     except Exception as e:
#         exc_type, exc_value, exc_tb = sys.exc_info()
#         tb = traceback.extract_tb(exc_tb)


#         # Encontra a linha do erro dentro do seu script
#         for frame in reversed(tb):
#             if "dash.py" in frame.filename:  # Substitua pelo nome correto do seu arquivo
#                 error_line = f"Erro na linha {frame.lineno}: {frame.line.strip()} -> {e}"
#                 print(error_line)
#                 aviso_email(dash, error_line )
#                 st.session_state.error = error_line
#                 break
#         else:
#             print(f"Erro: {e}")  # Caso o erro não seja encontrado no seu script principal
        
#         st.rerun()
# else:
#     st.empty()
#     render_header('SISGRAD')
#     erro()
