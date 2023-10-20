from decouple import config
from pymongo import MongoClient
from pymongo import database

class Database():
    def __init__(self) -> None:
        self.uri:str = config("MONGO_URI")
        self.client:MongoClient = MongoClient(self.uri)
        self.db = self.connect_db()

    # CONECTA AO BANCO DE DADOS
    def connect_db(self) -> database.Database:
        """
            Realiza conexao com banco de dados
        """
        try:
            self.client.admin.command("ping")
            print("Succesfully deployed your MongoDB Cluster")
            db = self.client['formula1_db']
        except Exception as e:
            print(e)
        return db

    # INSERE ELEMENTO NO BANCO
    def insert_element(self, collection:str, element) -> None:
        """
            collection: Colecao a ser inserida (piloto, time)
            element: Elemento a ser inserido (piloto, time)
        """
        # element_collection = self.db.collection
        element_id = self.db[collection].insert_one(element).inserted_id
        print(f"elemento {element_id} inserido na coleção {collection}")

    # BUSCA POR ELEMENTO NO BANCO
    def search_element(self, collection:str , element) -> None:
        query = self.db[collection].find_one({"Name": str(element)})
        if query:
            print(query)
        else:
            print("Nao foi encontrado nenhum elemento que satisfaz sua busca!")
            return None