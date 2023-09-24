import requests
from bs4 import BeautifulSoup
from bs4.element import Comment

URL_2 = "https://www.planetf1.com/"
URL_1 = "https://www.motorsport.com/"

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

if __name__ == "__main__":

    response1 = requests.get(URL_1).text
    response2 = requests.get(URL_2).text

    print(text_from_html(response1))
    # text_from_html(response2)

# bs1 = BeautifulSoup(response1.text)
# bs2 = BeautifulSoup(response2.text, 'html.parser')
# texts = bs2.find_all(text=True)
# visible_texts = filter(tag_visible, texts)
# print(texts)
# print(u" ".join(t.strip() for t in visible_texts))
# print(bs2.find("body"))




"""
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