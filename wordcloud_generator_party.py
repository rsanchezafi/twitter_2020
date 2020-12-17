import json
import datetime
import re
import os
import numpy as np

import nltk
from nltk.corpus import stopwords
from stop_words import get_stop_words

from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image

# Cargamos json políticos
with open(r"data_politicos.json", "r", encoding = 'utf-8') as read_file:
    data_politicos = json.load(read_file)
data_politicos = dict((key,d[key]) for d in data_politicos for key in d)

perfiles = []
partidos = []
for key in data_politicos.keys():
    partido = data_politicos[key]['partido']
    if (partido not in partidos) and (partido != 'Independiente'):
        partidos = partidos + [partido]
    perfiles = perfiles + [f"{key} ({partido})"]
    
perfiles.sort()
partidos.sort()

for partido in partidos:
    print(partido)
    partido_politicos = [key for key in data_politicos.keys() if data_politicos[key]['partido'] == partido]
    
    text_total = ''
    for perfil in partido_politicos:
        print(perfil)
        # Leemos los últimos 3200 tuits
        with open(f"dat_20201212/{data_politicos[perfil]['twitter_name']}_tweets.json",'rb') as f:
            data = json.load(f)
    
        # Nos quedamos solo con los de 2020
        aux = dict()
        for date in data.keys():
            date_dt = datetime.datetime.strptime(date[:10], '%Y-%m-%d')
            if date_dt > datetime.datetime(2019, 12, 31):
                aux[date] = data[date]
        
        data = aux
    
        text = []
        for tweet in data.values():
            if 'full_text_RT' in tweet.keys():
                text = text + [tweet['full_text_RT']]
            else:
                text = text + [tweet['full_text']]
        text = ' '.join(text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub('[^\w\s]', '', text)
        idiomas = ['spanish', 'catalan', 'english']
        for idioma in idiomas:
            if idioma != 'catalan':
                text = [token for token in nltk.word_tokenize(text) if token.lower() not in stopwords.words(idioma)]
            else:
                text = [token for token in nltk.word_tokenize(text) if token.lower() not in get_stop_words(idioma)]
            text = ' '.join(text)        
    
        text = text.replace('RT', '')
        text = text.replace(partido, '')
        text_total = f'{text_total} {text}'
    
    for perfil in partido_politicos:
        text_total = text_total.replace(data_politicos[perfil]['twitter_name'], '')
    
    twitter_mask = np.array(Image.open("twitter-logo.png"))
    wordcloud = WordCloud(
                          #font_path='/Users/sebastian/Library/Fonts/CabinSketch-Bold.ttf',
                          #stopwords=STOPWORDS,
                          background_color='white',
                          width=5800,
                          height=3400,
                          mask=twitter_mask,
                          prefer_horizontal=1,
                            contour_width=0,
                ).generate(text_total)
    
    plt.imshow(wordcloud)
    plt.axis("off")
    path_wc = f'wordcloud/wordcloud_{partido}.png'
    plt.savefig(path_wc, dpi=300)
        