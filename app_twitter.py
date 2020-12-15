import streamlit as st
import pandas as pd
import json
import re
import datetime

from PIL import Image
import altair as alt

# import nltk
# from nltk.corpus import stopwords
# from stop_words import get_stop_words

st.sidebar.title('Selecciona una opción')
selection = st.sidebar.radio("Go to", ['Análisis individual', 'Comparador'])

st.title('¿Cómo han estado nuestros políticos en Twitter en 2020?')

# Cargamos json políticos
with open(r"data_politicos.json", "r", encoding = 'utf-8') as read_file:
    data = json.load(read_file)
data = dict((key,d[key]) for d in data for key in d)

perfiles = []
for key in data.keys():    
    perfiles = perfiles + [f"{key} ({data[key]['partido']})"]
perfiles.sort()
perfil = st.selectbox('Elige un político', perfiles)
real_name = re.sub(' \(.*\)', '', perfil)
perfil = data[real_name]['twitter_name']
cargo = data[real_name]['cargo']

# =============================================================================
# Carga de datos
# =============================================================================
with open(f'dat_20201212/{perfil}_tweets.json','rb') as f:
    data = json.load(f)

# =============================================================================
# Imagen, Nombre, Partido y bio
# =============================================================================
col1, col2 = st.beta_columns([1, 2])

# col1.header("Foto de perfil")
img_profile = Image.open(f'img_profile/{perfil}.jpg')
col1.image(img_profile, use_column_width=True)

col2.header(real_name)
# Load bios profiles
with open(r"data_bios.json", "r", encoding = 'utf-8') as read_file:
    data_bios = json.load(read_file)
col2.markdown(f"**{cargo}**")
col2.markdown(data_bios[perfil])

html_string = "<hr>"

st.markdown(html_string, unsafe_allow_html=True)

# =============================================================================
# Número de tuits
# TODO: filtrar offline no online
# =============================================================================
aux = []
for date in data.keys():
    date_dt = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
    if date_dt > datetime.datetime(2019, 12, 31):
        aux = aux + [date_dt]
n_tweets = len(aux)
col2.markdown(f'{real_name} ha publicado {n_tweets} tuits en 2020.')
if n_tweets >= 3170:
    col2.markdown(f'<span style="color:red">{real_name} ha publicado demasiados tuits en 2020 y no tenemos todos sus tuits disponibles, estamos trabajando en ello.</span>', unsafe_allow_html=True)

# =============================================================================
# WordCloud
# =============================================================================
html_string_wc = f"<h3>WordCloud de {real_name}</h3>"
st.markdown(html_string_wc, unsafe_allow_html=True)

path_wc = f'wordcloud/wordcloud_{perfil}.png'
wc = Image.open(path_wc)
st.image(wc, use_column_width=True) # caption='Sunrise by the mountains',
    
# =============================================================================
# A quién menciona más?
# =============================================================================
html_string_m = f"<h3>Cuentas de Twitter más mencionados por {real_name}</h3>"
st.markdown(html_string_m, unsafe_allow_html=True)

text = []
for tweet in data.values():
    text = text + [tweet['user_mentions']]

flat_list = [item for sublist in text for item in sublist]  
flat_list = [mention for mention in flat_list if mention != perfil]
mentions = pd.DataFrame(flat_list, columns = ['menciones'])['menciones'].value_counts().iloc[:10]
mentions = mentions.reset_index()
mentions = mentions.rename(columns = {'index': 'perfil'})

# st.write(mentions)

bars = alt.Chart(mentions).mark_bar(color = '#d84510').encode(
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
html_string_h = f"<h3>Hashtags más utilizados por {real_name}</h3>"
st.markdown(html_string_h, unsafe_allow_html=True)

text = []
for tweet in data.values():
    text = text + [tweet['hashtags']]

flat_list = [item for sublist in text for item in sublist]  
hashtags = pd.DataFrame(flat_list, columns = ['menciones'])['menciones'].value_counts().iloc[:10]
hashtags = hashtags.reset_index()
hashtags = hashtags.rename(columns = {'index': 'hashtags'})

# st.write(hashtags)

bars = alt.Chart(hashtags).mark_bar(color = '#d84510').encode(
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

Contact1 = st.sidebar.info('[Ramón Sánchez Leo](https://es.linkedin.com/in/jos%C3%A9-ram%C3%B3n-s%C3%A1nchez-leo) \n Data Scientist en [Afi](https://www.afi.es/).')


@st.cache(allow_output_mutation=True)
def Pageviews():
    return []

pageviews=Pageviews()
pageviews.append('dummy')

try:
    st.sidebar.markdown('Visitas a la app {}.'.format(len(pageviews)))
except ValueError:
    st.sidebar.markdown('Visitas a la app {}.'.format(1))
