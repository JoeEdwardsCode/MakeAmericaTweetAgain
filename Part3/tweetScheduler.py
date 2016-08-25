from apscheduler.schedulers.background import BackgroundScheduler
from os import system
from time import sleep
from datetime import datetime
import json

from api import getAPI
from tweetGenerator import TrumpTweetGenerator

print("tweetScheduler.py Loaded @ {}".format(datetime.now()))

# Edit Global TWITTER_NAME for Different User
TWITTER_NAME = "realDonaldTrump"
TWEET_WINDOW = True
FOLLOWERS = []

try:
    print("Attempting to Load/Get New Tweet Set")
    try:
        GENERATOR = TrumpTweetGenerator(TWITTER_NAME + "Tweets")
        print("Tweet Generator Created @ {}".format(datetime.now()))
    except:
        print("Getting Most Current Tweets @ {}".format(datetime.now()))
        system("python getTweetsFromUser.py " + TWITTER_NAME)
        print("Tweet Set Collected @ {}".format(datetime.now()))
        # If not using TrumpTweetGenerator object, change to TweetGenerator object
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
    if TWEET_WINDOW:
        tweet = GENERATOR.generateTrumpTweet()
        try:
            if rateLimitNotExceeded():
                API.update_status(tweet)
                print("Tweet Posted @ {}".format(datetime.now()))
                print("--- {}".format(tweet))
            else:
                print("API Calls Maxed Out @ {}".format(datetime.now()))
        except:
            print("Tweet Posting Failed @ {}".format(datetime.now()))
    else:
        print("Tweet Posting Delayed. Resumes at 8:00 AM")

def likeFollowers():
    print("Getting Followers List @ {}".format(datetime.now()))
    if rateLimitNotExceeded():
        followers = API.followers()
        if followers:
            for follower in followers:
                if follower.id not in FOLLOWERS
                    if rateLimitNotExceeded():
                        print("Creating Friendship with User: {}".format(follower.id))
                        API.create_friendship(follower.id)
                        FOLLOWERS.append(follower.id)
                    else:
                        print("API Calls Maxed Out @ {}".format(datetime.now()))

def likeTweets():
    print("Liking Tweets @ {}".format(datetime.now()))
    if rateLimitNotExceeded():
        tweets = API.search("@"+TWITTER_NAME)
        for tweet in tweets:
            if rateLimitNotExceeded():
                API.create_favorite(tweet.id)
            else:
                print("API Calls Maxed Out @ {}".format(datetime.now()))
    else:
        print("API Calls Maxed Out @ {}".format(datetime.now()))


def rateLimitNotExceeded():
    status = API.rate_limit_status()['resources']['application']['/application/rate_limit_status']['remaining']
    if status > 0:
        print("Rate Limit Status: API Under Rate Limit ({}) @ {}".format(status, datetime.now()))
    else:
        print("Rate Limit Status: Rate Limit Exceeded @ {}".format(datetime.now()))
    return status > 0

def closeTweetWindow():
    TWEET_WINDOW = False

def openTweetWindow():
    TWEET_WINDOW = True


tweetScheduler = BackgroundScheduler()
tweetScheduler.add_job(closeTweetWindow, 'cron', hour=21, id='closeTweetWindow')
tweetScheduler.add_job(openTweetWindow, 'cron', hour=8, id='openTweetWindow')
tweetScheduler.add_job(postTweet, 'interval', minutes=15, id='postTweet')
tweetScheduler.add_job(updateTweets, 'cron', hour=23, minute=59, id='updateTweets')
tweetScheduler.add_job(likeFollowers, 'cron', hour=22, id='likeFollowers')
tweetScheduler.add_job(likeTweets, 'cron', hour=7, id='likeTweets')
tweetScheduler.start()
while True:
    sleep(60)
