from datetime import date, datetime, timedelta, time
from sys import stdout

from data.api.twitter.TwitterClient import TwitterClient
from data.utils.parserUtil import PartiesTwitterParser

twitterClient = TwitterClient()
partiesTP = PartiesTwitterParser(filename='files/parties-config/parties-twitter.json')

def fetch_timeline_tweets():
    startdate = date(2017, 8, 28)
    enddate = date(2017, 10, 1)
    print("Saving tweets from " + str(startdate) + " to " + str(enddate))
    count = 0
    while startdate != datetime.now().date() and startdate != enddate:
        count += 1
        nextdate = startdate + timedelta(days=1)
        twitterClient.setStartDate(str(startdate))
        twitterClient.setEndDate(str(nextdate))
        stdout.write("\nStart date: " + str(startdate) + " -> Next date: " + str(nextdate))
        twitterClient.getTweetsAndSave()
        startdate = nextdate
    print("Finished saving tweets from " + str(count) + " days")

def fetch_party_tweets():
    for party in partiesTP.parties:
        print("\nGetting tweets from Party: " + party.pname + ", Username: " + party.pusername)
        twitterClient.setUsername(party.pusername)
        twitterClient.setStartDate(str(date(2010,1,1)))
        twitterClient.setEndDate(str(date(2017,9,30)))
        twitterClient.getTweetsAndSave()
        for user in party.pusers:
            print("\nGetting tweets from User: " + user.name)
            twitterClient.setUsername(user.username)
            twitterClient.setStartDate(None)
            twitterClient.getTweetsAndSave()

def fetch_tweets():
    #Get timeline tweets
    fetch_timeline_tweets()
    time.sleep(10)
    #Get party tweets
    fetch_party_tweets()


fetch_tweets()