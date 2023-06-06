# =============================================================================
# MongoDB Database CLI Actions
# =============================================================================
#
# Click CLI commands to interact with collection in MongoDB database.
#
import ast
import json

import click
from connect import connection
from constants import DATABASE, QUERY_RESULT, TWEET_DATE_FIELDS
from query import count_documents, find_documents


@click.group()
@click.option("--username", required=True)
@click.option("--password", required=True)
@click.option("--collection", required=True)
@click.pass_context
def cli(ctx, username, password, collection):
    client = connection(user=username, password=password)
    db = client[DATABASE]
    collection = db[collection]
    ctx.ensure_object(dict)
    ctx.obj["collection"] = collection


@cli.command()
@click.pass_context
def count(ctx):
    collection = ctx.obj["collection"]
    count = count_documents(collection=collection)
    print(f"Collection has {count} documents.")


@cli.command()
@click.option("--field")
@click.option("--value")
@click.pass_context
def find(ctx, field, value):
    collection = ctx.obj["collection"]
    try:
        value = ast.literal_eval(value)
    except:
        value = value
    print(f"Parsed the value as {type(value)}")
    query = {field: value}
    generator = find_documents(collection=collection, query=query)
    matches = [match for match in generator]
    print(f"{len(matches)} documents matched the query {query}.")
    write_output(data=matches)


def write_output(data: list):
    with open(QUERY_RESULT, "w") as of:
        output = {"items": [format_json_output(d) for d in data]}
        json.dump(output, of, indent=4, ensure_ascii=False)


def format_json_output(output: dict) -> dict:
    for field in TWEET_DATE_FIELDS:
        if output.get(field):
            output[field] = str(output[field])
    return output


if __name__ == "__main__":
    cli(obj={})
