
import tweepy
from decouple import config

API_KEY = config("API_KEY")
API_SECRET_KEY = config("API_SECRET_KEY")
ACCESS_TOKEN = config("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = config("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.Client(auth)

user_info = api.get_user(username="food_porn17")
print(user_info)
# public_tweets = user_info.t

# for tweet in public_tweets:
#     print(tweet.text)


"""

import requests
from bs4 import BeautifulSoup

url = "https://twitter.com/food_porn17"
response = requests.get(url)
print(response.status_code)

if response.status_code == 200:
    # print(response.content)
    soup = BeautifulSoup(response.text, "html.parser")
    print(soup)
    # tweets = soup.find_all("div", class_="tweet")
    # for tweet in tweets:
    #     print(tweet)
    
        # tweet_text = tweet.find("p", class_="tweet-text").text
        # print(tweet_text)

    # print(response.cookies)
    # print(response.headers)
else:
    print("Failed!")
"""