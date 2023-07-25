import click
import stanza
import json

from annotator import STANZA_PROCESSORS, annotate, corenlp_client
from utils import create_client, yield_data, scroll_index


@click.group()
@click.option("--index-name", required=True)
@click.pass_context
def cli(ctx, index_name):
    ctx.obj["index"] = index_name


@cli.command("export")
@click.pass_context
def export(ctx):
    # Get index name
    index_name = ctx.obj["index"]

    # Establish connection to the database
    db_client = create_client(authentication=("admin", "admin"))

    # Pull all documents from the database
    output = []
    for _, entry in scroll_index(client=db_client, index=index_name):
        output.append(entry)

    print(f"Writing {len(output)} documents to 'export.json' file.")
    with open("export.json", "w") as of:
        json.dump(output, of, indent=4)


@cli.command("annotate")
@click.option("--datafile", required=True)
@click.option("--lang", required=False, default="en")
@click.option("--keep-index", is_flag=True, show_default=True, default=False)
@click.pass_context
def annotate_all(ctx, datafile, lang, keep_index):
    # Get index name
    index_name = ctx.obj["index"]

    # Establish a connection to the database
    db_client = create_client(authentication=("admin", "admin"))

    # (Re)create the index
    if not keep_index and db_client.indices.exists(index=index_name):
        db_client.indices.delete(index=index_name)
    if not db_client.indices.exists(index=index_name):
        index_body = {"settings": {"index": {"number_of_shards": 4}}}
        response = db_client.indices.create(index_name, body=index_body)
        print("\nCreating index")
        print(response)

    # Set up the NLP models
    with corenlp_client() as nlp_client:
        stanza.download(lang)
        nlp_pipeline = stanza.Pipeline(
            lang=lang, processors=STANZA_PROCESSORS, use_gpu=True
        )

        # Annotate the Tweets and insert in the database
        for data in yield_data(datafile=datafile):
            # Determine if the Tweet is already in the database
            doc_id = data["id"]
            response = db_client.search(
                body={"query": {"terms": {"_id": [doc_id]}}}, index=index_name
            )
            hits = response["hits"]["total"]["value"]

            # If not in the database, annotate it and add it
            if hits == 0 and data.get("text"):
                text = data["text"]
                annotation_layer = annotate(
                    text=text, nlp_pipeline=nlp_pipeline, nlp_client=nlp_client
                )

                data.update(annotation_layer)

                db_client.index(index=index_name, body=data, id=doc_id, refresh=True)


if __name__ == "__main__":
    cli(obj={})  # type: ignore
