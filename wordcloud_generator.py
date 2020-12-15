import json
import datetime
import re
import numpy as np

import nltk
from nltk.corpus import stopwords
from stop_words import get_stop_words

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image
import altair as alt
from PIL import Image



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

for perfil in perfiles:
    print(perfil)
    # Leemos los últimos 3200 tuits
    with open(f'dat_20201212/{perfil}_tweets.json','rb') as f:
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
    text = text.replace(perfil, '')
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
                ).generate(text)
    
    plt.imshow(wordcloud)
    plt.axis("off")
    path_wc = f'wordcloud/wordcloud_{perfil}.png'
    plt.savefig(path_wc, dpi=300)