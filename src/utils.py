"""
    Módulo contendo funções auxiliares para o crawler
"""
from bs4 import BeautifulSoup
from bs4.element import Comment
import pandas as pd
import requests

def return_soup(html) -> BeautifulSoup:
    """
        Parametros:
            html: URL que possui os dados a serem raspados
        
        Retorna: 
            Elemento BeautifulSoup
    """
    content = requests.get(html).text
    soup = BeautifulSoup(content, "html.parser")
    return soup

# GERA UM EXCEL, A IDEIA É QUE SEJA GERADO UM EXCEL E SEJA POSTADO EM UM TWEET QUANDO O BOT FOR MENCIONADO
# EXEMPLO @RacingBot RESULTADO <PILOTO>, O NOME DO PILOTO ESTÁ HARDCODED MAS SERÁ ADICIONADO PARAM. A FUNÇÃO
def generate_excel(labels, rows, pilot_name='all_pilots'):
    print(f"labels = {labels}, rows = {rows}")
    df = pd.DataFrame(rows, columns = labels)
    df.to_excel(f"{pilot_name}.xlsx")

# GERA UM GRAFICO PARA PODER SER POSTADO NO TWITTER CONTENDO OS RESULTADOS DO PILOTO
def generate_graph():
    ...


# NAO ESTAO SENDO USADAS
"""
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

"""