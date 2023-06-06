# =============================================================================
# MongoDB Database Connection
# =============================================================================
#
# Command to connect to a cluster on remote MongoDB database.
#
from constants import CLUSTER
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def connection(user, password):
    uri = f"mongodb+srv://{user}:{password}@{CLUSTER}.ymcouvk.mongodb.net/?retryWrites=true&w=majority"
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi("1"))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        raise e
