import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

DB_URI = os.getenv("DB_URI")
DB_NAME = "hydrolab-database-v0"

info_bins_path_json = "./data/infobins.json"
info_grid_path_json = "./data/infogrid.json"
info_splited_data_json = "./data/spliteddata.json"
info_pairing_data_json = "./data/pairingdata.json"
info_all_data_json = "./data/metadata.json"
statistical_data_json = "./data/statisticaldata.json"


def load_file_json(data_path):
    datafile = None

    try:
        with open(data_path, "r") as file:
            datafile = json.load(file)

    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
    
    return datafile


info_bins_path = load_file_json(info_bins_path_json)
info_grid_path = load_file_json(info_grid_path_json)
info_splited_data = load_file_json(info_splited_data_json)
info_pairing_data = load_file_json(info_pairing_data_json)
info_all_data = load_file_json(info_all_data_json)
statistical_data = load_file_json(statistical_data_json)


client = MongoClient(DB_URI)
client


client.list_database_names()


db = client[DB_NAME]
db

db.list_collection_names()

db["bins"].delete_many({})
db["bins"].insert_one(info_bins_path)

db["grid"].delete_many({})
db["grid"].insert_one(info_grid_path)

db["splitted"].delete_many({})
db["splitted"].insert_one(info_splited_data)

db["stations"].delete_many({})
db["stations"].insert_many(info_all_data)

db["pairings"].delete_many({})
db["pairings"].insert_many(info_pairing_data)

db["statistics"].delete_many({})
db["statistics"].insert_many(statistical_data)
