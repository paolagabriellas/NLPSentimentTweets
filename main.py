import nltk
from nltk.corpus import twitter_samples
import json
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import tweepy
from config import API_KEYS


# Twitter API vars
api_key = API_KEYS['api_key']
api_secret = API_KEYS['api_secret']
access_token = API_KEYS['access_token']
access_secret = API_KEYS['access_secret']

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


class Tweet:
    def __init__(self, text, favCount, rtCount):
        self.text = text
        self.favCount = favCount
        self.rtCount = rtCount

    def updateText(self, text):
        self.text = text


def getTweets():
    # get tweets in english language
    tweets = tweepy.Cursor(api.search, q="lang:en").items(1000)
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
        obj = Tweet(tweet.text, favCount, tweet.retweet_count)
        tweetsList.append(obj)
    return tweetsList


def getPopular(tweets):
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


if __name__ == '__main__':
    # print('Hello world')
    #
    # # pull in sample tweets for vader testing
    # tweet_data = twitter_samples.open('positive_tweets.json')
    # lines = tweet_data.readlines()
    # pattern = r'RT\s@.+:\s|\shttp.+'
    # tweets = list()
    # for line in lines:
    #     json_object = json.loads(line)
    #     text = json_object['text']
    #     split = re.split(pattern, text)
    #     for string in split:
    #         if string != '':
    #             tweets.append(string)
    #
    # # create vader sentiment analyzer, testing on tweets below
    # vader = SentimentIntensityAnalyzer()
    # for tweet in tweets:
    #     print(tweet)
    #     polarity_scores = vader.polarity_scores(tweet)
    #     for x in sorted(polarity_scores):
    #         print('{0}: {1}, '.format(x, polarity_scores[x]), end='')
    #         # polarity_scores['compound'] for just the compound score
    #     print()

    # pattern to clean tweet text
    pattern = r'RT\s@.+:\s|\shttp.+'
    vader = SentimentIntensityAnalyzer()
    tweets = getTweets()
    popular_tweets = getPopular(tweets)
    for i in range(50):
        tweet = tweets[i]
        text = tweet.text
        split = re.split(pattern, text)
        for string in split:
            if string != '':
                text = string
        polarity_scores = vader.polarity_scores(text)
        print(text)
        print('{}: {}, {}: {}, {}: {}'.format('retweet count', tweet.rtCount, 'favorite count', tweet.favCount,
                                              'compound score', polarity_scores['compound']))

    print()
    print('#### Popular tweets ####')
    print()

    for j in range(50):
        tweet = popular_tweets[j]
        text = tweet.text
        split = re.split(pattern, text)
        for string in split:
            if string != '':
                text = string
        polarity_scores = vader.polarity_scores(text)
        print(text)
        print('{}: {}, {}: {}, {}: {}'.format('retweet count', tweet.rtCount, 'favorite count', tweet.favCount,
                                              'compound score', polarity_scores['compound']))



