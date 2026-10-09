from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv
from requests import HTTPError
from datetime import datetime
import pandas as pd
import zipfile
import requests
import logging
import os
import io

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
    db = client.get_database("dados_saude")
    return db


def buscar_dados_ubs():
    logging.info("Buscando dados na API...")
    csv_url = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/CNES/Unidades_Basicas_Saude-UBS_csv.zip"
    response = requests.get(csv_url)
    response.raise_for_status()
    csv_file = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        with zip_file.open("Unidades_Basicas_Saude-UBS") as arquivo:
            df = pd.read_csv(arquivo)
            df["location"] = df.apply(
                lambda row: {
                    "type": "Point",
                    "coordinates": [
                        row["longitude"],
                        row["latitude"]
                    ]
                },
                axis=1
            )
            df = df.drop(columns=["latitude", "longitude"])

    data = df.to_dict(orient="records")
    response.close()
    return data


def processar_e_gravar_dados(
        db:Database, dados_ubs:list[dict]
        ):
    logging.info("Gravando dados na collection...")
    collection_ubs = db["geo_ubs"]
    collection_ubs.create_index(
        [("location", "2dsphere")],
        name="location_2dsphere"
    )
    collection_ubs.insert_many(dados_ubs)
    

def main():
    load_dotenv()

    db = conectar_mongodb()
    try: 
        dados = buscar_dados_ubs()
    except HTTPError:
        print("erro encontrado durante a consulta: "+str(HTTPError))
        return
    processar_e_gravar_dados(db, dados)


if __name__ == "__main__":
    main()