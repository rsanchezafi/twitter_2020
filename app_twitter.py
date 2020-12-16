import streamlit as st
import pandas as pd
import json
import re
import datetime
import locale

from PIL import Image
import altair as alt

import random    
import pyecharts.options as opts
from pyecharts.charts import Calendar
from streamlit_echarts import st_pyecharts

# =============================================================================
# Cargamos json políticos
# =============================================================================
with open(r"data_politicos.json", "r", encoding = 'utf-8') as read_file:
    data_politicos = json.load(read_file)
data_politicos = dict((key,d[key]) for d in data_politicos for key in d)

perfiles = []
for key in data_politicos.keys():    
    perfiles = perfiles + [f"{key} ({data_politicos[key]['partido']})"]
perfiles.sort()

# Load bios profiles
with open(r"data_bios.json", "r", encoding = 'utf-8') as read_file:
    data_bios = json.load(read_file)

# =============================================================================
# Cabeceras
# =============================================================================
# html_string_s = f"<h3>Elige un político</h3>"
# st.sidebar.markdown(html_string_s, unsafe_allow_html=True)

# st.title('Política española en Twitter en 2020')
image = Image.open('logo.png')
st.sidebar.image(image)
# st.sidebar.title('Política española en Twitter en 2020')
selection = st.sidebar.radio("Selecciona una opción", ['Análisis individual', 'Comparador'])

