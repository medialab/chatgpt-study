# =============================================================================
# MongoDB Database Queries
# =============================================================================
#
# PyMongo commands to query a collection in a MongoDB database.
#
from pymongo.collection import Collection
import pymongo


def count_documents(collection: Collection):
    return collection.count_documents({})


def find_documents(collection: Collection, query: dict):
    for match in collection.find(query):
        yield match


def search_text(collection: Collection, keyword: str):
    text_index = "text_search_index"
    if not text_index in [index.get("name") for index in collection.list_indexes()]:
        print("Indexing text.")
        collection.create_index(
            [("text", pymongo.TEXT)],
            name=text_index,
            default_language="english",
        )
    query = {"$text": {"$search": keyword}}
    for match in collection.find(query):
        yield match
