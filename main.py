import TwitterKeys

import time
import tweepy
import praw
import OAuth2Util
import datetime
import requests
import json
from tweepy.streaming import StreamListener
from tweepy import Stream



class PyStreamListener(StreamListener):
    def __init__(self, client):
        self.client = client
        self.do_action = True
        super(PyStreamListener, self).__init__()

    def on_data(self, data):
        if self.do_action:
            tweet = json.loads(data)
            try:
                publish = True

                if tweet.get('lang') and tweet.get('lang') != 'en':
                    publish = False

                if publish:
                    self.client.retweet(tweet['id'])
                    print(tweet['text'])


            except Exception as ex:
                print(ex)

            return True
        else:
            return False

    def on_error(self, status):
        print(status)




def SetUpTwitter():
    auth = tweepy.OAuthHandler(TwitterKeys.consumer_key, TwitterKeys.consumer_secret)
    auth.set_access_token(TwitterKeys.access_token, TwitterKeys.access_secret)
    api = tweepy.API(auth)
    return {"api" : api, "auth_handler": auth }


def TwitterHandleFromPK(opponent):
    # Carolina
    if opponent == "12":
        return "@NHLCanes"
    # Blue Jackets
    elif opponent == "29":
        return "@BlueJacketsNHL"
    # New Jersey
    elif opponent == "1":
        return "@NJDevils"
    # NY Islanders
    elif opponent == "2":
        return "@NYIslanders"
    # NY Rangers
    elif opponent == "3":
        return "@NYRangers"
    # Philadelphia
    elif opponent == "4":
        return "@NHLFlyers"
    # Pittsburgh
    elif opponent == "5":
        return "@penguins"
    # Washington
    elif opponent == "15":
        return "@Capitals"
    # Boston
    elif opponent == "6":
        return "@NHLBruins"
    # Buffalo
    elif opponent == "7":
        return "@BuffaloSabres"
    # Detroit
    elif opponent == "17":
        return "@DetroitRedWings"
    # Florida
    elif opponent == "13":
        return "@FlaPanthers"
    # Montreal
    elif opponent == "8":
        return "@CanadiensMTL"
    # Ottawa
    elif opponent == "9":
        return "@Senators"
    # Tampa Bay
    elif opponent == "14":
        return "@TBLightning"
    # Toronto
    elif opponent == "10":
        return "@MapleLeafs"
    # Chicago
    elif opponent == "16":
        return "@NHLBlackhawks"
    # Colorado
    elif opponent == "21":
        return "@Avalanche"
    # Dallas
    elif opponent == "25":
        return "@DallasStars"
    # Minnesota
    elif opponent == "30":
        return "@mnwild"
    # Nashville
    elif opponent == "18":
        return "@PredsNHL"
    # St. Louis
    elif opponent == "19":
        return "@StLouisBlues"
    # Winnipeg
    elif opponent == "52":
        return "@NHLJets"
    # Anaheim
    elif opponent == "24":
        return "@AnaheimDucks"
    # Arizona
    elif opponent == "53":
        return "@ArizonaCoyotes"
    # Calgary
    elif opponent == "20":
        return "@NHLFlames"
    # Edmonton
    elif opponent == "22":
        return "@EdmontonOilers"
    # Los Angeles
    elif opponent == "26":
        return "@LAKings"
    # San Jose
    elif opponent == "28":
        return "@SanJoseSharks"
    # Vancouver
    elif opponent == "23":
        return "@Canucks"
    #
    else:
        return "";

def GetOpponent(data):
    home = str(data['dates'][0]['games'][0]['teams']['home']['team']['id'])
    away = str(data['dates'][0]['games'][0]['teams']['away']['team']['id'])

    if home == "17":
        return TwitterHandleFromPK(away)
    else:
        return TwitterHandleFromPK(home)

def GetGameTime(data):
    d = datetime.datetime.strptime(data['dates'][0]['games'][0]['gameDate'], "%Y-%m-%dT%H:%M:%SZ")
    d = d + datetime.timedelta(hours=-5)
    return d.strftime("%I:%M%p EST")

