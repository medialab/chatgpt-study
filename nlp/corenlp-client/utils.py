import casanova  # pip install casanova
import csv
import json
import pymongo  # pip install pymongo
from tqdm import tqdm
from pymongo.collection import Collection
from typing import Generator

CONFIG = "config.json"


def yield_data(datafile) -> Generator[dict, None, None]:
    print("counting data file length...")
    total = casanova.reader.count(datafile)
    with open(datafile, "r") as f:
        reader = csv.DictReader(f)
        for row in tqdm(
            reader,
            total=total,
            desc="Processing documents...",
        ):
            yield row


def database_connection(collection_name: str, drop: bool = False) -> Collection:
    print("connecting to database...")
    with open(CONFIG, "r") as f:
        config = json.load(f)
        connection_URI = config["mongo"]["connection string URI"]
    client = pymongo.MongoClient(connection_URI)
    db = client.chatgpt
    if drop:
        db.drop_collection(collection_name)
    return db[collection_name]
