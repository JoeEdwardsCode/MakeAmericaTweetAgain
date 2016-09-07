from apscheduler.schedulers.background import BackgroundScheduler
from os import system
from time import sleep
from datetime import datetime

from api import getAPI
from tweetGenerator import TrumpTweetGenerator

print("tweetScheduler.py Loaded @ {}".format(datetime.now()))

# Edit Global TWITTER_NAME for Different User
TWITTER_NAME = "realDonaldTrump"
FOLLOWERS = []

try:
    print("Attempting to Load/Get New Tweet Set")
    try:
        # Load Existing Tweet Set if We Already Have One
        GENERATOR = TrumpTweetGenerator(TWITTER_NAME + "Tweets")
        print("Tweet Generator Created @ {}".format(datetime.now()))
    except:
        # Gather New Tweet Set
        print("Getting Most Current Tweets @ {}".format(datetime.now()))
        system("python getTweetsFromUser.py " + TWITTER_NAME)
        print("Tweet Set Collected @ {}".format(datetime.now()))
        GENERATOR = TrumpTweetGenerator(TWITTER_NAME + "Tweets")
        print("Tweet Generator Created @ {}".format(datetime.now()))
    API = getAPI()
    print("Bot Ready To Post.")
    print("Test Tweet:  {}".format(GENERATOR.generateTrumpTweet()))
except:
    print("Setup Failed @ {}".format(datetime.now()))
    print("Exiting tweetScheduler.py")
    quit()

def updateTweets():
    try:
        system("python getTweetsFromUser.py " + TWITTER_NAME)
        newGen = TrumpTweetGenerator(TWITTER_NAME + "Tweets")
        print("Tweet Set Updated @ {}".format(datetime.now()))
        GENERATOR = newGen
    except:
        print("Tweet Set Update Failed @ {}".format(datetime.now()))

def postTweet():
    date = datetime.now()
    if date.hour >= 8 and date.hour <= 20:
        tweet = cleanTweet(GENERATOR.generateTrumpTweet())
        try:
            if rateLimitNotExceeded():
                API.update_status(tweet)
                print("Tweet Posted @ {}".format(datetime.now()))
                print("--- {}".format(tweet))
        except:
            print("Tweet Posting Failed @ {}".format(datetime.now()))
    else:
        print("Tweet Posting Delayed. Resumes at 8:00 AM")

def friendFollowers():
    print("Getting Followers List @ {}".format(datetime.now()))
    if rateLimitNotExceeded():
        followers = API.followers()
        if followers:
            for follower in followers:
                if follower.id not in FOLLOWERS:
                    if rateLimitNotExceeded():
                        print("Creating Friendship with User: {}".format(follower.id))
                        API.create_friendship(follower.id)
                        FOLLOWERS.append(follower.id)

def likeAndReplyToMAGA():
    print("Liking Tweets @ {}".format(datetime.now()))
    if rateLimitNotExceeded():
        tweets = API.search("MakeAmericaGreatAgain")
        for tweet in tweets:
            if rateLimitNotExceeded():
                API.create_favorite(tweet.id)
            if rateLimitNotExceeded():
                reply = cleanTweet(GENERATOR.generateTrumpTweet())
                API.update_status(reply, tweet.id)

def likeAndFollowRetweets():
    print("Liking Retweets & following poster @ {}".format(datetime.now()))
    if rateLimitNotExceeded():
        retweets = API.retweets_of_me()
        for tweet in retweets:
            if rateLimitNotExceeded():
                API.create_favorite(tweet.id)
            if rateLimitNotExceeded() and not tweet.user.id in FOLLOWERS:
                API.create_friendship(tweet.user.id)
                FOLLOWERS.append(tweet.user.id)

def rateLimitNotExceeded():
    status = API.rate_limit_status()['resources']['application']['/application/rate_limit_status']['remaining']
    if status > 0:
        print("Rate Limit Status: API Under Rate Limit ({}) @ {}".format(status, datetime.now()))
    else:
        print("Rate Limit Status: Rate Limit Exceeded @ {}".format(datetime.now()))
    return status > 0

def cleanTweet(tweet):
    if tweet.count('"') == 1:
        tweet.replace('"', '')
    if "amp;" in tweet:
        tweet.replace("amp;", "")
    return tweet

tweetScheduler = BackgroundScheduler()
tweetScheduler.add_job(postTweet, 'interval', minutes=15, id='postTweet')
tweetScheduler.add_job(updateTweets, 'cron', hour=23, minute=59, id='updateTweets')
tweetScheduler.add_job(friendFollowers, 'cron', hour=22, id='friendFollowers')
tweetScheduler.add_job(likeAndReplyToMAGA, 'cron', hour=7, id='likeAndReplyToMAGA')
tweetScheduler.add_job(likeAndFollowRetweets, 'cron', hour=5, id='likeAndFollowRetweets')
tweetScheduler.start()
while True:
    sleep(60)
