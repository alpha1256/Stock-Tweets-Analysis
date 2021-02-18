from init import *
import tweepy
from tweepy import OAuthHandler
from tweepy import API
from tweepy.streaming import StreamListener
from tweepy import Stream
from concurrent.futures import ThreadPoolExecutor as PoolExecutor

#Ignore robinhood, webull, fee, giveaway

def tweetParse(a):
	tempString = a.text
	tempOriginal = a.text
	check = False
	tempString = tempString.lower()
	tempString = re.sub(r"https.\/\/.+", "",tempString )
	tempString = re.sub(r"(\$[a-zA-Z]+)", "", tempString)
	tempString = re.sub(r"(@[a-zA-Z0-9]+)", "", tempString)
	encoded = tempString.encode("ascii", "ignore")
	tempString = encoded.decode()
	tempString = tempString.strip()
	checkRob = re.findall(r"(robinhood)", tempString)
	checkGive = re.findall(r"(giveaway)", tempString)
	checkWe = re.findall(r"(webull)", tempString)
	checkfee = re.findall(r"(giveaway)", tempString)
	checkearn = re.findall(r"(earn)", tempString)
	checkGiving = re.findall(r"(giving away)", tempString)
	checkBit = re.findall(r"(bitcoin)", tempString)
	if len(checkRob) > 0 or len(checkGive) > 0:
		check = True
	if len(checkWe) > 0 or len(checkGive) > 0:
		check = True
	if len(checkearn) > 0 or len(checkGiving) > 0:
		check = True
	if len(checkBit) > 0:
		check = True
	if tempString == "":
		check = True
	if tempOriginal in originalTweets:
		check = True

	if check is False:
		parsedTweets.append(tempString)
		originalTweets.append(tempOriginal)

def enterTrainingData():
	goingUp = open("going_up.txt", 'r')
	for a in goingUp:
		trendUp.append(a)
	goingDown = open("going_down.txt", 'r')
	for b in goingDown:
		trendDown.append(b)

def sampleTrain(cl):
	for a in trendUp:
		cl.train(a, "going up")
	for b in trendDown:
		cl.train(b, "going down")


#Train Model
trendUp = []
trendDown =[]

enterTrainingData()
cl = naivebayes(getwords)
sampleTrain(cl)
print("Done training")

#Login
access_token = "oauth_token"
access_token_secret = "oauth_secret"
consumer_key = "api_key"
consumer_secret = "api_key_secret"

#Get tweets
originalTweets = []
parsedTweets =[]
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

search_words = input("Enter ticker symbol: ")
filter_tweets = search_words + "-filter:retweets"

public_tweets = tweepy.Cursor(api.search, q = filter_tweets, lang ="en").items(100)
with PoolExecutor(max_workers=10) as executor:
    for _ in executor.map(tweetParse, public_tweets):
        pass

#Classify tweets
positiveSentiments = []
negativeSentiments = []
positiveTweets =[]
negativeTweets =[]
for a in parsedTweets:
	classValue = cl.classify(a, default='unknown')
	#print(a, "\n---------------- classified as ", classValue)
	if classValue == "going up":
		positiveTweets.append(a)
		positiveSentiments.append(1)
	elif classValue == "going down":
		negativeTweets.append(a)
		negativeSentiments.append(1)

totalSentiments = len(positiveSentiments) + len(negativeSentiments)
percent = len(positiveSentiments) / totalSentiments

newFile = open("OrgTweets.txt", "w", encoding="utf-8")
for a in originalTweets:
	newFile.write(a)
	newFile.write("----------------------------------------\n")

newFile.close()
print(search_words," is a total ", percent, "% buy")

posFile = open("positiveTweets.txt", 'w')
for a in positiveTweets:
	posFile.write(a)
	posFile.write("\n-----------------------------------------\n")
posFile.close()

negFile = open("negativeTweets.txt", 'w')
for a in negativeTweets:
	negFile.write(a)
	negFile.write("\n-----------------------------------------\n")
negFile.close()
