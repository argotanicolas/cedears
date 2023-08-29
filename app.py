
######################
import plotly.express as px  # pip install plotly-express
from PIL import Image
import yaml
import streamlit_authenticator as stauth  # pip install streamlit-authenticator 
from yaml.loader import SafeLoader
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf

######################
# Page Title
# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
######################
st.set_page_config(page_title="Cedears ", page_icon=":bar_chart:", layout="wide")
#this is the header
 

t1, t2 = st.columns((0.07,1)) 

#t1.age('logo.png', width = 120)
t2.title("Compro & Vendo  - Cedears")
t2.markdown("Nicolas Argota")

         
# --- USER AUTHENTICATION ---

# load hashed passwords
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login("Login", "main")
if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    # ---- READ EXCEL ----
    def calcular_cociente(ultimos_precios):
        primer_valor = ultimos_precios[0]
        otros_valores = ultimos_precios[1:]
        cocientes = [primer_valor / valor for valor in otros_valores]
        return np.round(cocientes, 2)
   
    @st.cache(allow_output_mutation=True)
    def get_data():
        url = "https://iol.invertironline.com/mercado/cotizaciones/argentina/cedears/todos"
        # Realiza la solicitud GET a la página
        response = requests.get(url)
        # Parsea el contenido HTML con BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        # Encuentra todas las filas de la tabla dentro de <tbody>
        rows = soup.find("tbody").find_all("tr")
        # Listas para almacenar los datos
        symbol_list = []
        title_list = []
        price_list = []
        # Itera a través de las filas y extrae los datos
        for row in rows:
            title_value = row.find('i')['title']
            title_list.append(title_value)
            data_symbol_value = row.find('a').get('data-symbol')
            symbol_list.append(data_symbol_value)
            # Encuentra la etiqueta <td> con las condiciones dadas
            td_element = row.find('td', {'class': 'right tar', 'data-field': 'UltimoPrecio'})
            # Obtiene el valor del atributo data-order
            data_order_value = td_element.get('data-order')
            price_list.append(data_order_value)
        # Crea un DataFrame con los datos
        data = {
            "Symbol": symbol_list,
            "Título": title_list,
            "Último precio": price_list
        }
        df = pd.DataFrame(data)
        df['Último precio'] = df['Último precio'].astype(str)
        df['Último precio'] = df['Último precio'].str.replace(',', '.')
        df['Último precio'] = df['Último precio'].astype(float)
        return df

    with st.spinner('Updating Report...'):
         df = get_data()
    st.sidebar.title("Panel de navegación")
    with st.sidebar:
        #selected = option_menu("Menu principal", ["FAVORITOS", "SUPERVISIÓN", "HISTÓRICOS", "PREDICCIÓN"], 
        #icons=["house", 'eye-fill', "card-list", 'robot'], menu_icon="cast", default_index=0)
        selected = option_menu("Menu principal", ["FAVORITOS", "HISTÓRICOS"], 
        icons=["house", 'eye-fill'], menu_icon="cast", default_index=0)
    

    def grupos(df):
     # Reemplazar la coma por un punto y convertir la columna "Último precio" a tipo float
        
       
    # Agrupar por 'Título' y combinar símbolos y últimos precios en una lista
        grouped = df.groupby('Título').agg({'Symbol': list, 'Último precio': list}).reset_index()
    # Renombrar las columnas resultantes
        grouped.columns = ['Título', 'Símbolos', 'Últimos precios']
    # Aplicar la función de cálculo de cociente y agregar la columna 'Cocientes'
        grouped['Cocientes'] = grouped['Últimos precios'].apply(calcular_cociente)
    # Filtrar las filas donde 'Cocientes' no sea una lista vacía
        nuevo_df = grouped[grouped['Cocientes'].apply(lambda x: len(x) > 0)]
    # Convertir las listas en valores numéricos (en este caso, tomamos el primer elemento de cada lista)
        nuevo_df['Cocientes'] = nuevo_df['Cocientes'].apply(lambda x: x[-1] if len(x) > 0 else None)
        return nuevo_df

    def graficas(nuevo_df):

       # col1, col2, col3 = st.columns(3)
       # col1.metric("Temperature", "70 °F", "1.2 °F")
       # col2.metric("Wind", "9 mph", "-8%")
       # col3.metric("Humidity", "86%", "4%")
    # Ordenar el DataFrame por la columna 'Cocientes' de manera descendente y tomar los 10 mejores valores
        top_10_filas = nuevo_df.sort_values(by='Cocientes', ascending=False).head(15)
        top_10_filas.reset_index(drop=True, inplace=True)
        top_10_filas.index += 1
        # Crear una aplicación Streamlit
        st.title('Top CEDEARs en Argentina')
        st.table(top_10_filas)
        # Crear un gráfico de barras para los 10 mejores valores
         # Number of Completed Handovers by Hour
        # Dividir la pantalla en tres columnas
        g1, g2 = st.columns((1, 1))

        # Gráfico de Barras
        with g1:
            st.write("Gráfico de Barras:")
            fig_bar = px.bar(top_10_filas, x='Título', y='Cocientes', title='Top 10 de Cocientes')
            fig_bar.update_xaxes(tickangle=45)
            st.plotly_chart(fig_bar)

        # Gráfico de Pastel
        with g2:
            st.write("Gráfico de Pastel:")
            fig_pie = px.pie(top_10_filas, values='Cocientes', names='Título', title='Top 10 de Cocientes')
            st.plotly_chart(fig_pie)

        # Agrega un tercer gráfico aquí si es necesario

    def supervision():
        st.title("Stocks App")
        symbol = st.text_input("Enter a stock symbol", "AAPL")
        if st.button("Get Quote"):
            st.json(yf.Ticker(symbol).info)


    if selected == "FAVORITOS" :
       # Agregar un widget de entrada de texto para el buscador
        search_term = st.text_input("Buscar por título:")

        # Filtra los datos en función del término de búsqueda
        filtered_data = df[df['Título'].str.contains(search_term, case=False)]

        # Divide la página en dos columnas
        col1, col2 = st.columns(2)

        # Muestra los datos en la columna 1
        with col1:
            st.write("Datos de Cedears en Argentina")
            st.write(filtered_data,width=200)

        # Muestra los resultados de la función de grupos en la columna 2
        with col2:
            st.write("Resultados Agrupados")
            st.write(grupos(filtered_data))
        
    elif selected == "HISTÓRICOS" :
        nuevo_df=grupos(df)
        graficas(nuevo_df)
    elif selected == "SUPERVISIÓN":
        supervision()


  
   