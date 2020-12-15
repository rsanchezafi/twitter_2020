import tweepy #https://github.com/tweepy/tweepy
import csv
import json
import os

#Twitter API credentials
config = json.load(open('sf_config.json', 'rb'))

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
    path_data = f"dat_20201212/{data[key]['twitter_name']}_tweets.json"
    if not os.path.isfile(path_data):
        perfiles = perfiles + [data[key]['twitter_name']]

for perfil in perfiles:
    print(perfil)
    screen_name = perfil
    #Twitter only allows access to a users most recent 3240 tweets with this method
    
    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    
    #initialize a list to hold all the tweepy Tweets
    alltweets = []  
    
    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name, count = 200, 
                                   tweet_mode = 'extended', include_rts = True)
    
    #save most recent tweets
    alltweets.extend(new_tweets)
    
    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    
    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print(f"getting tweets before {oldest}")
        
        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name, count = 200, 
                                       max_id=oldest, tweet_mode = 'extended', include_rts = True)
        
        #save most recent tweets
        alltweets.extend(new_tweets)
        
        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        
        print(f"...{len(alltweets)} tweets downloaded so far")
    
    #transform the tweepy tweets into a 2D array that will populate the csv 
    # outtweets = [[tweet.id_str, tweet.created_at, tweet.text] for tweet in alltweets]
    dict_aux = dict()
    for tweet in alltweets:
        try:
            tweet_hashtags = []
            for hashtag in tweet.entities['hashtags']:
                tweet_hashtags = tweet_hashtags + [hashtag['text']]
                
            tweet_user_mentions = []
            for user_mention in tweet.entities['user_mentions']:
                tweet_user_mentions = tweet_user_mentions + [user_mention['screen_name']]
                
            if tweet.full_text.startswith("RT @"):
                dict_aux[str(tweet.created_at)] = {'full_text': tweet.full_text, 
                                                   'full_text_RT': tweet.retweeted_status.full_text,
                                                   'screen_name_RT': tweet.retweeted_status.author.screen_name,
                                                   'source': tweet.source,
                                                   'hashtags': tweet_hashtags,
                                                   'user_mentions': tweet_user_mentions
                                                   }
            else:
                dict_aux[str(tweet.created_at)] = {'full_text': tweet.full_text, 
                                                   'source': tweet.source,
                                                   'hashtags': tweet_hashtags,
                                                   'user_mentions': tweet_user_mentions
                                                   }
        except Exception as e:
            print(f'{perfil}: {tweet.full_text}')
            print(f'ERROR: {str(e)}')
        
    #write the csv  
    # with open(f'new_{screen_name}_tweets.csv', 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["id","created_at","text"])
    #     writer.writerows(outtweets)
    
    # write json
    with open(f'dat_20201212/{screen_name}_tweets.json', 'w', encoding='utf-8') as f:
        json.dump(dict_aux, f, ensure_ascii=False, indent=4)
    







