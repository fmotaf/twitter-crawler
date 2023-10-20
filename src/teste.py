import tweepy
from decouple import config
# import os
# from dotenv import load_dotenv

bearer_token = config("BEARER_TOKEN")
consumer_key = config("API_KEY")
consumer_secret = config("API_SECRET_KEY")
access_token = config("ACCESS_TOKEN")
access_token_secret = config("ACCESS_TOKEN_SECRET")

# print(consumer_key, type(consumer_key))
# print(consumer_secret, type(consumer_secret))
print(access_token, type(access_token))
print(access_token_secret, type(access_token_secret))

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

try:
    api = tweepy.API(auth)
    api.verify_credentials()
    client.create_tweet(text="Olá")
    print("Authentication OK")

except tweepy.TwitterServerError as e:
    print(f"Error: {e}")

# public_tweets = api.home_timeline()
# for tweet in public_tweets:
#     print(tweet.text)


# auth = tweepy.OAuth1UserHandler(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)
# auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
# auth = tweepy.OAuth2BearerHandler(BEARER_TOKEN)
# api = tweepy.API(auth)
# client.create_tweet(text="Olá")