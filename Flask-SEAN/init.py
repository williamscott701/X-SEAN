# import nltk
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('stopwords')
# nltk.download('punkt')

import tweepy
import time
import datetime
import re
import json
import operator
import nltk
import os
import string
import copy
import _pickle as pickle
import math
import matplotlib.pyplot as plt
import re
import glob
import scipy.spatial
import json

from flask import Flask
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from collections import Counter
from pprint import pprint
from sklearn import preprocessing
from dateutil.parser import parse
from sentimentanalysis.sentiment import SentimentAnalysis
from flask import request, jsonify

w_tokenizer = nltk.tokenize.WhitespaceTokenizer()
sentiment_analysis = SentimentAnalysis(filename='sentimentanalysis/SentiWordNet.txt', weighting='harmonic')
stop_words = stopwords.words('english')
stop_words.append('rt')
stop_words.append('\n')

app = Flask(__name__)
app.run(debug=True)

def hydrate_tweet(tweet_id):
    CONSUMER_KEY = '***REMOVED_TWITTER_CONSUMER_KEY***'
    CONSUMER_SECRET = '***REMOVED_TWITTER_CONSUMER_SECRET***'
    OAUTH_TOKEN = '***REMOVED_TWITTER_ACCESS_TOKEN***'
    OAUTH_TOKEN_SECRET = '***REMOVED_TWITTER_ACCESS_TOKEN_SECRET***'
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    api = tweepy.API(auth)

    try:
        tweet = api.get_status(tweet_id)._json
        with open(str(tweet_id) + '.json', 'w') as f:
            json.dump(tweet, f)
        return tweet
    except:
        return 'Tweet ID not detected.'

def get_tweet_text(tweet_object):
    return tweet_object['text']

def get_processed_text(text):
    text = re.sub(r'http\S+', ' ', text)
    text = re.sub(r'[^a-zA-Z@]', ' ', text).lower()
    tokens = [w for w in w_tokenizer.tokenize(text) if w not in stop_words and w[0] != '@']
    return ' '.join(tokens)

def tweet_extra_features(text):
    senti_score = sentiment_analysis.score(text)
    tokens = nltk.word_tokenize(text.lower())
    tags = nltk.pos_tag(nltk.Text(tokens))
    counter_ = Counter(tag for word, tag in tags)
    prp = int(counter_['PRP'])  # personal pronoun	I, he, she
    prp_ = int(counter_['PRP$'])  # possessive pronoun	my, his, hers
    pronouns = prp + prp_
    adjectives = int(counter_['JJ']) + int(counter_['JJR']) + int(counter_['JJS'])  # adjective
    nouns = int(counter_['NN']) + int(counter_['NNS']) + int(counter_['NNP']) + int(counter_['NNPS'])  # nouns
    vb = int(counter_['VB']) + int(counter_['VBD']) + int(counter_['VBG']) + int(counter_['VBN']) + int(
        counter_['VBP']) + int(counter_['VBZ'])  # verbs
    return [senti_score, nouns, adjectives, pronouns, vb]

def tweet_special_chars(text):
    num_special = 0
    for char in text:
        if not char.isalnum():
            num_special += 1

    if num_special < 0:
        print("ERROR: Okay something went really wrong here...")
        num_special = 0

    return num_special

def tweet_all_features(tweet):
    num_user_mentions = len(tweet['entities']['user_mentions'])
    num_hashtags = len(tweet['entities']['hashtags'])
    num_urls = len(tweet['entities']['urls'])
    num_favs = tweet['favorite_count']
    num_rts = tweet['retweet_count']

    if 'media' in tweet['entities']:
        num_media = len(tweet['entities']['media'])
    else:
        num_media = 0

    is_reply = 0
    if tweet['in_reply_to_status_id']:
        is_reply = 1

    num_special_chars = tweet_special_chars(tweet)
    text = get_tweet_text(tweet)
    tweet_length = len(text)
    extra_features = tweet_extra_features(text)

    return [num_user_mentions, num_hashtags, num_urls, num_favs, num_rts, num_media, is_reply,
            num_special_chars, tweet_length] + extra_features

def user_all_features(tweet):
    verified = tweet['user']['verified']
    followers_count = tweet['user']['followers_count']
    friends_count = tweet['user']['friends_count']
    favourites_count = tweet['user']['favourites_count']
    statuses_count = tweet['user']['statuses_count']

    return [verified, followers_count, friends_count, favourites_count, statuses_count]

def process(tweet_id):
    tweet_object = hydrate_tweet(tweet_id)

    if tweet_object == '-1':
        return 'Tweet id', tweet_id, 'doesn\'t exist'
    else:
        tweet_text = get_tweet_text(tweet_object)
        processed_text = get_processed_text(tweet_text)
        tweet_features = tweet_all_features(tweet_object) #
        user_features = user_all_features(tweet_object)

        return_data = [tweet_text, processed_text, tweet_features, user_features]

        return return_data

@app.route('/')
def main():
    data = request.args.get("data", "")

    if data.split("/")[-2] != "status":
        return "Error! Not in status page"
    else:
        tweet_id = data.split("/")[-1]
        print("tweet_id", tweet_id)
        return_data = process(tweet_id)
        print(return_data)
        return str(return_data)

# except Exception as e:
# 	print(e)
# 	return str(e)
# return jsonify(data)
# return get_tweet(1277846219277008897)