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

# ESSA PARTE SERA USADA APENAS PARA INTERAÇÃO COM TWITTER PORTANTO SERÁ DEIXADA DE LADO POR ENQUANTO
"""
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
"""

URL_3 = "https://www.formula1.com/"
URL_TO_WATCH = "https://www.band.uol.com.br/esportes/automobilismo/formula-1/ao-vivo"
TEAMS_URL = "https://www.formula1.com/en/teams.html"
DRIVERS_URL = "https://www.formula1.com/en/drivers"
IMG_CLASS = "image fom-image fom-adaptiveimage-fallback"
DRIVERS_STANDING_2023 = "https://www.formula1.com/en/results.html/2023/drivers"

# NO NEED TO CONNECT TO DB RIGHT NOW!!!
# db = Database().connect_db()

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
    db.insert_element(pilots_collection, pilot)

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
        pilot_obj = json.loads(pilot["data-tracking"])
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

    # print(date.split('T'))
    date_ = date.split('T')[0]
    time = date.split('T')[1]

    return (date_, time)

CALENDAR = "https://www.formula1.com/en/racing/2023.html"
BR_TIMEZONE = -3
def convert_utc_timezone(time, gmt_offset):

    # if int(gmt_offset) < BR_TIMEZONE:
    br_time = int(time) - (int(gmt_offset) - int(BR_TIMEZONE)) 
    # else:
    #     br_time = int(time) - (int(gmt_offset) + int(BR_TIMEZONE))
    return br_time % 24

def funcao(race_details, race_event:str):

    # print(f"race event = {race_event}")
    # print(race)
    schedule = race_details.find("div", attrs={"class":"f1-race-hub--timetable-listings"})    
    race = schedule.find("div", attrs={"class": f"row js-{race_event}"})
    if race:
        # event = race.attrs['class'][1].split('js-')[1].capitalize()
        start_day, start_time = date_parser(race["data-start-time"])
        gmt_offset = race["data-gmt-offset"]
        br_start_time = convert_utc_timezone(start_time.split(":")[0], gmt_offset.split(":")[0])
        minutes = start_time.split(":")[1]

        date_object = {
            # "Event":str(event),
            "Day":str(start_day),
            "Hour": f"{br_start_time}:{minutes}"
        }
        # print(date_object)
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
    today = datetime.date.today()

    races_obj = soup.find_all("script", attrs={"type":"application/ld+json"})
    # print(races_obj)

    next_race_dates = []
    for race in races_obj:
        race_info = json.loads(race.text)
        next_race_dates.append(race_info)

    for race in next_race_dates:
        url_ = race.get("@id")
        print(url_)
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


        # print(divs_with_prefix)
        # for div in divs_with_prefix:
        #     print(div)
            # print(10*'-')
            
        # print(race_details.find_all("div", attrs={"class": "row js-"}))
        
        if 'js-practice-3' in divs_with_prefix:
            print('1st Caaase')
            for race_event in ['race','qualifying','practice-3', 'practice-2', 'practice-1']:
                print(f"race event = {race_event}")
                funcao(race_details, race_event)
        else:
            print('2nd Case')
            for race_event in ['race', 'sprint', 'sprint-shootout', 'qualifying', 'practice-1']:
                print(f"race event = {race_event}")
                funcao(race_details, race_event)
    
    # start_time_br = start_time +  

    # for s in schedule:
    #     print(s)

    # print(race_details.find("div", attrs={"class":"row js-race"}))
    #find("div", attrs={"class":"f1-timetable--row f1-bg--white"}).find_parent().find_parent())

    ...
    
    """
    for race in races_obj:
        race_calendar = json.loads(race.text)
        print(race_calendar)
    
        start_time = race_calendar.get("startDate")
        end_time = race_calendar.get("endDate")

        fp_session_date = datetime.date(date_parser(start_time)[0])
        fp_session_time = date_parser(start_time)[1]
        start_time = (fp_session_date, fp_session_time)

        next_race_date = datetime.date(date_parser(end_time)[0])
        next_race_time = date_parser(end_time)[1]
        end_time = (next_race_date, next_race_time)
        
        race_date = (start_time, end_time)
        next_race_dates.append(race_date)
    """        
        
    # print("free practice time:")
    # print(fp_session_date, fp_session_time)

    # print("race time:")
    # print(next_race_date, next_race_time)
    """
    print(next_race_dates)
    return next_race_dates
    """

def main():
    crawl_next_race_dates(CALENDAR)

# APENAS COMO TESTE INSERE OS RESULTADOS EM UM EXCEL DE UM PILOTO
if __name__ == "__main__":
    main()

"""
TEAMS_URL_2 = "https://www.formula1.com/en/results.html/2023/team.html"
def crawl_teams(html):
    soup = utils.give_me_soup(html)
    teams_nicknames = soup.find("select", attrs={"name":"teamKey"})
    
    for team in teams_nicknames.find_all("option"):
        
        if team.get("value") != "all":
            print(team.get("value"))
"""