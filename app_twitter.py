import streamlit as st
import pandas as pd
import json
import datetime

from PIL import Image
import altair as alt

# import nltk
# from nltk.corpus import stopwords
# from stop_words import get_stop_words

st.sidebar.title('Selecciona una opción')
selection = st.sidebar.radio("Go to", ['Análisis individual', 'Comparador'])

st.title('¿Cómo han estado nuestros políticos en Twitter en 2020?')

perfiles = ['sanchezcastejon', 'salvadorilla', 'abalosmeco', 'AranchaGlezLaya',
            'Jccampm', 'carmencalvo_', 'NadiaCalvino', 'Teresaribera',
            'mjmonteroc', 'CelaaIsabel', 'MarotoReyes', 'LuisPlanas',
            'CarolinaDarias', 'jmrdezuribes', 'astro_duque', 'agarzon',
            'joseluisescriva', 
            'PabloIglesias', 'PabloEchenique', 'Yolanda_Diaz_', 'IreneMontero',
            'Adrilastra', 'SimancasRafael',
            'pablocasado_', 'cayetanaAT', 'cucagamarra', 'TeoGarciaEgea',
            'AlmeidaPP_', 'IdiazAyuso', 'JuanMa_Moreno', 'FeijooGalicia',
            'InesArrimadas', 'Tonicanto1',
            'ierrejon', 
            'gabrielrufian']

perfil = st.selectbox('Elige un político', perfiles)

# =============================================================================
# Carga de datos
# =============================================================================
with open(f'dat_20201212/{perfil}_tweets.json','rb') as f:
    data = json.load(f)

# =============================================================================
# Número de tuits
# =============================================================================
aux = []
for date in data.keys():
    date_dt = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
    if date_dt > datetime.datetime(2019, 12, 31):
        aux = aux + [date_dt]
n_tweets = len(aux)
st.markdown(f'{perfil} ha twitteado en 2020: {n_tweets} tweets.')
if n_tweets >= 3170:
    st.markdown(f'<span style="color:red">{perfil} ha twitteado demasiado en 2020 y no tenemos todos sus tweets disponibles...</span>', unsafe_allow_html=True)

# =============================================================================
# WordCloud
# =============================================================================
path_wc = f'wordcloud/wordcloud_{perfil}.png'
wc = Image.open(path_wc)
st.image(wc, use_column_width=True) # caption='Sunrise by the mountains',
    
# =============================================================================
# A quién menciona más?
# =============================================================================
st.markdown(f'Cuentas de Twitter más mencionados por {perfil}')

text = []
for tweet in data.values():
    text = text + [tweet['user_mentions']]

flat_list = [item for sublist in text for item in sublist]  
flat_list = [mention for mention in flat_list if mention != perfil]
mentions = pd.DataFrame(flat_list, columns = ['menciones'])['menciones'].value_counts().iloc[:10]
mentions = mentions.reset_index()
mentions = mentions.rename(columns = {'index': 'perfil'})

# st.write(mentions)

bars = alt.Chart(mentions).mark_bar().encode(
    x='menciones:Q',
    y=alt.Y('perfil:O', sort = '-x'))

text = bars.mark_text(align='left', baseline='middle',
    dx=3  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(text='menciones:Q')

plot = alt.layer(bars, text).configure_view(
    stroke='transparent').configure_axis(
        domainWidth=0.8,
        ticks = False,
        labelFontSize = 13,
        titleFontSize = 15)
    
st.altair_chart(plot, use_container_width = True)

# =============================================================================
# Hashtags más usados
# =============================================================================
st.markdown(f'Hashtags más utilizados por {perfil}')

text = []
for tweet in data.values():
    text = text + [tweet['hashtags']]

flat_list = [item for sublist in text for item in sublist]  
hashtags = pd.DataFrame(flat_list, columns = ['menciones'])['menciones'].value_counts().iloc[:10]
hashtags = hashtags.reset_index()
hashtags = hashtags.rename(columns = {'index': 'hashtags'})

# st.write(hashtags)

bars = alt.Chart(hashtags).mark_bar().encode(
    x='menciones:Q',
    y=alt.Y('hashtags:O', sort = '-x'))

text = bars.mark_text(align = 'left', baseline = 'middle',
    dx = 2  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(text='menciones:Q')

plot = alt.layer(bars, text).configure_view(
    stroke='transparent').configure_axis(
        domainWidth=0.8,
        ticks = False,
        labelFontSize = 13,
        titleFontSize = 15)
    
st.altair_chart(plot, use_container_width = True)


About1 = st.sidebar.markdown('## 🤝 Sobre nosotros')

# About = st.sidebar.info('Somos dos amigos graduados en matemáticas por la Universidad de Cádiz. Posteriormente obtuvimos el Máster en Data Science & Big Data en Afi Escuela de Finanzas.')

Contact = st.sidebar.markdown('## 📩 ¡Encuéntranos en LinkedIn!')

Contact1 = st.sidebar.info('[José Ramón Sánchez Leo](https://es.linkedin.com/in/jos%C3%A9-ram%C3%B3n-s%C3%A1nchez-leo) Data Scientist en [Afi](https://www.afi.es/).')