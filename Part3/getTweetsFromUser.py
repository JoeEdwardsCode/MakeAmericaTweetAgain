from sys import argv
import time
import json

from api import getAPI

REQUEST_DELAY = 3
MAX_REQUESTS = 150

def main():
    try:
        arg = argv[1]
        api = getAPI()
        tweetResults = []

        tweetIndex = api.user_timeline(screen_name=arg, count=1)[0].id
        time.sleep(REQUEST_DELAY)
        for request in range(MAX_REQUESTS):
            tweets = api.user_timeline(screen_name=arg, include_retweets=False, max_id=tweetIndex)
            for tweet in tweets:
                tweetResults.append(tweet.text)
                tweetIndex = tweet.id
            time.sleep(REQUEST_DELAY)

    except IndexError:
        print("Program Missing Arg. Twitter Handle")
    except Exception as e:
        print("Program Failure.  Error: {}".format(e))
    finally:
        with open("{}Tweets".format(arg), 'w') as saveFile:
            json.dump(tweetResults, saveFile)
            print("File Saved.")

if __name__ == '__main__':
    main()
