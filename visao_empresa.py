# bibliotecas:
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import pandas as pd
import streamlit as st
# python -m pip install streamlit-folium
import folium
from streamlit_folium import st_folium
#from streamlit_folium import folium_static

# ==================================
# Funções
# ==================================

df = pd.read_csv (r'dataset/train.csv')
df1 = df.copy()

def clean_code(df1):

    #Selecionando apenas linhas filtradas em um campo específico e salvando como cópia retirando "NaN "
    linhas_selecionadas = df1['Road_traffic_density'] !='NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = df1['Delivery_person_Age'] !='NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = df1['City'] !='NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = df1['Festival'] !='NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = df1['Order_Date'] !='NaN'
    df1 = df1.loc[linhas_selecionadas,:].copy()

    #Convertendo dados tipo número inteiro
    df1 ['Delivery_person_Age'] = df1 ['Delivery_person_Age'].astype (int)

    #Convertendo dados tipo número decimal
    df1 ['Delivery_person_Ratings'] = df1 ['Delivery_person_Ratings'].astype (float)

    #Convertendo dados tipo texto em data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'],format='%d-%m-%Y')

    #Selecionando apenas linhas filtradas em um campo específico e salvando como cópia retirando "NaN " e convertando para inteiro
    linhas_selecionadas = df1['multiple_deliveries'] !='NaN '
    df1 = df1.loc[linhas_selecionadas,:].copy()
    df1 ['multiple_deliveries'] = df1 ['multiple_deliveries'].astype (int)

    #transforma em string e retira todas os espaços após a string.
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # Limpeza da coluna de tempo
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype (int)

    return df1

# ------------------------ Início da estrutura lógica do código ------------------------

# Import dataset
df = pd.read_csv('dataset/train.csv')

# Limpar código
df1 = clean_code(df)

# ==================================
# Barra lateral no Streamlit
# ==================================

st.header('Tabela de Pedidos')


from datetime import datetime
from PIL import Image

#image_path = 'C:/repos/ftc_programacao_python/imagem.jpg'
imagem = Image.open('imagem.jpg')

st.image(imagem, width = 120)

date_slider = st.sidebar.slider(
    'Selecione o período',
    value = datetime(2022,4,13),
    min_value = datetime(2022,2,11),
    max_value = datetime(2022,4,6),
    format = 'DD-MM-YYYY'
)

traffic_op = st.sidebar.multiselect(
    'Condição de trânsito',
    ['Low', 'Medium', 'High','Jam'],
    default='Low'
)
st.sidebar.markdown("""--------""")

st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]


# Filtro de Data
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_op)
df1 = df1.loc[linhas_selecionadas,:]


st.header(date_slider)
st.dataframe(df1)
print('Página atualizada')

#==========================
# Layout no Streamlit
#==========================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():

        st.markdown('# Orders by Day')

        # Visão - Empresa
        cols = ['ID','Order_Date']
        df1_graf1 = df1.loc[:,cols].groupby(['Order_Date']).count().reset_index()
        # gráfico de barras
        fig1= px.bar(df1_graf1 , x='Order_Date', y='ID')
        st.plotly_chart(fig1,use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Trafic Order Share')
            df_aux = df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density']!= 'NaN',:]
            df_aux['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()
            fig2 = px.pie(df_aux, values ='entregas_perc', names = 'Road_traffic_density')
            st.plotly_chart(fig2,use_container_width=True)

        with col2:
            st.header('Trafic Order City')
            cols = (['ID','City','Road_traffic_density'])
            agrupamento = (['City','Road_traffic_density'])
            df_aux = df1.loc[:,cols].groupby(agrupamento).count().reset_index()
            df_aux = df_aux.loc[df_aux['City']!= 'NaN',:]
            df_aux = df_aux.loc[df_aux['Road_traffic_density']!= 'NaN',:]
            fig3= px.scatter(df_aux, x='City', y = 'Road_traffic_density', size='ID', color = 'City')
            st.plotly_chart(fig3,use_container_width=True)


with tab2:
    with st.container():
        st.markdown('# Order by Week')
        # Converte em semana do ano (1 a 52) sendo início domingo (U) ou segunda (W)
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        df1.head()

        cols = ['ID', 'week_of_year']
        df1_graf2 = df1.loc[:,cols].groupby('week_of_year').count().reset_index()
        fig4 = px.line(df1_graf2, x= 'week_of_year', y = 'ID')
        st.plotly_chart(fig4,use_container_width=True)

    with st.container():
        st.markdown('# Order Share by Week')
        # Qt. de entregas na semana / número únicode entregadores por semana
        df_aux01= df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02= df1.loc[:,['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
        df_aux = pd.merge(df_aux01, df_aux02,how = 'inner' )
        df_aux [ 'order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
        fig5 = px.line(df_aux, x='week_of_year', y = 'order_by_deliver')
        st.plotly_chart(fig5,use_container_width=True)


with tab3:

    st.markdown('# Country Maps')

    cols= (['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude' ])
    df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City']!= 'NaN',:]
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!= 'NaN',:]
    df_aux

    map = folium.Map()

    for index,location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude' ]],
        popup=location_info[['City','Road_traffic_density']]).add_to(map)
        
    st_folium(map, width=1024, height=600)
