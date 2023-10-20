import requests
import json
import tweepy
from decouple import config
import datetime
import dbase
from dbase import Database
import utils
from bs4 import BeautifulSoup
import re
import schedule

# ESSA PARTE SERA USADA APENAS PARA INTERAÇÃO COM TWITTER PORTANTO SERÁ DEIXADA DE LADO POR ENQUANTO
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
# api = tweepy.API(auth)


FORMULA1_URL = "https://www.formula1.com/"
URL_TO_WATCH = "https://www.band.uol.com.br/esportes/automobilismo/formula-1/ao-vivo"
TEAMS_URL = "https://www.formula1.com/en/teams.html"
DRIVERS_URL = "https://www.formula1.com/en/drivers"
IMG_CLASS = "image fom-image fom-adaptiveimage-fallback"
DRIVERS_STANDING_2023 = "https://www.formula1.com/en/results.html/2023/drivers"
CALENDAR = "https://www.formula1.com/en/racing/2023.html"
BR_TIMEZONE = -3
LINKS_TO_WATCH = ""

def insert_pilot(db:dbase.Database, pilot_data) -> None:
    """
        Parametros:
        db: Database conectada ao cluster MongoDb
        data:
    """
    pilots_collection = db.pilots
    pilot = {
        "Name": pilot_data[0],
        "URI1": pilot_data[1],
        "URI2": pilot_data[2]
    }
    pilot_id = pilots_collection.insert_one(pilot).inserted_id
    print(pilot_id)
    try:
        db.insert_element(pilots_collection, pilot)
    except Exception as e:
        print(e)

def insert_team(db:dbase.Database, team_data) -> None:
    teams_collection = db.teams
    team = {
        "Name": team_data[0],
        "Pilot1": team_data[1],
        "Pilot2": team_data[2],
        "Points": team_data[3]
    }
    db.insert_element(teams_collection, team)

def search_pilot(db:dbase.Database, pilot_name) -> None:
    pilots_collection = db.pilots
    query = pilots_collection.find_one({"Name": str(pilot_name)})
    print(query)

### FUNCOES RELACIONADAS AO CRAWLING DA URL_FORMULA1
def crawl_all_pilots(html) -> list:
    """
        Parametros:
            html: URL que possui os dados a serem raspados
        
        Retorna: 
            Lista contendo os pilotos
    """
    soup = utils.give_me_soup(html)
    list_of_pilots = soup.find("div", attrs={"class": "container listing-items--wrapper driver during-season"}).find_all("a", attrs={"class":"listing-item--link"})
    
    all_pilots = []
    for pilot in list_of_pilots:
        pilot_obj = json.loads(pilot["tdata-tracking"])
        pilot_name = pilot_obj.get("path")
        pilot_codename = str(pilot["href"]).split("/drivers/")[1].split(".html")[0]
        pilot_callsign = str(pilot_name.split(' ')[0][:3]).upper() + str(pilot_name.split(' ')[1][:3]).upper() + str('01')
        all_pilots.append((pilot_name, pilot_codename, pilot_callsign))
    
    return all_pilots

def crawl_all_teams(html:str) -> list:
    """
        Parametros:
            html: URL que possui os dados a serem raspados
        
        Retorna: 
            Lista contendo as equipes
    """
    soup = utils.give_me_soup(html)
    list_of_teams = soup.find("div", attrs={"class": "container listing team-listing"}).find_all("a", attrs={"class":"listing-link"})
    
    all_teams = []
    for team in list_of_teams:
        team_obj = json.loads(team["data-tracking"])
        team_name = team_obj.get("path")
        driver1 = team.find("div", attrs={"class": "driver"})
        driver1_name = driver1.get_text().strip().rstrip().replace('\n',' ')
        driver2 = driver1.findNext("div", attrs={"class": "driver"})
        driver2_name = driver2.get_text().strip().rstrip().replace('\n',' ')
        points = team.find("div", attrs={"class": "f1-wide--s"}).get_text().strip().rstrip().replace('\n',' ')
        team = {
            "Name": team_name,
            "Driver1": driver2_name,
            "Driver2": driver1_name,
            "Points": points
        }
        all_teams.append(team)
        print(all_teams)

    return all_teams

def insert_teams(html):
    soup = utils.give_me_soup(html)

# BAIXA IMAGEM DO PILOTO DE ACORDO COM SEU NOME
def crawl_pilot_img(html, pilot_name):
    """
        Baixa as imagens dos pilotos para exibicao quando alguem perguntar dados
        Parametros:
            html: URL que possui os dados a serem raspados
        
        Retorna: 
            Lista contendo as equipes
    """
    soup = utils.give_me_soup(html)
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

# PEGA OS RESULTADOS DO PILOTO NA TEMPORADA 2023
def crawl_pilot_results(html):
    soup = utils.give_me_soup(html)
    table = soup.find("table", class_="resultsarchive-table")

    first_row = table.findChild("thead")
    print(first_row.get_text().strip().split('\n'))

    excel_labels = first_row.get_text().strip().split('\n')
    
    excel_data = []
    for row in table.find_all("tr")[1:]:
        line = list(row.get_text().strip().split('\n'))
        for _ in line:
            if _ == "":
                line.remove(_)
        excel_data.append(line)

    print(f"excel data ={excel_data}")
    return (excel_labels, excel_data)

