import click

from tokenizer import stanza_annotations
from corefs import corenlp_annotations


@click.group()
@click.argument("collection")
@click.pass_context
def cli(ctx, collection):
    ctx.ensure_object(dict)
    ctx.obj["collection"] = collection


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
