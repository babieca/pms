# -*- coding: utf-8 -*-
import tweepy
import datetime
import re
import json
import asyncio

from config import conf
from ddbb import SQLite
from controller import Broadcaster

auth = tweepy.OAuthHandler(
    conf.get('twitter',{}).get('api_key'),
    conf.get('twitter',{}).get('api_secret'))

auth.set_access_token(
    conf.get('twitter',{}).get('access_token'),
    conf.get('twitter',{}).get('access_token_secret'))

api = tweepy.API(auth)


class StreamListener(tweepy.StreamListener, Broadcaster):

    def __init__(self, keywords):
        self.keywords = keywords
    
    def on_data(self, data):
        # Make it JSON
        tweet = json.loads(data)

        # filter out retweets
        if ('text' in tweet and
            'created_at' in tweet and
            'id_str' in tweet and
            'name' in tweet['user'] and
            'screen_name' in tweet['user'] and
            'followers_count' in tweet['user'] and
            'created_at' in tweet['user']):
        
            if 'RT @' not in tweet['text']:
                kws = self.keywords.split() if type(self.keywords) is str else self.keywords
                for kw in kws:
                    if kw in tweet['text']:
                        
                        created_at = datetime.datetime.strptime(
                                        tweet['created_at'],
                                        '%a %b %d %H:%M:%S +%f %Y')
                        user_created_at = datetime.datetime.strptime(
                                            tweet['user']['created_at'],
                                            '%a %b %d %H:%M:%S +%f %Y')
                        
                        data = {'created_at': created_at.isoformat(),
                                'id_str': tweet['id_str'],
                                'tweet': tweet['text'],
                                'user_name': tweet['user']['name'],
                                'user_screen_name': tweet['user']['screen_name'],
                                'user_followers_count': tweet['user']['followers_count'],
                                'user_created_at': user_created_at.isoformat(),
                                'user_location': tweet['user']['location'],
                                'keyword': kw}
                        
                        oSQLite = SQLite(conf.get('sqlite',{}).get('path'),
                                         conf.get('sqlite',{}).get('name'),
                                         conf.get('sqlite',{}).get('table'))
                        oSQLite.insert(data)

                        Broadcaster.update_cache(data)
                        Broadcaster.send_updates(data)
        
    def on_error(self, status_code):
        if status_code == 420:
            return False
        
    # limit handling
    def on_limit(self, status):
        logger.info('Limit threshold exceeded: {}'.format(status))
    
    def on_timeout(self, status):
        logger.info('Stream disconnected; continuing...')  
    
    '''    
    def on_data(self, data):
        pass
        #return format_tweets(data)
    '''


async def twitterStream(keywords):

    stream_listener = StreamListener(keywords)
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    
    # filter levels: none, low, medium, high
    stream.filter(languages=["en"], track=keywords, encoding='utf8', is_async=True, filter_level='medium')


def twitter_search(to_search, retweets=False, max_tweets=100):
  
    tweet_filter = ''
    if not retweets:
        tweet_filter = ' -filter:retweets'
    
    query = to_search + tweet_filter
    
    searched_tweets = []
    last_id = -1
    while len(searched_tweets) < max_tweets:
        count = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search(q=query, count=count, max_id=str(last_id - 1))
            if not new_tweets:
                break
            
            searched_tweets.extend(new_tweets)
            last_id = new_tweets[-1].id
        except TweepError as e:
            # depending on TweepError.code, one may want to retry or wait
            # to keep things simple, we will give up on an error
            break
        
    return format_tweets(searched_tweets)


def format_tweets(tweets):
    
    filt = '[^A-Za-z0-9\ \/\\\:\.\,\[\]\!\-\_\{\}\$\£\€\%\+\=\&\^\*\#\@\?\<\>\;\~]+'
    
    count = 0
    # tblhdr = {'id': '#',
    #          'date': 'Date',
    #          'time': 'Time',
    #          'username': 'Username',
    #          'lang': 'Lang', 
    #          'retweeted': 'Retweeted', 
    #          'truncated': 'Truncated', 
    #          'tweet': 'Tweet'}

    # table_data = [tblhdr]
    table_data = []
    for tweet in tweets:
        if (not tweet.retweeted) and ('RT @' not in tweet.text):
            tblrow = {
                'id': str(count),
                'date': tweet.created_at.strftime('%Y-%m-%d'),
                'time': tweet.created_at.strftime('%H:%M:%S'),
                'username': re.sub(filt, '', tweet.user.name),
                'lang': tweet.lang,
                'retweeted': 'Yes' if tweet.retweeted else 'No',
                'truncated': 'Yes' if tweet.truncated else 'No',
                'tweet': re.sub(filt, '', tweet.text.encode("ascii", errors="ignore").decode("ascii"))
                }
            table_data.append(tblrow)
            count += 1

    return table_data

__all__ = ['twitterStream', 'twitter_search']


