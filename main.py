import nltk
from nltk.corpus import twitter_samples
import json
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import tweepy
from config import API_KEYS
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2_contingency
import scipy
from scipy.stats import iqr

# Twitter API vars
api_key = API_KEYS['api_key']
api_secret = API_KEYS['api_secret']
access_token = API_KEYS['access_token']
access_secret = API_KEYS['access_secret']

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


class Tweet:
    def __init__(self, id, text, favCount, rtCount):
        self.id = id
        self.text = text
        self.favCount = favCount
        self.rtCount = rtCount
        self.popularity = favCount + rtCount
        self.polarity = None

    def updateText(self, text):
        self.text = text
    
    def updatePolarity(self, polarity):
        self.polarity = polarity

def getTweets():
    # get tweets in english language
    tweets = tweepy.Cursor(api.search, q="lang:en").items(300000)
    tweetArr = list()

    for tweet in tweets:
        tweetArr.append(tweet)

    tweetsList = []
    for tweet in tweetArr:
        # print(tweet.text, "	rt count:  ", tweet.retweet_count)
        favCount = 0
        if hasattr(tweet, "retweeted_status"):
            # print("favorite count:  ", tweet.retweeted_status._json["favorite_count"])
            favCount = tweet.retweeted_status._json["favorite_count"]
        else:
            # print("favorite count:  ", tweet.favorite_count)
            favCount = tweet.favorite_count
        obj = Tweet(tweet.id, tweet.text, favCount, tweet.retweet_count)
        tweetsList.append(obj)
    return tweetsList

def get10PercentPopular(tweets):
    # get 10% most popular tweets based on favs and RTs
    popular = []
    n = int(len(tweets) * 0.1)
    for i in range(0, n):
        maximum = 0
        maxObj = None
        for j in range(len(tweets)):
            if (tweets[j].favCount + tweets[j].rtCount) > maximum:
                maximum = tweets[j].favCount + tweets[j].rtCount
                maxObj = tweets[j]
        tweets.remove(maxObj)
        popular.append(maxObj)
    return popular

def getPopular(tweets):
    # get tweets with popularity > mean + std
    popularity_scores = [tweet.popularity for tweet in tweets]
    mean = scipy.stats.tmean(popularity_scores)
    std = scipy.stats.tstd(popularity_scores)
    popular = []
    for tweet in tweets:
        if tweet.popularity > (mean + std):
            popular.append(tweet)
    return popular

    # get those with popularity Score > 100
    # popular = []
    # for tweet in tweets:
    #     if tweet.popularity > 1000:
    #         popular.append(tweet)
    # return popular

def getUnpopular(tweets, popular):
    # get all tweets that are not on the popular list
	ids = []
	unpopular = []
	for tweet in popular:
		ids.append(tweet.id)
	for tweet in tweets:
		if (tweet.id not in ids):
			unpopular.append(tweet)
	return unpopular

def getNeutral(tweets, strong):
	#get tweets with neutral sentiment ( -0.05 < compound score< 0.05)
    strong_ids = [tweet.id for tweet in strong]
    neutrals = []
    for tweet in tweets:
        if tweet.id not in strong_ids:
            neutrals.append(tweet)
    return neutrals

def getSentimental(tweets):
    polarity_scores = [tweet.polarity for tweet in tweets]
    mean = scipy.stats.tmean(polarity_scores)
    std = scipy.stats.tstd(polarity_scores)
    strong = []
    for tweet in tweets:
        if tweet.polarity > (mean + std) or tweet.polarity < (mean - std):
            strong.append(tweet)
    return strong

	# #get tweets with strong sentiment ( -0.05 > compound score > 0.05)
	# sentimental = []
	# for tweet in tweets:
	# 	if tweet.polarity < -0.05 or tweet.polarity > 0.05:
	# 		sentimental.append(tweet)
	# return sentimental

def chiSquareTest(tweets):
    # H0: popularity and sentiment strength are independent

    popular = getPopular(tweets)
    # print(len(popular))
    unpopular = getUnpopular(tweets, popular)
    strongPopular = getSentimental(popular)
    strongUnpopular = getSentimental(unpopular)
    neutralPopular = getNeutral(popular, strongPopular)
    neutralUnpopular = getNeutral(unpopular, strongUnpopular)

    alpha = 0.05

    table = [
        [ len(strongPopular), len(strongUnpopular)],
        [ len(neutralPopular), len(neutralUnpopular)]
    ]

    # E = (row total * column total)/grand total

    stat, p, dof, expected = chi2_contingency(table)
    print("p value is " + str(p))
    if p <= alpha:
        print('Dependent (reject H0)')
    else:
        print('Independent (H0 holds true)')


def normalizePopularity(tweets):
    # find min and max
    min = tweets[0].popularity
    max = tweets[0].popularity
    for tweet in tweets:
        if tweet.popularity < min:
            min = tweet.popularity
        elif tweet.popularity > max:
            max = tweet.popularity

    # rescale popularity
    for tweet in tweets:
        tweet.popularity = float(tweet.popularity - min) / (max - min)

    return tweets

def normalizePolarity(tweets):
    # find min and max
    min = tweets[0].polarity
    max = tweets[0].polarity
    for tweet in tweets:
        if tweet.polarity < min:
            min = tweet.polarity
        if tweet.polarity > max:
            max = tweet.polarity

    # rescale polarity
    for tweet in tweets:
        tweet.polarity = -1 + (float(tweet.polarity - min) * 2) / (max - min)

    return tweets

if __name__ == '__main__':
    
    # pattern to clean tweet text
    pattern = r'RT\s@.+:\s|\shttp.+'
    vader = SentimentIntensityAnalyzer()
    tweets = getTweets()
    # print('got tweets')
    popularity = []
    for tweet in tweets:
        #print(tweet.popularity)
        popularity.append(tweet.popularity)

    # histogram for popularity tweets
    # interRange = iqr(popularity, interpolation='midpoint')
    # print(interRange, max(popularity), min(popularity))
    # binWidth = 2 * interRange * (len(popularity)**(-1/3))
    # numBins = (max(popularity)-min(popularity))/binWidth
    # print(numBins, int(numBins))
    # plt.hist(popularity, bins=305)
    # plt.savefig("histo.png")
    
    #popular_tweets = getPopular(tweets)

    for i in range(len(tweets)):
        tweet = tweets[i]
        text = tweet.text
        split = re.split(pattern, text)
        for string in split:
            if string != '':
                text = string
        polarity_scores = vader.polarity_scores(text)
        tweet.updatePolarity(polarity_scores['compound'])
        
        #print(text)
        #print('{}: {}, {}: {}, {}: {}'.format('retweet count', tweet.rtCount, 'favorite count', tweet.favCount,
        #                                     'compound score', polarity_scores['compound']))

    tweets = normalizePopularity(tweets)
    tweets = normalizePolarity(tweets)


    chiSquareTest(tweets)

    #print()
    #print('#### Popular tweets ####')
    #print()

    #for j in range(50):
    #    tweet = popular_tweets[j]
    #    text = tweet.text
    #    split = re.split(pattern, text)
    #    for string in split:
    #        if string != '':
    #            text = string
    #    polarity_scores = vader.polarity_scores(text)
    #    print(text)
    #    print('{}: {}, {}: {}, {}: {}'.format('retweet count', tweet.rtCount, 'favorite count', tweet.favCount,
    #                                          'compound score', polarity_scores['compound']))



