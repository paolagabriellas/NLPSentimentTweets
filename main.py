import nltk
from nltk.corpus import twitter_samples
import json
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize

if __name__ == '__main__':
    print('Hello world')

    # pull in sample tweets for vader testing
    tweet_data = twitter_samples.open('positive_tweets.json')
    lines = tweet_data.readlines()
    pattern = r'RT\s@.+:\s|\shttp.+'
    tweets = list()
    for line in lines:
        json_object = json.loads(line)
        text = json_object['text']
        split = re.split(pattern, text)
        for string in split:
            if string != '':
                tweets.append(string)
    # create vader sentiment analyzer, testing on tweets below
    vader = SentimentIntensityAnalyzer()
    for tweet in tweets:
        print(tweet)
        polarity_scores = vader.polarity_scores(tweet)
        for x in sorted(polarity_scores):
            print('{0}: {1}, '.format(x, polarity_scores[x]), end='')
            # polarity_scores['compound'] for just the compound score
        print()


