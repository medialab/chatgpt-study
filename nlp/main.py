import logging

import click
from pathlib import Path
from datetime import datetime
import os

from src import TwitterStanzaAnnotator
from src.constants import TWEET_STANZA_MAPPINGS
from src.utils import (
    create_client,
    scroll_index,
    search_document,
    setup_index,
    yield_data,
)

log_dir = Path("log")
log_dir.mkdir(exist_ok=True)
log_filename = log_dir.joinpath(
    "screen_{}_{}.log".format(os.getenv("STY"), datetime.utcnow())
).absolute()
logging.basicConfig(filename=log_filename, encoding="utf-8", level=logging.ERROR)


@click.group()
@click.option("--index", required=True)
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, index, debug):
    ctx.ensure_object(dict)
    ctx.obj["INDEX"] = index
    ctx.obj["DEBUG"] = debug


@cli.command("dep-parser")
@click.option("--datafile", required=True)
@click.option("--reverse", is_flag=True, show_default=True, default=False)
@click.option("--reset-index", is_flag=True, show_default=True, default=False)
@click.pass_context
def dep_parsing(ctx, datafile, reverse, reset_index):
    # Set up the database client and index
    index_name = ctx.obj["INDEX"]
    db_client = create_client()
    setup_index(
        client=db_client,
        index_name=index_name,
        reset=reset_index,
        mappings=TWEET_STANZA_MAPPINGS,
    )

    # Set up the NLP pipeline
    twitter_stanza_pipeline = TwitterStanzaAnnotator()

    # Annotate the Tweets and insert them into the database
    for data in yield_data(datafile=datafile, reverse=reverse):
        if isinstance(data, dict):
            # Determine if the Tweet is already in the database
            tweet_id = data["id"]
            tweet_text = data["text"]
            result = search_document(
                client=db_client, id=tweet_id, index_name=index_name
            )

            # If the Tweet is not in the database, annotate it and add it
            if not result:
                # Annotate the Tweet's text
                annotation = twitter_stanza_pipeline(tweet_text)
                data.update(annotation)

                # Try inserting the annotated Tweet into the index
                try:
                    db_client.index(index=index_name, body=data, id=tweet_id)
                except Exception as e:
                    logging.error(e)


if __name__ == "__main__":
    cli(obj={})  # type: ignore
