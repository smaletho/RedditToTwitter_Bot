import time
import datetime

def GetHoursOffUtc():
    if time.localtime().tm_isdst == 1:
        return 4
    else:
        return 5

def GetCurrentSeason():
    now = datetime.datetime.now()
    if now.month > 8:
        # this year and next
        return str(now.year) + str(now.year + 1)
    else:
        # last year and this one
        return str(now.year - 1) + str(now.year)
