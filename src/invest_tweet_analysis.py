import tweepy
from tweepy import OAuthHandler
from tweepy import API
from tweepy.streaming import StreamListener
from tweepy import Stream
import re
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
import plotly.graph_objs as go
import plotly.offline as ply

def workonTweets(a):
	#print(a.text)
	patternUp = re.compile(r"(buy)")
	patternDown = re.compile (r"(sell)")
	patternLong = re.compile(r"(go long)")
	patternShort = re.compile(r"(go short)")
	patternRocket = re.compile(r"(rocket)")
	upMatch = re.findall(patternUp, a.text)
	downMatch = re.findall(patternDown, a.text)
	longMatch = re.findall(patternLong, a.text)
	shortMatch = re.findall(patternShort, a.text)
	rocketMatch = re.findall(patternRocket, a.text)
	if len(upMatch) > 0 or len(longMatch) > 0 or len(rocketMatch) > 0:
		positive_sentiments.append(1)
		print("Got Postive")
	elif len(downMatch) > 0 or len(shortMatch) > 0:
		negative_sentiments.append(1)
		print("Got Postive")

access_token = "ouath_token"
access_token_secret = "oauth_secret"
api_key = "api_key"
api_key_secret = "api_key_secret"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

search_words = input("Enter ticker symbol: ")
filter_tweets = search_words + "-filter:retweets"

negative_sentiments = []
positive_sentiments = []


public_tweets = tweepy.Cursor(api.search, q = filter_tweets, lang ="en").items(1000)
with PoolExecutor(max_workers=10) as executor:
    for _ in executor.map(workonTweets, public_tweets):
        pass

print("Positive sentiments: ",len(positive_sentiments))
print("Negative sentiments: ",len(negative_sentiments))

domain = ['Negative', 'Positive']
domainSentiments = [len(negative_sentiments), len(positive_sentiments)]

#plotly section for drawing graph of sentiments 
print("Drawing graph of tweets to domain") 
trace1 = go.Bar(x=domain, y=domainSentiments)
data=[trace1]
layout = dict(title = search_words+" sentiments",
		xaxis = dict(title = "Domain", showticklabels=True),
		yaxis = dict(title ="Number of sentiments"))
fig = dict(data = data, layout = layout)
ply.plot(fig, filename='tweetGraph.html')