def date_parser(date:str):
    date_ = date.split('T')[0]
    time = date.split('T')[1]

    return (date_, time)

def convert_utc_timezone(time, gmt_offset):
    br_time = int(time) - (int(gmt_offset) - int(BR_TIMEZONE)) 
    return br_time % 24

def create_event_object(racetrack:str, race_details, race_event:str):
    schedule = race_details.find("div", attrs={"class":"f1-race-hub--timetable-listings"})    
    race = schedule.find("div", attrs={"class": f"row js-{race_event}"})
    if race:
        event = race.attrs['class'][1].split('js-')[1].capitalize()
        start_day, start_time = date_parser(race["data-start-time"])
        gmt_offset = race["data-gmt-offset"]
        br_start_time = convert_utc_timezone(start_time.split(":")[0], gmt_offset.split(":")[0])
        minutes = start_time.split(":")[1]

        date_object = {
            "Racetrack": racetrack,
            "Event":str(event),
            "Day":str(start_day),
            "Hour": f"{br_start_time}:{minutes}"
        }
        print(date_object)
        return date_object
    else:
        print(f'No race found!')

def start_with(div):
    return str(div.get("class")).startswith("row js-")

def crawl_next_race_dates(html):
    """
        Busca pelas datas das proximas corridas
        Parametros:
            html: URL que possui os dados a serem raspados
        
        Retorna: 
            Lista contendo as equipes    
    """
    soup = utils.give_me_soup(html)
    db = Database()

    races_obj = soup.find_all("script", attrs={"type":"application/ld+json"})

    next_race_dates = []
    for race in races_obj:
        race_info = json.loads(race.text)
        next_race_dates.append(race_info)

    for race in next_race_dates:
        racetrack = race.get("name")
        url_ = race.get("@id")
        print(url_)
        print(racetrack)
        race_details = utils.give_me_soup(url_)
        # race_details = BeautifulSoup(requests.get(url_).content, "html.parser")

        # divs_with_prefix = race_details.select('div[class^="row js-"]')
        all_divs = race_details.find_all("div")
        div_classes = []
        for div in all_divs:
            if div.get('class') is not None:
                div_classes.append(div.get('class'))
        # divs_with_prefix = [div for div in div_classes if 'js-' in div]
        divs_with_prefix = []
        for e in div_classes:
            # print(f'e={e}')
            for i in range(len(e)):
                if e[i].startswith('js-'):
                    divs_with_prefix.append(e[i])

        print(divs_with_prefix)

        if 'js-practice-3' in divs_with_prefix:
            print('1st Caaase')
            for race_event in ['race','qualifying','practice-3', 'practice-2', 'practice-1']:
                print(f"race event = {race_event}")
                new_event = create_event_object(racetrack, race_details, race_event)
                if db.search_element("events", new_event.get("Racetrack")) == None:
                    try:
                        db.insert_element("events", new_event)
                    except Exception as e:
                        print(e)       
                else:
                    print("evento ja inserido em banco")
        else:
            print('2nd Case')
            for race_event in ['race', 'sprint', 'sprint-shootout', 'qualifying', 'practice-1']:
                print(f"race event = {race_event}")
                new_event = create_event_object(racetrack, race_details, race_event)
                print(f"RACETRACK = {new_event.get('Racetrack')}")
                if db.search_element("events", new_event.get("Racetrack")) == None:
                    try:
                        db.insert_element("events", new_event)
                    except Exception as e:
                        print(e)     
                else:
                    print("evento ja inserido em banco")

def message_content():
    ...

def post_msg(bot:tweepy.Client):
    db = Database()
    today = datetime.datetime.today()
    events = db.search_all_elements("events")
    # print(events)

    event = events[0]
    # for event in events:
    print(event)
        # print(event["Day"].replace('-',','))
    year = int(event["Day"].split('-')[0])
    month = int(event["Day"].split('-')[1])
    day = int(event["Day"].split('-')[2])
    new_datetime = datetime.datetime(year, month, day)
    delta = new_datetime - today
    print(delta.days)
        
    if delta.days < 0:    
        try:
            msg = f"A corrida {event} aconteceu há {delta.days} dias!"
            print(msg)
            bot.create_tweet(text=msg)
        except tweepy.TwitterServerError as e:
                print(f'Erro: {e}')
    else:
        try:
            msg = f"A corrida {event} vai acontecer em {delta.days} dias!\nConfira aqui os links para assistir:\n{LINKS_TO_WATCH}"
            print(msg)
            bot.create_tweet(text=msg)
        except tweepy.TwitterServerError as e:
            print(f'Erro: {e}')


# def job():
#     schedule.every(1).minutes.do(job)    
#     # api.create_tweet(text)
#     ...
    

def main():
    # crawl_next_race_dates(CALENDAR)
    post_msg(bot=client)

# APENAS COMO TESTE INSERE OS RESULTADOS EM UM EXCEL DE UM PILOTO
if __name__ == "__main__":
    main()
