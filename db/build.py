# =============================================================================
# MongoDB Database Construction
# =============================================================================
#
# Python script to connect to MongoDB database and create a cluster.
#
import json
from argparse import ArgumentParser

from connect import connection
from constants import DATABASE, TWEET_DATE_FIELDS
from dateutil import parser


def parse_dates(item: dict) -> dict:
    for field in TWEET_DATE_FIELDS:
        if item.get(field):
            item[field] = parser.parse(item[field])
    return item


def create_collection():
    # Connect to the MongoDB cluster with a username and password
    parser = ArgumentParser()
    parser.add_argument(
        "--username",
        required=True,
        help="Username that has access to the MongoDB cluster.",
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Password for the user account with access to the MongoDB cluster.",
    )
    parser.add_argument(
        "--datafile",
        required=True,
        help="Path to the JSON file that has data to be added to a new collection in the cluster.",
    )
    parser.add_argument(
        "--collection",
        required=True,
        help="Name of the collection to be added to the cluster.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        required=False,
        default=False,
        help="Flag permitting an existing cluster with the same given name to be overwritten with new data.",
    )
    args = parser.parse_args()
    client = connection(user=args.username, password=args.password)
    db = client[DATABASE]
    collection_name = args.collection

    # Create / connect to a database in the cluster
    if args.overwrite:
        # Remove any existing collection with the collection name
        db.drop_collection(collection_name)
    else:
        print(
            f"This collection already exists in the database. The data will not be overwritten."
        )
    # (Re)create the collection
    collection = db[collection_name]

    # Parse the data
    with open(args.datafile, "r") as f:
        data = json.load(f)
        if collection_name == "tweets":
            items = [parse_dates(item) for item in data["items"]]
        else:
            items = [item for item in data]

    # Insert the parsed data into the new collection
    collection.insert_many(items)


if __name__ == "__main__":
    create_collection()
