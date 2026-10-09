from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv
from requests import HTTPError
from datetime import datetime
import requests
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

client:MongoClient|None = None

def conectar_mongodb():
    logging.info("Conectando ao MongoDB...")
    global client
    if client is None:
        client = MongoClient(os.getenv("MONGO_URI"))
    db = client.get_database("cartola_fc_db")
    return db


def buscar_dados_mercado():
    logging.info("Buscando dados na API...")
    api_url = "https://api.cartola.globo.com/atletas/mercado"
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
    response.close()
    return data


def processar_e_gravar_dados(
        db:Database, dados_mercado:dict[str, dict]
        ):
    current_timestamp = datetime.now()
    logging.info("Gravando dados dos clubes...")
    clubes_collection = db["clubes_rodada_atual"]
    for clube in dados_mercado["clubes"].values():
        clubes_collection.update_one(
            {"_id": clube.pop("id")},
            {"$set": clube},
            upsert=True
        )

    logging.info("Gravando dados dos atletas...")
    atletas_collection = db["atletas_rodada_atual"]
    atletas_collection.delete_many({})
    atletas_list = [
        {
            **atleta, 
            "timestamp_coleta": current_timestamp
        } for atleta in dados_mercado["atletas"]
    ]

    atletas_collection.insert_many(atletas_list)

    logging.info("Gravando dados do mercado...")
    mercado_collection = db["mercado_rodada_atual"]
    mercado_collection.delete_many({})
    mercado_collection.insert_one({
        **dados_mercado["status"],
        "timestamp_coleta": current_timestamp
        }
    )

    logging.info("Finalizado com sucesso.")
    

def main():
    load_dotenv()

    db = conectar_mongodb()
    try: 
        dados = buscar_dados_mercado()
    except HTTPError:
        print("erro encontrado durante a consulta: "+str(HTTPError))
        return
    processar_e_gravar_dados(db, dados)


if __name__ == "__main__":
    main()