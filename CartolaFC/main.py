from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv
from requests import HTTPError
from datetime import datetime
import requests
import os


client:MongoClient|None = None

def conectar_mongodb():
    global client
    if client is None:
        client = MongoClient(os.getenv("MONGO_URI"))
    db = client.get_database("cartola_fc_db")
    return db

def buscar_dados_mercado():
    api_url = "https://api.cartola.globo.com/atletas/mercado"
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
    response.close()
    return data

def processar_e_gravar_dados(
        db:Database, dados_mercado:dict[str, dict]
        ):
    clubes_data = dados_mercado["clubes"]
    clubes_collection = db["clubes_rodada_atual"]
    for clube in clubes_data.values():
        clubes_collection.update_one(
            {"id": clube.pop("id")},
            {"$set": clube},
            upsert=True
        )

    atletas_data = dados_mercado["atletas"]
    atletas_collection = db["atletas_rodada_atual"]
    atletas_collection.delete_many({})
    atletas_list = []
    current_timestamp = 

    for atleta in atletas_data.values():
        atleta
        atletas_collection.update_one(
            {"id": atleta.pop("id")},
            {"$set": {**atleta, }},
            upsert=True
        )

    atletas_data = dados_mercado["atletas"]

    collection = db[collection_name]
    for item in data:
        unique_params = {key: item.pop(key) for key in unique_keys}
        collection.update_one(
            unique_params,
            {"$set": item},
            upsert=True
        )

def main():
    load_dotenv()

    session = fetch_data("/sessions", {"session_key": 9159})
    drivers = fetch_data("/drivers", {"session_key": 9159})
    laps = fetch_data("/laps", {"session_key": 9159})

    save_to_collection(session, "sessions", ["session_key"])
    save_to_collection(drivers, "drivers", ["session_key", "driver_number"])
    save_to_collection(laps, "laps", ["session_key", "driver_number", "lap_number"])


if __name__ == "__main__":
    main()