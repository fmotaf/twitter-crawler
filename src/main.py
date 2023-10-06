import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Comment
import tweepy
from decouple import config

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

### FUNCOES AUXILIARES
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

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

DRIVERS_URL = "https://www.formula1.com/en/drivers"
ALEXANDER_ALBON = "https://www.formula1.com/en/drivers/alexander-albon.html"
IMG_CLASS = "image fom-image fom-adaptiveimage-fallback"
DRIVERS_STANDING_2023 = "https://www.formula1.com/en/results.html/2023/drivers"

### FUNCOES RELACIONADAS AO CRAWLING DA URL_3

# ESSA FUNÇÃO RETORNA LISTA CONTENDO NOME DOS PILOTOS, CODENOME USADO NA URL
# E APELIDO TAMBÉM PARA SER COM OUTRO FORMATO DE URL
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


# BAIXA IMAGEM DO PILOTO DE ACORDO COM SEU NOME
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

# PEGA OS RESULTADOS DO PILOTO NA TEMPORADA 2023
def get_pilot_results(html, pilot_name):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="resultsarchive-table")

    first_row = table.findChild("thead")
    print(first_row.get_text().strip().split('\n'))

    excel_labels = first_row.get_text().strip().split('\n')
    
    excel_data = []
    for row in table.find_all("tr")[1:]:
        line = list(row.get_text().strip().split('\n'))
        print(line)
        for _ in line:
            if _ == "":
                print(60*"_")
                line.remove(_)
        print(line)
        excel_data.append(line)

    print(f"excel data ={excel_data}")
    return (excel_labels, excel_data)


# GERA UM EXCEL, A IDEIA É QUE SEJA GERADO UM EXCEL E SEJA POSTADO EM UM TWEET QUANDO O BOT FOR MENCIONADO
# EXEMPLO @RacingBot RESULTADO <PILOTO>, O NOME DO PILOTO ESTÁ HARDCODED MAS SERÁ ADICIONADO PARAM. A FUNÇÃO
def generate_excel(labels, rows):
    print(f"labels = {labels}, rows = {rows}")
    df = pd.DataFrame(rows, columns = labels)
    df.to_excel('verstappen.xlsx')

# APENAS COMO TESTE INSERE OS RESULTADOS EM UM EXCEL DE UM PILOTO
if __name__ == "__main__":

    pilots = get_all_pilots(DRIVERS_URL+".html")
    max_v = pilots[0][1]
    max_v_callsign = pilots[0][2]
    # print(DRIVERS_STANDING_2023+"/"+str(max_v_callsign)+"/"+str(max_v)+".html")
    # print("RESULTADOS DO PILOTO MAX VERSTAPPEN")
    labels, data = get_pilot_results(requests.get(DRIVERS_STANDING_2023+"/"+str(max_v_callsign)+"/"+str(max_v)+".html").content, max_v)
    generate_excel(labels, data)
    
    # for pilot in pilots:
    #     print(DRIVERS_URL+"/"+str(pilot[1])+".html")
    #     get_pilot_img(requests.get(DRIVERS_URL+"/"+str(pilot[1])+".html").content, pilot[1])


    # all_rows = table.children
    # for row in all_rows:
    #     print(row)
    
    # for row in table.children:
    #     print(row.text.strip)

    # print(f"first row = {first_row}")
    # for row in table:
    #     print(row.text.strip())
        