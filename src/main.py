import requests
import json
import tweepy
from decouple import config
import datetime
import dbase
from dbase import Database
import utils


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

db = Database.connect_db()

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

### FUNCOES RELACIONADAS AO CRAWLING DA URL_3
def crawl_all_pilots(html) -> list:
    """
        Parametros:
            html: URL que possui os dados a serem raspados
        
        Retorna: 
            Lista contendo os pilotos
    """

    soup = utils.return_soup(html)
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

    soup = utils.return_soup(html)
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
        # all_teams.append(team)
        # print(team_name)

# BAIXA IMAGEM DO PILOTO DE ACORDO COM SEU NOME
def crawl_pilot_img(html, pilot_name):
    """
        Baixa as imagens dos pilotos para exibicao quando alguem perguntar dados
        Parametros:
            html: URL que possui os dados a serem raspados
        
        Retorna: 
            Lista contendo as equipes
    """

    soup = utils.return_soup(html)
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
    soup = utils.return_soup(html)
    table = soup.find("table", class_="resultsarchive-table")

    first_row = table.findChild("thead")
    print(first_row.get_text().strip().split('\n'))

    excel_labels = first_row.get_text().strip().split('\n')
    
    excel_data = []
    for row in table.find_all("tr")[1:]:
        line = list(row.get_text().strip().split('\n'))
        # print(line)
        for _ in line:
            if _ == "":
                line.remove(_)
        # print(line)
        excel_data.append(line)

    print(f"excel data ={excel_data}")
    return (excel_labels, excel_data)

# PEGA AS DATAS DE TODOS AS PROXIMAS PROVAS
def crawl_next_races(html):
    soup = utils.return_soup(html)
    today = datetime.datetime.today()
    
    races_obj = soup.find_all("script", attrs={"type":"application/ld+json"})
    next_race_dates = []
    for race in races_obj:
        race_calendar = json.loads(race.text)
        next_race_dates.append(race_calendar.get("startDate"))
        start_time = race_calendar.get("startDate")
        end_time = race_calendar.get("endDate")
    
    print("start time")
    print(start_time)
    print("end time")
    print(end_time)

def crawl_race_results(html):
    ...

"""
def main():
    list_of_pilots = get_all_pilots(DRIVERS_URL+".html")

    # for pilot in list_of_pilots:
        # print(pilot)
        # print(DRIVERS_STANDING_2023+str(pilot[2])+".html")
        # pilot_result = get_pilot_results(DRIVERS_STANDING_2023+"/"+str(pilot[2])+".html")
        # print(pilot_result)
        
    # INSERE DADOS DO PILOTO NO BANCO
    db = connect_db()
        
    # insert_pilot(db, pilot)

    # PROCURA POR PILOTO/ EXEMPLO MAX VERSTAPPEN
    search_pilot(db, "Max Verstappen")
"""

def main():
    print(TEAMS_URL)
    crawl_all_teams(TEAMS_URL)

"""
SCHEDULE_URL = "https://www.formula1.com/en/racing/2023.html"
def main():
    get_next_races(SCHEDULE_URL)
"""

# APENAS COMO TESTE INSERE OS RESULTADOS EM UM EXCEL DE UM PILOTO
if __name__ == "__main__":
    main()