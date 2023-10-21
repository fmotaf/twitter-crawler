## TWITTER-CRAWLER

### Desenvolvido como atividade durante curso de WebCrawler

### Detalhes do projeto
Trata-se de um bot que notifica quando irão acontecer as próximas corridas da temporada de 2023 e também mostra os resultados das corridas que já ocorreram


### Como executar:

#### Primeiro faça o clone do repositório

```
    git clone https://github.com/fmotaf/twitter-crawler.git
```
#### Caso esteja usando SSH

```
    git clone git@github.com:fmotaf/twitter-crawler.git
```

#### Após isso crie um amb. virtual e instale as dependências necessárias

```
    cd twitter-crawler
    python -m venv venv 
    <venv>\Scripts\activate.bat (Windows)
    source venv/bin/activate (Linux/MacOS)
    pip install -r requirements.txt
```
#### Finalmente para executar o crawler basta digitar:
` python src/main.py `
ou 
```
cd src
python main.py
```