# =============================================================================
# Análisis individual
# =============================================================================
if selection == 'Análisis individual':
    st.markdown("<h1 style='text-align: center; color: #d84519;'>Política española en Twitter durante 2020</h1>", unsafe_allow_html=True)
    perfil = st.selectbox('Elige un político', perfiles)
    
    # =============================================================================
    # Variables globales
    # =============================================================================
    real_name = re.sub(' \(.*\)', '', perfil)
    perfil = data_politicos[real_name]['twitter_name']
    cargo = data_politicos[real_name]['cargo']
    
    # =============================================================================
    # Carga de datos
    # =============================================================================
    with open(f'dat_20201212/{perfil}_tweets.json','rb') as f:
        data = json.load(f)
    
    # Nos quedamos solo con la información de 2020
    aux = []
    for date in data.keys():
        date_dt = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
        if not date_dt > datetime.datetime(2019, 12, 31):
            aux = aux + [date]
    
    for date in aux:
        del data[date]
    
    # =============================================================================
    # Imagen, Nombre, Partido y bio
    # =============================================================================
    col1, col2 = st.beta_columns([1, 2])
    
    # col1.header("Foto de perfil")
    img_profile = Image.open(f'img_profile/{perfil}.jpg')
    col1.image(img_profile, use_column_width=True)
    
    col2.header(real_name)
    col2.markdown(f"**{cargo}**")
    col2.markdown(data_bios[perfil])
    
    # =============================================================================
    # Número de tuits
    # TODO: filtrar offline no online
    # =============================================================================
    n_tweets = len(data.keys())
    col2.markdown(f"{real_name} ha publicado {format(n_tweets,',d').replace(',','.')} tuits en 2020.")
    if n_tweets >= 3170:
        st.markdown(f'''<span style="color:red">{real_name} ha publicado demasiados tuits en 2020 y no tenemos todos sus tuits disponibles, estamos trabajando en ello. Disculpa las molestias</span>''', unsafe_allow_html=True)
    
    
    html_string = "<hr>"
    st.markdown(html_string, unsafe_allow_html=True)
    
    # =============================================================================
    # WordCloud
    # =============================================================================
    st.markdown(f"<h3 style='color: #d84519;'>WordCloud de {real_name}</h3>", unsafe_allow_html=True)
    
    path_wc = f'wordcloud/wordcloud_{perfil}.png'
    wc = Image.open(path_wc)
    st.image(wc, use_column_width=True) # caption='Sunrise by the mountains',
        
    # =============================================================================
    # A quién menciona más?
    # =============================================================================
    st.markdown(f"<h3 style='color: #d84519;'>Cuentas de Twitter más mencionados por {real_name}</h3>", unsafe_allow_html=True)
    
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
    st.markdown(f"<h3 style='color: #d84519;'>Hashtags más utilizados por {real_name}</h3>", unsafe_allow_html=True)
    
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
    
    # =============================================================================
    # Calendario publicaciones
    # =============================================================================
    begin = datetime.date(2020, 1, 1)
    end = datetime.date(2020, 12, 31)

    dates = []
    for date in data.keys():
        date = date[:10]
        dates = dates + [date]
    dates = pd.DataFrame(dates, columns = ['dates']).value_counts()
    dates = pd.DataFrame(dates, columns = ['n']).reset_index()
    data_dates = []
    for _, row in dates.iterrows():
        data_dates = data_dates + [(row['dates'], row['n'])]
    
    # data_dates = [[str(begin + datetime.timedelta(days=i)), random.randint(1000, 25000)]
    #         for i in range((end - begin).days + 1)]
    
    c = (
        Calendar(init_opts=opts.InitOpts(width="1000px", height="300px"))
        .add(
            series_name="",
            yaxis_data=data_dates,
            calendar_opts=opts.CalendarOpts(
                pos_top="120",
                pos_left="30",
                pos_right="30",
                range_="2020",
                yearlabel_opts=opts.CalendarYearLabelOpts(is_show=False),
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(pos_top="30", pos_left="center", title=f"Número de tuits por día de {real_name}"),
            visualmap_opts=opts.VisualMapOpts(
                max_=25, min_=0, orient="horizontal", is_piecewise=False
            ),
        )
    )
    st_pyecharts(c)

# =============================================================================
# Comparador
# =============================================================================
if selection == 'Comparador':
    perfil_1 = st.sidebar.selectbox('Elige un político', perfiles)
    perfil_2 = st.sidebar.selectbox('Elige un político', [p for p in perfiles if p != perfil_1])
    st.markdown("<h1 style='text-align: center; color: #d84519;'>Política española en Twitter durante 2020</h1>", unsafe_allow_html=True)
    
    # =============================================================================
    # Variables globales
    # =============================================================================
    real_name_1 = re.sub(' \(.*\)', '', perfil_1)
    perfil_1 = data_politicos[real_name_1]['twitter_name']
    cargo_1 = data_politicos[real_name_1]['cargo']
    
    real_name_2 = re.sub(' \(.*\)', '', perfil_2)
    perfil_2 = data_politicos[real_name_2]['twitter_name']
    cargo_2 = data_politicos[real_name_2]['cargo']
    
    # =============================================================================
    # Carga de datos
    # =============================================================================
    with open(f'dat_20201212/{perfil_1}_tweets.json','rb') as f:
        data_1 = json.load(f)
    
    with open(f'dat_20201212/{perfil_2}_tweets.json','rb') as f:
        data_2 = json.load(f)
    
    # Nos quedamos solo con la información de 2020
    for data in [data_1, data_2]:
        aux = []
        for date in data.keys():
            date_dt = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
            if not date_dt > datetime.datetime(2019, 12, 31):
                aux = aux + [date]
        
        for date in aux:
            del data[date]
    
    # =============================================================================
    # Imagen, Nombre, Partido y bio
    # =============================================================================
    col1, col2 = st.beta_columns([1, 1])
    
    col1.header(real_name_1)
    img_profile_1 = Image.open(f'img_profile/{perfil_1}.jpg')
    col1.image(img_profile_1, use_column_width=True)
    
    col2.header(real_name_2)
    img_profile_2 = Image.open(f'img_profile/{perfil_2}.jpg')
    col2.image(img_profile_2, use_column_width=True)
    
    col1.markdown(f"**{cargo_1}**")
    col1.markdown(data_bios[perfil_1])
    col2.markdown(f"**{cargo_2}**")
    col2.markdown(data_bios[perfil_2])
    
    # # =============================================================================
    # # Número de tuits
    # # TODO: filtrar offline no online
    # # =============================================================================
    # aux = []
    # for date in data_1.keys():
    #     date_dt = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
    #     if date_dt > datetime.datetime(2019, 12, 31):
    #         aux = aux + [date_dt]
    # n_tweets_1 = len(aux)
    
    # for date in data_2.keys():
    #     date_dt = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
    #     if date_dt > datetime.datetime(2019, 12, 31):
    #         aux = aux + [date_dt]
    # n_tweets_2 = len(aux)
    
    # col1.markdown(f"{real_name_1} ha publicado {format(n_tweets_1,',d').replace(',','.')} tuits en 2020.")
    # col2.markdown(f"{real_name_2} ha publicado {format(n_tweets_2,',d').replace(',','.')} tuits en 2020.")
    
    # if n_tweets_1 >= 3170:
    #     col1.markdown(f'''<span style="color:red">{real_name_1} ha publicado demasiados tuits en 2020 y no tenemos todos sus tuits disponibles, estamos trabajando en ello. Disculpa las molestias</span>''', unsafe_allow_html=True)
    # if n_tweets_2 >= 3170:
    #     col2.markdown(f'''<span style="color:red">{real_name_2} ha publicado demasiados tuits en 2020 y no tenemos todos sus tuits disponibles, estamos trabajando en ello. Disculpa las molestias</span>''', unsafe_allow_html=True)
    
    # html_string = "<hr>"
    # st.markdown(html_string, unsafe_allow_html=True)
    
    # =============================================================================
    # WordCloud
    # =============================================================================
    col1.markdown(f"<h3 style='color: #d84519;'>WordCloud de {real_name_1}</h3>", unsafe_allow_html=True)
    col2.markdown(f"<h3 style='color: #d84519;'>WordCloud de {real_name_2}</h3>", unsafe_allow_html=True)
    
    path_wc_1 = f'wordcloud/wordcloud_{perfil_1}.png'
    wc_1 = Image.open(path_wc_1)
    col1.image(wc_1, use_column_width=True)
    
    path_wc_2 = f'wordcloud/wordcloud_{perfil_2}.png'
    wc_2 = Image.open(path_wc_2)
    col2.image(wc_2, use_column_width=True)
        
    # # =============================================================================
    # # A quién menciona más?
    # # =============================================================================
    # st.markdown(f"<h3 style='color: #d84519;'>Cuentas de Twitter más mencionados por {real_name}</h3>", unsafe_allow_html=True)
    
    # text = []
    # for tweet in data.values():
    #     text = text + [tweet['user_mentions']]
    
    # flat_list = [item for sublist in text for item in sublist]  
    # flat_list = [mention for mention in flat_list if mention != perfil]
    # mentions = pd.DataFrame(flat_list, columns = ['menciones'])['menciones'].value_counts().iloc[:10]
    # mentions = mentions.reset_index()
    # mentions = mentions.rename(columns = {'index': 'perfil'})
    
    # # st.write(mentions)
    
    # bars = alt.Chart(mentions).mark_bar(color = '#d84510').encode(
    #     x='menciones:Q',
    #     y=alt.Y('perfil:O', sort = '-x'))
    
    # text = bars.mark_text(align='left', baseline='middle',
    #     dx=3  # Nudges text to right so it doesn't appear on top of the bar
    #     ).encode(text='menciones:Q')
    
    # plot = alt.layer(bars, text).configure_view(
    #     stroke='transparent').configure_axis(
    #         domainWidth=0.8,
    #         ticks = False,
    #         labelFontSize = 13,
    #         titleFontSize = 15)
        
    # st.altair_chart(plot, use_container_width = True)
    
    # # =============================================================================
    # # Hashtags más usados
    # # =============================================================================
    # st.markdown(f"<h3 style='color: #d84519;'>Hashtags más utilizados por {real_name}</h3>", unsafe_allow_html=True)
    
    # text = []
    # for tweet in data.values():
    #     text = text + [tweet['hashtags']]
    
    # flat_list = [item for sublist in text for item in sublist]  
    # hashtags = pd.DataFrame(flat_list, columns = ['menciones'])['menciones'].value_counts().iloc[:10]
    # hashtags = hashtags.reset_index()
    # hashtags = hashtags.rename(columns = {'index': 'hashtags'})
    
    # # st.write(hashtags)
    
    # bars = alt.Chart(hashtags).mark_bar(color = '#d84510').encode(
    #     x='menciones:Q',
    #     y=alt.Y('hashtags:O', sort = '-x'))
    
    # text = bars.mark_text(align = 'left', baseline = 'middle',
    #     dx = 2  # Nudges text to right so it doesn't appear on top of the bar
    #     ).encode(text='menciones:Q')
    
    # plot = alt.layer(bars, text).configure_view(
    #     stroke='transparent').configure_axis(
    #         domainWidth=0.8,
    #         ticks = False,
    #         labelFontSize = 13,
    #         titleFontSize = 15)
        
    # st.altair_chart(plot, use_container_width = True)

# =============================================================================
# 
# =============================================================================
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
    st.sidebar.markdown('Consultas a la app {}.'.format(len(pageviews)))
except ValueError:
    st.sidebar.markdown('Consultas a la app {}.'.format(1))
