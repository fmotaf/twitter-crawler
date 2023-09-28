import requests
import json
from bs4 import BeautifulSoup
from bs4.element import Comment
import tweepy
from decouple import config

API_KEY = config("API_KEY")
API_SECRET_KEY = config("API_SECRET_KEY")
ACCESS_TOKEN = config("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = config("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = config("BEARER_TOKEN")
CLIENT_ID = config("CLIENT_ID")
CLIENT_SECRET = config("CLIENT_SECRET")

auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# api = tweepy.API(auth)
api = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    bearer_token=BEARER_TOKEN
)

URL_1 = "https://www.motorsport.com/"
URL_2 = "https://www.planetf1.com/"

URL_3 = "https://www.formula1.com/"
URL_4 = "https://www.formula1points.com/"

### FUNCOES AUXILIARES
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def generate_dict(pilots:list):
    pilot_dict = dict(pilots)
    return dict((k,v) for k,v in pilot_dict.items())

def text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

DRIVERS_URL = "https://www.formula1.com/en/drivers"
ALEXANDER_ALBON = "https://www.formula1.com/en/drivers/alexander-albon.html"
IMG_CLASS = "image fom-image fom-adaptiveimage-fallback"
DRIVERS_STANDING_2023 = "https://www.formula1.com/en/results.html/2023/drivers"
def get_all_pilots(html):
    content = requests.get(html).text
    soup = BeautifulSoup(content, "html.parser")
    list_of_pilots = soup.find("div", attrs={"class": "container listing-items--wrapper driver during-season"}).find_all("a", attrs={"class":"listing-item--link"})
    
    all_pilots = []
    for pilot in list_of_pilots:
        pilot_obj = json.loads(pilot["data-tracking"])
        pilot_name = pilot_obj.get("path")
        pilot_codename = str(pilot["href"]).split("/drivers/")[1].split(".html")[0]
        pilot_callsign = str(pilot_name.split(' ')[0][:3]).upper() + str(pilot_name.split(' ')[1][:3]).upper() + str('01')
        # print("pilot_callsign")
        # print(pilot_callsign)
        all_pilots.append((pilot_name, pilot_codename, pilot_callsign))
    return all_pilots

### FUNCOES RELACIONADAS AO CRAWLING DA URL_3
def get_pilot_img(html, pilot_name):
    
    soup = BeautifulSoup(html, "html.parser")
    images = soup.find_all("img", attrs={"class":IMG_CLASS})
    
    for image in images:
        if "/drivers/" in image.get("src"):
            print(image)
            img_url = image.get("src")
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                with open("./media/img/"+pilot_name+".jpg","wb") as file:
                    file.write(img_response.content)
                    print(f"imagem salva!")
            else:
                print(f"Falha no download da imagem, Código de status = {img_response.status_code}")
        else:
            print("Nenhuma imagem do piloto foi encontrada!")

def get_pilot_results(html, pilot_name):

    soup = BeautifulSoup(html, "html.parser")
    table_title = soup.find("h1", attrs={"class": "ResultsArchiveTitle"})
    table_of_results = soup.find("table", attrs={"class": "resultsarchive-table"})
    table_head = table_of_results.find_next()
    table_body = table_head.find_next()
    table_rows = table_head.find_next()
    # for row in table_rows:
    #     print(row)
    print('table title')
    print(table_title.get_text().strip().rstrip().replace("\n",""))
    print('table body')
    print(table_body.get_text())
    print('table rows')
    race_obj = {}
    for row in table_rows:
        row_content = row.find_next()
        # print(row_content)
        for line in row_content:
            # if line != '\n':
            # race_obj["Grand Prix"] = 
            # race_obj["Date"] =
            # race_obj["Car"] =
            # race_obj["Race Position"] = 
            # race_obj["Pts"] =
            print(f"line = {line.get_text().split()}")
        # row_content = set(map(str, row_content.split()))
        # print(row_content)
    
    # print(table_body)
    # for row in table_body:
    #     print(row)
    # for row in table_of_results:
    #     print("NOVA LINHA")
    #     print(row.get_text().replace('\n',''))
    # print(table_of_results.get_text())

if __name__ == "__main__":

    pilots = get_all_pilots(DRIVERS_URL+".html")
    max_v = pilots[0][1]
    max_v_callsign = pilots[0][2]
    # print(DRIVERS_STANDING_2023+"/"+str(max_v_callsign)+"/"+str(max_v)+".html")
    # print("RESULTADOS DO PILOTO MAX VERSTAPPEN")
    get_pilot_results(requests.get(DRIVERS_STANDING_2023+"/"+str(max_v_callsign)+"/"+str(max_v)+".html").content, max_v)
    
    # for pilot in pilots:
    #     print(DRIVERS_URL+"/"+str(pilot[1])+".html")
    #     get_pilot_img(requests.get(DRIVERS_URL+"/"+str(pilot[1])+".html").content, pilot[1])

"""

# STANDINGS = "https://www.motorsport.com/f1/standings/2023/"
# STANDINGS = "https://www.formula1.com/en/results.html/2023/races.html"
STANDINGS = "https://www.formula1points.com/season"
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def get_standings(html):
    soup = BeautifulSoup(html, "html.parser")
    print(soup.find("table"))
    # texts = soup.findAll(text=True)
    # visible_texts = filter(tag_visible, texts)  
    # return u" ".join(t.strip() for t in visible_texts)

def get_better_standings(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    # Extract the table data
    rows = table.find_all("tr")
    # Extract header and data
    header = [th.text.strip() for th in rows[0].find_all("th")]
    data = [[td.text.strip() for td in row.find_all("td")] for row in rows[1:]]
    # Print the table
    print(header)
    for row in data:
        print(row)
    
    return str(data)

def post_standings(content: str):
    api.create_tweet(text = content)
    # .create_tweet(text=content)


def get_next_race_date_time():
    ...

if __name__ == "__main__":
    formula1_points = requests.get(URL_4).text
    get_standings(formula1_points)
"""


    # print(text_from_html(formula1_points))
    # response_standings = requests.get(STANDINGS).text
    # championship_standings = get_better_standings(response_standings)
    # post_standings(championship_standings)


    # print(text_from_html(response_standings))
    # print(get_standings(response_standings))
    
    #user_info = api.get_user(username="food_porn17")
    #print(user_info)

# for tweet in public_tweets:
#     print(tweet.text)
#     response1 = requests.get(URL_1).text
#     response2 = requests.get(URL_2).text

#     print(text_from_html(response1))
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