from pymongo import MongoClient
from dotenv import load_dotenv
import requests
import os


client:MongoClient|None = None

def connect_db():
    global client
    if client is None:
        client = MongoClient(os.getenv("MONGO_URI"))
    db = client.get_database("openf1_data")
    return db

def fetch_data(endpoint: str, params: dict) -> list:
    api_url = "https://api.openf1.org/v1"
    response = requests.get(api_url+endpoint, params)
    data = response.json()
    response.close()
    return data

def save_to_collection(data: list, collection_name: str, unique_keys: list):
    db = connect_db()
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