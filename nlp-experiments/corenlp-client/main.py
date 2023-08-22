import click

from tokenizer import stanza_annotations
from corefs import corenlp_annotations


@click.group()
@click.option("--collection-name", required=True, help="collection name in database")
@click.pass_context
def cli(ctx, collection_name):
    ctx.ensure_object(dict)
    ctx.obj["collection"] = collection_name


@cli.command("stanza")
@click.argument("datafile")
@click.pass_context
def tokenize(ctx, datafile):
    stanza_annotations(collection_name=ctx.obj["collection"], datafile=datafile)


@cli.command("corenlp")
@click.pass_context
def corefs(ctx):
    corenlp_annotations(ctx.obj["collection"])


if __name__ == "__main__":
    cli(obj={})
