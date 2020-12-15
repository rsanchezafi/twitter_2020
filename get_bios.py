import tweepy #https://github.com/tweepy/tweepy
import csv
import json
import os

#Twitter API credentials
config = json.load(open('config.json', 'rb'))

consumer_key = config['consumer_key']
consumer_secret = config['consumer_secret']
access_key = config['access_key']
access_secret = config['access_secret']

# Cargamos json políticos
with open(r"data_politicos.json", "r", encoding = 'utf-8') as read_file:
    data = json.load(read_file)
data = dict((key,d[key]) for d in data for key in d)

perfiles = []
for key in data.keys():    
    perfiles = perfiles + [data[key]['twitter_name']]

dict_bios = dict()
for screen_name in perfiles:
    print(screen_name)
    #Twitter only allows access to a users most recent 3240 tweets with this method
    
    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    
    user = api.get_user(screen_name)
    dict_bios[screen_name] = user.description

with open('data_bios.json', 'w') as fp:
    json.dump(dict_bios, fp)