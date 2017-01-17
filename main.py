import TwitterKeys

import time
import tweepy
import praw
import OAuth2Util
import datetime
import requests
import json

def SetUpTwitter():
    auth = tweepy.OAuthHandler(TwitterKeys.consumer_key, TwitterKeys.consumer_secret)
    auth.set_access_token(TwitterKeys.access_token, TwitterKeys.access_secret)
    api = tweepy.API(auth)
    return api

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

    #url = "https://statsapi.web.nhl.com/api/v1/schedule?season=20162017&teamId=17&startDate=" \
          #+ today + "&endDate=" + today

    url = "https://statsapi.web.nhl.com/api/v1/schedule?season=20162017&teamId=17&startDate=2017-01-16&endDate=2017-01-16"

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



    if gdtLink != "":
        api = SetUpTwitter()
        print("twitter set")
        api.update_status(GetGdtTweetText(gdtLink))
        print("made post")
        # create twitter post


if __name__ == '__main__':

    # Ran each day at 10am
    PromoteGdtPost()

    if IsGameToday():
        PromoteGdtPost()
