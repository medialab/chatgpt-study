import click

from annotators.stanza import TwitterStanzaAnnotator
from annotators.coref import FastCorefAnnotator
from constants import TWEET_MAPPINGS, COREF_MAPPINGS
from utils import create_client, search_document, setup_index, yield_data, scroll_index
import logging
import casanova
from tqdm import tqdm
import sys
import io
import contextlib
import os


class IndexNameFormatter:
    def __init__(self, name: str) -> None:
        self.tweets = name
        self.corefs = self.tweets + "-corefs"
        self.deps = self.tweets + "-deps"


@click.group()
@click.option("--index-name", required=True)
@click.option("--reset-index", is_flag=True, show_default=True, default=False)
@click.pass_context
def cli(ctx, index_name, reset_index):
    client = create_client()
    setup_index(
        client=client,
        index_name=index_name,
        reset=reset_index,
        mappings=TWEET_MAPPINGS,
    )
    ctx.obj["client"] = client
    ctx.obj["index_name"] = IndexNameFormatter(name=index_name)


@cli.command("import")
@click.option("--datafile", required=True)
@click.option("--reverse", is_flag=True, show_default=True, default=False)
@click.pass_context
def import_all(ctx, datafile, reverse):
    client = ctx.obj["client"]
    index_name = ctx.obj["index_name"]

    for document in yield_data(datafile=datafile, reverse=reverse):
        doc_id = document["id"]  # type:ignore
        found_document = search_document(
            client=client, id=doc_id, index_name=index_name.tweets
        )
        if not found_document:
            client.index(index=index_name.tweets, body=document, id=doc_id)


@cli.command("corefs")
@click.option("--reset-index", is_flag=True, show_default=True, default=False)
@click.pass_context
def corefs(ctx, reset_index):
    print("\nInitiating FastCoref...")
    nlp = FastCorefAnnotator()

    client = ctx.obj["client"]
    index_name = ctx.obj["index_name"]
    setup_index(
        client=client,
        index_name=index_name.corefs,
        reset=reset_index,
        mappings=COREF_MAPPINGS,
    )

    import csv

    with open("resolved_tweet_text.csv", "w") as outfile:
        writer = csv.writer(outfile)
        fieldnames = list(TWEET_MAPPINGS["properties"].keys()) + ["text_resolved"]
        writer.writerow(fieldnames)

        for batch in scroll_index(client=client, index=index_name.tweets):
            docs = [
                doc["_source"]
                for doc in batch
                # if not search_document(
                #     client=client, id=doc["_source"]["id"], index_name=index_name.corefs
                # )
            ]
            texts = nlp(texts=[doc["text"] for doc in docs])

            batch_rows = []
            for doc, text in list(zip(docs, texts)):
                row = list(doc.values()) + [text]
                batch_rows.append(row)

            writer.writerows(batch_rows)


@cli.command("dependencies")
@click.option("--lang", required=False, default="en")
@click.option("--datafile", required=True)
@click.option("--reverse", is_flag=True, show_default=True, default=False)
@click.option("--reset-index", is_flag=True, show_default=True, default=False)
@click.pass_context
def dependencies(ctx, lang, datafile, reverse, reset_index):
    client = ctx.obj["client"]
    index_name = ctx.obj["index_name"]
    setup_index(
        client=client,
        index_name=index_name.tokens,
        reset=reset_index,
        mappings=TWEET_MAPPINGS,
    )

    stanza_annotator = TwitterStanzaAnnotator()

    for doc_id in yield_data(datafile=datafile, reverse=reverse, single_column="id"):
        found_document = search_document(
            client=client, id=doc_id, index_name=index_name.tweets  # type:ignore
        )
        found_annotation = search_document(
            client=client, id=doc_id, index_name=index_name.tokens  # type:ignore
        )
        if found_document and not found_annotation:
            doc = found_document.copy()
            tweet_text = doc["text"]
            stanza_annotation = stanza_annotator(tweet_text)
            doc.update(stanza_annotation.asdict())
            try:
                client.index(index=index_name.tokens, body=doc, id=doc_id)
            except Exception as e:
                from pprint import pprint

                pprint(doc)
                raise e


if __name__ == "__main__":
    cli(obj={})  # type: ignore
