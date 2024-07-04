import pandas as pd
import plotly_express as px
import streamlit as st
from PIL import Image
import os
from fpdf import FPDF
import folium
from streamlit_folium import folium_static 
from streamlit_extras.metric_cards import style_metric_cards

# Configurando o tamanho da página após a autenticação
st.set_page_config(layout="wide", initial_sidebar_state="auto")


# CRIANDO A TELA DE (login e senha)
def authenticate_user():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        with st.form(key='login_form'):
            col1, col2, col3 = st.columns([1, 2, 1])  # Colunas para centralizar o formulário
            with col2:
                st.markdown(
                    "<style>.login-title { color: #333; font-size: 24px; text-align: center; }</style>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    "<p class='login-title'>Tela de Login</p>",
                    unsafe_allow_html=True
                )

                user = st.text_input(label="Usuário:", value="", key="user")
                passwd = st.text_input(label="Senha:", value="", key="passwd", type="password")
                submitted = st.form_submit_button("Login")

                if submitted:
                    if user.strip() == "admin" and passwd.strip() == "admin":
                        st.session_state["authenticated"] = True
                        return True  # Retorna True após autenticar com sucesso

                    st.error("Usuário ou senha incorretos")
                    return False  # Retorna False se o login falhar

    else:
        return True  # Retorna True se já estiver autenticado


