import nltk
import tweepy
import json

# Twitter API vars
api_key = 'jSnViwO15mr0Yhgdv8VVV3MzA'
api_secret = 'QDyIqKJMWOTIsxsoi0LRrrpi45St56rcJrZRjIOnr5mNMWiOUJ'
access_token = '549804137-7q0hZyVZazQn4DlIF4qtmnfpV2aJNfFaTIReGqB7'
access_secret = 'kMAcWXxoZCAr4z7TMlWs9B6bvVEMR71Jx54tb5m97qhye'

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

class Tweet:
    def __init__(self, text, favCount, rtCount):
	self.text = text
	self.favCount = favCount
	self.rtCount = rtCount

    def updateText(text):
        self.text = text

def getTweets():
    #get tweets in english language 
    tweets = tweepy.Cursor(api.search, q="lang:en").items(1000)

    for tweet in tweets:
	tweetArr.append(tweet)
    
    tweetsList = []
    for tweet in tweetArr:
	#print(tweet.text, "	rt count:  ", tweet.retweet_count)
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

def cleanTokens(txt):
    # remove urls and symbols, return tokens
    txt = " ".join(re.sub(r"([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())
    return nltk.word_tokenize(txt)

