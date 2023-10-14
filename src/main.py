import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Comment
import tweepy
from decouple import config
from pymongo import MongoClient
from pymongo import database


uri:str = config("MONGO_URI")
client:MongoClient = MongoClient(uri)

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
URL_4 = "https://www.formula1points.com/"

DRIVERS_URL = "https://www.formula1.com/en/drivers"
ALEXANDER_ALBON = "https://www.formula1.com/en/drivers/alexander-albon.html"
IMG_CLASS = "image fom-image fom-adaptiveimage-fallback"
DRIVERS_STANDING_2023 = "https://www.formula1.com/en/results.html/2023/drivers"


### FUNCOES AUXILIARES
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

# CONECTA AO BANCO DE DADOS
def connect_db() -> database.Database:
    try:
        client.admin.command("ping")
        print("Succesfully deployed your MongoDB Cluster")
        db = client['formula1_db']
    except Exception as e:
        print(e)
    return db

def insert_pilot(db:database.Database, pilot_data) -> None:
    pilots_collection = db.pilots
    pilot = {
        "Name": pilot_data[0],
        "URI1": pilot_data[1],
        "URI2": pilot_data[2]
    }
    pilot_id = pilots_collection.insert_one(pilot).inserted_id
    print(pilot_id)

"""
def insert_team(db:database.Database, team_data) -> None:
    teams_collection = db.teams
    team = {
        "Name":,
        "Pilot1":,
        "Pilot2":,
    }
    team_id = teams_collection.insert_one(team).inserted_id
"""

def search_pilot(db:database.Database, pilot_name) -> None:
    pilots_collection = db.pilots
    query = pilots_collection.find_one({"Name": str(pilot_name)})
    print(query)

# GERA UM DICIONÁRIO DE PILOTOS
def generate_dict(pilots:list):
    pilot_dict = dict(pilots)
    return dict((k,v) for k,v in pilot_dict.items())

# EXTRAI TEXTO DE HTML, NÃO SERÁ USADA POR ENQUANTO
def text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

# Retorna Um elemento BeautifulSoup, função auxiliar parr
def return_soup(html) -> BeautifulSoup:
    content = requests.get(html).text
    soup = BeautifulSoup(content, "html.parser")
    return soup

### FUNCOES RELACIONADAS AO CRAWLING DA URL_3

# ESSA FUNÇÃO RETORNA LISTA CONTENDO NOME DOS PILOTOS, CODENOME USADO NA URL
# E APELIDO TAMBÉM PARA SER COM OUTRO FORMATO DE URL
def get_all_pilots(html):
    soup = return_soup(html)
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

TEAMS_URL = "https://www.formula1.com/en/teams.html"
def get_all_teams(html) -> None:
    soup = return_soup(html)
    list_of_teams = soup.find("div", attrs={"class": "container listing team-listing"}).find_all("a", attrs={"class":"listing-link"})
    
    all_teams = []
    for team in list_of_teams:
        team_obj = json.loads(team["data-tracking"])
        team_name = team_obj.get("path")
        # print(team_obj)
        driver1 = team.find("div", attrs={"class": "driver"})
        driver1_name = driver1.get_text().strip().rstrip().replace('\n',' ')
        driver2 = driver1.findNext("div", attrs={"class": "driver"})
        driver2_name = driver2.get_text().strip().rstrip().replace('\n',' ')

        team = {
            "Name": team_name,
            "Driver1": driver2_name,
            "Driver2": driver1_name
        }
        all_teams.append(team)
    
    for team in all_teams:
        print(team)

        # all_teams.append(team)
        # print(team_name)

# BAIXA IMAGEM DO PILOTO DE ACORDO COM SEU NOME
def get_pilot_img(html, pilot_name):
    soup = return_soup(html)
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
def get_pilot_results(html):
    soup = return_soup(html)
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

# GERA UM EXCEL, A IDEIA É QUE SEJA GERADO UM EXCEL E SEJA POSTADO EM UM TWEET QUANDO O BOT FOR MENCIONADO
# EXEMPLO @RacingBot RESULTADO <PILOTO>, O NOME DO PILOTO ESTÁ HARDCODED MAS SERÁ ADICIONADO PARAM. A FUNÇÃO
def generate_excel(labels, rows, pilot_name='all_pilots'):
    print(f"labels = {labels}, rows = {rows}")
    df = pd.DataFrame(rows, columns = labels)
    df.to_excel(f"{pilot_name}.xlsx")

# GERA UM GRAFICO PARA PODER SER POSTADO NO TWITTER CONTENDO OS RESULTADOS DO PILOTO
def generate_graph():
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
    get_all_teams(TEAMS_URL)

# APENAS COMO TESTE INSERE OS RESULTADOS EM UM EXCEL DE UM PILOTO
if __name__ == "__main__":
    main()