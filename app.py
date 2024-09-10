import streamlit as st
import plotly.express as px
import pandas as pd
import base64

# Função para carregar uma imagem local como base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

image_path = "pngegg.png"  # Certifique-se de que o caminho esteja correto
image_base64 = get_base64_of_bin_file(image_path)

# Carregar o CSV
df_main = pd.read_csv("2004-2021.csv")

# Limpeza e ajustes no DataFrame
df_main.rename(columns={' DATA INICIAL': 'DATA INICIAL'}, inplace=True)
df_main['DATA INICIAL'] = pd.to_datetime(df_main['DATA INICIAL'])
df_main['DATA FINAL'] = pd.to_datetime(df_main['DATA FINAL'])
df_main['DATA MEDIA'] = ((df_main['DATA FINAL'] - df_main['DATA INICIAL']) / 2) + df_main['DATA INICIAL']
df_main = df_main.sort_values(by='DATA MEDIA', ascending=True)
df_main.rename(columns={'DATA MEDIA': 'DATA'}, inplace=True)
df_main.rename(columns={'PREÇO MÉDIO REVENDA': 'VALOR REVENDA (R$/L)'}, inplace=True)
df_main["ANO"] = df_main["DATA"].apply(lambda x: str(x.year))

# Filtrar para gasolina comum e limitar os anos entre 2019 e 2021
df_main = df_main[(df_main['PRODUTO'] == 'GASOLINA COMUM') & (df_main['ANO'].isin(['2019', '2020', '2021']))]

# Excluir colunas não usadas
df_main.drop(['UNIDADE DE MEDIDA', 'COEF DE VARIAÇÃO REVENDA', 'COEF DE VARIAÇÃO DISTRIBUIÇÃO',
              'NÚMERO DE POSTOS PESQUISADOS', 'DATA INICIAL', 'DATA FINAL', 'PREÇO MÁXIMO DISTRIBUIÇÃO', 
              'PREÇO MÍNIMO DISTRIBUIÇÃO', 'DESVIO PADRÃO DISTRIBUIÇÃO', 'MARGEM MÉDIA REVENDA', 
              'PREÇO MÍNIMO REVENDA', 'PREÇO MÁXIMO REVENDA', 'DESVIO PADRÃO REVENDA', 'PRODUTO', 
              'PREÇO MÉDIO DISTRIBUIÇÃO'], inplace=True, axis=1)

# Layout com Streamlit
st.set_page_config(layout="wide")  # Define o layout para tela cheia

# Título principal
st.markdown(
    f"""
    <div style='text-align: center;'>
        <h1> Análise de Preços da Gasolina Comum <img src="data:image/png;base64,{image_base64}" alt="caminhão" width="50" height="50"> </h1>
    </div>
    """, 
    unsafe_allow_html=True
)



# Seção de indicadores no topo
col1, col2, col3 = st.columns(3)

# Substituição dos Máximos e Mínimos por Cards de São Paulo e Rio de Janeiro
with col1:
    st.subheader("Preço - São Paulo")
    df_sao_paulo = df_main[df_main['ESTADO'] == 'SAO PAULO']
    if not df_sao_paulo.empty:
        # Pegar o último valor não nulo disponível para São Paulo
        preco_sp_atual = df_sao_paulo['VALOR REVENDA (R$/L)'].dropna().iloc[-1]  # Pegando o último valor válido
        preco_sp_inicial = df_sao_paulo['VALOR REVENDA (R$/L)'].dropna().iloc[0]  # Pegando o primeiro valor válido
        variacao_sp = (preco_sp_atual - preco_sp_inicial) / preco_sp_inicial * 100
        st.metric(label="São Paulo - Preço Atual", value=f"R${preco_sp_atual:.2f}", delta=f"{variacao_sp:.2f}%")
    else:
        # Se nenhum dado estiver disponível, mostrar uma mensagem adequada
        st.warning("Nenhum dado disponível para São Paulo.")

with col2:
    st.subheader("Preço - Rio de Janeiro")
    df_rio_janeiro = df_main[df_main['ESTADO'] == 'RIO DE JANEIRO']
    if not df_rio_janeiro.empty:
        preco_rj_atual = df_rio_janeiro.iloc[-1]['VALOR REVENDA (R$/L)']
        preco_rj_inicial = df_rio_janeiro.iloc[0]['VALOR REVENDA (R$/L)']
        variacao_rj = (preco_rj_atual - preco_rj_inicial) / preco_rj_inicial * 100
        st.metric(label="Rio de Janeiro - Preço Atual", value=f"R${preco_rj_atual:.2f}", delta=f"{variacao_rj:.2f}%")
    else:
        st.warning("Nenhum dado disponível para Rio de Janeiro.")

with col3:
    # Indicador para um estado selecionado
    st.subheader("Indicadores Gerais")
    estado_selecionado = st.selectbox('Selecione um Estado:', df_main['ESTADO'].unique())
    df_estado = df_main[df_main['ESTADO'] == estado_selecionado]
    valor_atual = df_estado.iloc[-1]['VALOR REVENDA (R$/L)']
    valor_inicial = df_estado.iloc[0]['VALOR REVENDA (R$/L)']
    variacao = (valor_atual - valor_inicial) / valor_inicial * 100

    st.metric(label=f"{estado_selecionado} - Preço Atual", value=f"R${valor_atual:.2f}", delta=f"{variacao:.2f}%")
    
    # Explicação sobre a variação
    with st.expander("Como a variação é calculada?"):
        st.write("""
            A variação percentual é calculada com base na diferença entre o preço atual e o preço inicial do período analisado. 
            A fórmula utilizada é:
            \n
            \[(Preço Atual - Preço Inicial) / Preço Inicial * 100\]
            \n
            Isso fornece a variação percentual do preço da gasolina ao longo do tempo, indicando se o preço subiu ou caiu.
        """)

# Linha com gráficos
st.subheader("Preço por Estado")
estados_selecionados = st.multiselect('Selecione os Estados para Comparação', df_main['ESTADO'].unique(),
                                      default=['RIO DE JANEIRO', 'SAO PAULO'])

if estados_selecionados:
    df_estados = df_main[df_main['ESTADO'].isin(estados_selecionados)]
    fig_comparacao = px.line(df_estados, x='DATA', y='VALOR REVENDA (R$/L)', color='ESTADO',
                             title="Comparação de Preço por Estado")
    st.plotly_chart(fig_comparacao, use_container_width=True)

# Seção inferior com indicadores adicionais
st.subheader("Comparação Direta")
col4, col5 = st.columns(2)

with col4:
    estado_1 = st.selectbox('Estado 1:', df_main['ESTADO'].unique(), key="estado1")
    df_estado_1 = df_main[df_main['ESTADO'] == estado_1]
    st.metric(label=f"Preço Atual ({estado_1})", value=f"R${df_estado_1.iloc[-1]['VALOR REVENDA (R$/L)']:.2f}")

with col5:
    estado_2 = st.selectbox('Estado 2:', df_main['ESTADO'].unique(), key="estado2")
    df_estado_2 = df_main[df_main['ESTADO'] == estado_2]
    st.metric(label=f"Preço Atual ({estado_2})", value=f"R${df_estado_2.iloc[-1]['VALOR REVENDA (R$/L)']:.2f}")