def GetGdtTweetText(link):
    today = datetime.datetime.today().strftime("%Y-%m-%d")

    url = "https://statsapi.web.nhl.com/api/v1/schedule?season=20162017&teamId=17&startDate=" \
          + today + "&endDate=" + today


    response = requests.get(url)
    data = json.loads(response.content.decode("utf-8"))

    retStr = "Come discuss today's game!\r\n" + link + "\r\n@DetroitRedWings vs. {0} at {1} #RedWings #WingsGDT"
    retStr = retStr.replace("{0}", GetOpponent(data))
    retStr = retStr.replace("{1}", GetGameTime(data))

    print("got text: ", str(len(retStr)))

    return retStr

def IsGameToday():
    today = datetime.datetime.today().strftime("%Y-%m-%d")

    url = "https://statsapi.web.nhl.com/api/v1/schedule?season=20162017&teamId=17&startDate=" \
          + today + "&endDate=" + today

    response = requests.get(url)
    data = json.loads(response.content.decode("utf-8"))

    if data['totalGames'] > 0:
        return True
    else:
        return False

def PromoteGdtPost():
    r = praw.Reddit(user_agent="WingsHockeyMod (by /u/schmaleo505)")
    o = OAuth2Util.OAuth2Util(r)
    o.refresh(force=True)

    gdtLink = ""

    for post in r.get_redditor(user_name="OctoMod").get_submitted():
        if "Game Thread" in post.title and "Post" not in post.title:
            gdtLink = post.short_link
            break

    print("got gdt link, " + gdtLink)

    twitter = SetUpTwitter()
    print("twitter set")

    if gdtLink != "":
        twitter['api'].update_status(GetGdtTweetText(gdtLink))
        print("made post")



def GameTimeStream():
    today = datetime.datetime.today().strftime("%Y-%m-%d")

    url = "https://statsapi.web.nhl.com/api/v1/schedule?season=20162017&teamId=17&startDate=" \
          + today + "&endDate=" + today

    response = requests.get(url)
    data = json.loads(response.content.decode("utf-8"))

    pk = str(data['dates'][0]['games'][0]['gamePk'])

    print("Got game PK")

    twitter = SetUpTwitter()
    twitter_client = tweepy.API(twitter['auth_handler'])

    listener = PyStreamListener(twitter_client)
    stream = Stream(twitter['auth_handler'], listener)

    # Follow Khan before gametime
    print("Tweeting during game time")
    stream.filter(follow=["429897945", "16826656"], async=True)

    GameOver = False
    while not GameOver:
        feedUrl = "https://statsapi.web.nhl.com/api/v1/game/" + pk + "/feed/live"
        response = requests.get(feedUrl)
        data = json.loads(response.content.decode("utf-8"))

        if data['gameData']['status']['abstractGameState'] == 'Final':
            print("game over")
            listener.do_action = False
            GameOver = True

        time.sleep(10)




def StartStream():
    today = datetime.datetime.today().strftime("%Y-%m-%d")

    url = "https://statsapi.web.nhl.com/api/v1/schedule?season=20162017&teamId=17&startDate=" \
          + today + "&endDate=" + today

    response = requests.get(url)
    data = json.loads(response.content.decode("utf-8"))

    gameTime = datetime.datetime.strptime(data['dates'][0]['games'][0]['gameDate'], "%Y-%m-%dT%H:%M:%SZ")
    gameTime = gameTime - datetime.timedelta(hours=5)


    print("Got game time")


    twitter = SetUpTwitter()
    twitter_client = tweepy.API(twitter['auth_handler'])

    listener = PyStreamListener(twitter_client)
    stream = Stream(twitter['auth_handler'], listener)

    # Follow Khan before gametime
    print("started Khan RTer")
    stream.filter(follow=["429897945"], async=True)

    while gameTime > datetime.datetime.now:
        time.sleep(300)
    print("Action stopped")
    listener.do_action = False

    GameTimeStream()

if __name__ == '__main__':


    if IsGameToday():
        print("game today")
        PromoteGdtPost()
        StartStream()