if authenticate_user():

    # Imagem cabeçalho da página
    imagem = Image.open("loja.png")
    st.image(imagem, use_column_width=True, caption="O MELHOR AÇAÍ DO BRASIL")

    # Abrindo o dataframe com o pandas
    df = pd.read_csv("vendas.csv", encoding="LATIN-1")

    # Convertendo a data para datetime
    df["data"] = pd.to_datetime(df["data"])

    # Criando a varável data_inicio
    data_inicio = pd.to_datetime(df["data"]).min()

    # Criando a varável data_fim
    data_fim = pd.to_datetime(df["data"]).max()

    # 4 - CRIANDO OS BOTÕES DE SELEÇÃO
    with st.sidebar:

        # Imagem da logo sidebar
        logo = Image.open("acai.png")
        st.image(logo, use_column_width=True, caption="Loja de Açai")
        st.subheader("", divider="rainbow")
        # Criando o botão de seleção [tamanho]

        # Selectbox Tamanho do copo
        st.info("Açaí", icon="🥤")
        opcao1 = ["Selecione o tamanho"] + list(df["tamanho"].unique())
        bt_tamanho = st.selectbox(label="Tamanho do copo", options=opcao1)
        st.subheader("", divider="rainbow")

        # Criando os botões de seleção do início e final da data
        st.info("Data da venda", icon="📆")
        st.write("Vendas entre: (2020-01-01) á (2022-12-31)")
        bt_data1 = pd.to_datetime(st.date_input("Início:", data_inicio))
        bt_data2 = pd.to_datetime(st.date_input("Fim:", data_fim))
        st.subheader("", divider="rainbow")

        # Criando o botão de seleção [estado]
        st.info("Cidades", icon="🏙️")
        opcao3 = ["Selecione o estado"] + list(df["cidade"].unique())
        bt_cidade = st.radio(label="Localização das lojas:", options=opcao3, horizontal=True)

    # 5 - CRIAÇÃO DOS FILTROS

    df_filtro = df.loc[(df["tamanho"] == bt_tamanho) & (df["data"].between(bt_data1, bt_data2))]
    df_data = df.loc[(df["tamanho"] == bt_tamanho) & (df["data"].between(bt_data1, bt_data2)) & (df["cidade"] == bt_cidade)]

    # Filtro ao clickar no estado gerar a localização no mapa
    df_local = df[df['cidade'] == bt_cidade][['latitude', 'longitude', 'cidade']]

    # 6 - CRIANDO AS COLUNAS

    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)
    col6, col7 = st.columns(2)
    col8, col9 = st.columns(2)
    col10, col11 = st.columns(2)
    
    # 7 - PALETAS DE CORES
    
    color1 = ["#a4ff2b", "#ea1c02", "#82143f", "#17c105", "#f839ac", "#161570"]
    color2 = ["#FD5A68", "#72B2E4", "#D06814", "#008996"]
    color3 = ["#FD5A68", "#008996"]
    
    

    # 8 - CRIANDO OS GRÁFICOS

    # (1) Card faturamento
    
    def faturamento():
        
        faturamento = df_data["preco"].sum()
        
        col1.info("Faturamento R$", icon="💲")
        col1.metric(label="Total R$", value=f"{faturamento:,.2f}")
        style_metric_cards(background_color="#47c339", border_left_color="#FF0000")
    
    faturamento()

    # (2) Card média
    
    def media():
        
        media = df_data["preco"].mean()
        
        col2.info("Média das vendas R$", icon='🔢')
        col2.metric(label="Total R$", value=f"{media:,.2f}")
    
    media()

    # (3) Card total pedidos
    
    def pedidos():
        
        pedido = df_data["pedido"].count()
        col3.info("Quantidade de vendas", icon="🛒")
        col3.metric(label="Total", value=f"{pedido:,.0f}")
    
    pedidos()

    # (4) Gráfico de linha (Quantidade de produtos vendidos por cidade)
    
    def produtos_vendidos():
        
        col4.info("Quantidade de produtos vendido por cidade", icon="〰️")
        produtos_vendidos = df_filtro.groupby("cidade")[["pedido"]].count().reset_index()
        fig_line = px.line(produtos_vendidos,
                           x="cidade",
                           y="pedido",
                           text="cidade",
                           line_shape="spline",
                           markers=True)

        fig_line.update_traces(textposition="bottom right", line=dict(color="#ea1c02", width=2, dash="dash"))
        fig_line.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgray",
                              showline=True, linewidth=0.5, linecolor="lightgray")
        fig_line.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgray",
                              showline=True, linewidth=0.5, linecolor="lightgray")
        col4.plotly_chart(fig_line, use_container_width=True)
    
    produtos_vendidos()

    # (5) Gráfico de barras (Total de vendas por cidade R$)
   
    def total_vendas():
        
        col5.info("Total de vendas por cidade R$", icon="📊")
        vendas_cidades = df_filtro.groupby("cidade")[["preco"]].sum().reset_index()
        fig_prc = px.bar(vendas_cidades,
                         x="cidade",
                         y="preco",
                         color="cidade",
                         text_auto=True,
                         color_discrete_sequence=color1)

        fig_prc.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgray",
                             showline=True, linewidth=0.5, linecolor="lightgray")
        fig_prc.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgray",
                             showline=True, linewidth=0.5, linecolor="lightgray")
        col5.plotly_chart(fig_prc, use_container_width=True)
    
    total_vendas()

    # (6) Gráfico de barras (Forma de pagamento)
    def forma_pagamento():
    
        col6.info("Forma de pagamento", icon="📊")
        pg = df_data.groupby("pagamento")[["preco"]].sum().reset_index()
        fig_pagamento = px.bar(pg,
                               x="preco",
                               y="pagamento",
                               orientation="h",
                               color="pagamento",
                               text_auto='.2s',
                               color_discrete_sequence=color2)

        fig_pagamento.update_xaxes(showline=True, linewidth=0.5, linecolor="lightgray")
        fig_pagamento.update_yaxes(showline=True, linewidth=0.5, linecolor="lightgray")

        col6.plotly_chart(fig_pagamento, use_container_width=True)
    
    forma_pagamento()

    # (7) Gráfico de pizza (Quantidade de pedidos por forma de pagamento)
    
    def quantidade_pedidos():
        
        col7.info("Quantidade de pedidos por forma de pagamento", icon="🍕")
        prc = df_data.groupby("pagamento")[["pedido"]].count().reset_index()
        fig_qtde = px.pie(prc, values="pedido",
                          names="pagamento",
                          hole=.5,
                          color_discrete_sequence=color2)
        fig_qtde.update_traces(textinfo="label+value+percent",
                               pull=[0.1, 0.1, 0.1, 0]) 
        
        col7.plotly_chart(fig_qtde, use_container_width=True)
    
    quantidade_pedidos()

    # (8) Gráfico de pizza (Tipo de consumo)
    
    def tipo_consumo():
        
        col8.info("Tipo de consumo", icon="🍕")
        prc = df_data.groupby("consumo")[["preco"]].sum().reset_index()
        fig_consumo = px.pie(prc, values="preco",
                             names="consumo",
                             hole=.5,
                             color_discrete_sequence=color3)
        fig_consumo.update_traces(textinfo="label+value+percent",
                                  pull=[0.1, 0]) 
        
        col8.plotly_chart(fig_consumo, use_container_width=True)
    
    tipo_consumo()

   
    # (9) Relatório de vendas
    with col9:
        
        # Configurando os botões de seleção das colunas do Dataframe
        st.sidebar.header("", divider="rainbow")
        st.info("Relatório de vendas", icon="📋")
        st.sidebar.info("Tabela de vendas", icon="📅")
        tabela = st.sidebar.multiselect("Selecione as colunas:", df_data.columns.to_list(), default=[])

        if tabela:  # Verifica se a lista de colunas não está vazia
            # Filtra o DataFrame para exibir apenas as colunas selecionadas
            df_display = df_data[tabela].sort_values(by=tabela)
            if not df_display.empty:
                st.write(df_display)

                # Botão para exportar o DataFrame para um arquivo .csv
                if st.button('Exportar como CSV'):
                    filename = "Dataframe.csv"

                    # Seu DataFrame
                    data = df_display
                    df_display = pd.DataFrame(data)

                    # Obtendo o caminho para a pasta de downloads do usuário
                    path_csv = os.path.join(os.path.expanduser("~"), "Downloads", filename)

                    # Salvando o DataFrame como um arquivo CSV na pasta de downloads
                    df_display.to_csv(path_csv, index=False, sep=';')
                    st.success(f'DataFrame exportado com sucesso como {path_csv}')

                # Botão para exportar o DataFrame para um arquivo .xlsx
                if st.button('Exportar como Excel'):
                    filename = "Dataframe.xlsx"

                    # Seu DataFrame
                    data = df_display
                    df_display = pd.DataFrame(data)

                    # Obtendo o caminho para a pasta de downloads do usuário
                    path_xlsx = os.path.join(os.path.expanduser("~"), "Downloads", filename)

                    # Salvando o DataFrame para um arquivo Excel (.xlsx)
                    df_display.to_excel(path_xlsx, index=False)
                    st.success(f'DataFrame exportado com sucesso como {path_xlsx}')


                # Função para gerar o PDF
                def generate_pdf(dataframe):
                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=1, margin=10)
                    pdf.add_page()
                    pdf.set_font("Arial", "B", size=12)
                    pdf.cell(200, 10, "Relatório de Análise Quy Açaí", ln=True, align="C")

                    col_names = dataframe.columns.values.tolist()
                    data = dataframe.values.tolist()

                    # Imprimir os cabeçalhos das colunas
                    pdf.set_font("Arial", "B", size=10)
                    for col_name in col_names:
                        pdf.cell(30, 8, col_name, border=1, align='C')
                    pdf.ln()

                    # Imprimir os dados do DataFrame
                    pdf.set_font("Arial", size=8)
                    for row in data:
                        for item in row:
                            pdf.cell(30, 8, str(item), border=1)
                        pdf.ln()

                    return pdf


                if st.button('Exportar como PDF', key='pdf'):
                    pdf_filename = "Dataframe.pdf"
                    # Gera o PDF
                    pdf = generate_pdf(df_display)

                    # Obtendo o caminho para a pasta de downloads do usuário
                    path_pdf = os.path.join(os.path.expanduser("~"), "Downloads", pdf_filename)

                    # Salvando o PDF na pasta de downloads
                    pdf.output(path_pdf)
                    st.success(f'DataFrame exportado com sucesso como {path_pdf}')
                    
                    
    # (10) Mapa de localização das lojas
    with col10:
        
        st.info('Localização das lojas', icon='🗺️')
                
    # Verificando se as coordenadas são encontradas
    if not df_local.empty:
        # Criando um mapa com base nas coordenadas da cidade selecionada
        m = folium.Map(location=[df_local['latitude'].iloc[0], df_local['longitude'].iloc[0]], 
                       zoom_start=12, 
                       width='100%' , 
                       height='100%',
                       )
        
        # Definir o ícone personalizado com a cor desejada
        angle = 180
        icon = folium.Icon(angle=angle, color='green', icon='arrow-up')
        
        # Adicionando um marcador com a localização da cidade selecionada
        folium.Marker(
            [df_local['latitude'].iloc[0], df_local['longitude'].iloc[0]],
             popup='localização',
             tooltip='localização',
             icon=icon
        ).add_to(m)

        # Exibindo o mapa no Streamlit
        folium_static(m)
    else:
         st.warning("O destino ainda não foi selecionado.")
                    

    # Rodapé
    st.subheader("", divider="green")
    st.markdown("<p style='text-align: center;'><b>Desenvolvido por: Tulio Meireles</b></p>", unsafe_allow_html=True)
