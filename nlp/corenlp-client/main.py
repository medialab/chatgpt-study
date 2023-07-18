import click

from tokenizer import stanza_annotations


@click.group()
@click.argument("datafile")
@click.pass_context
def cli(ctx, datafile):
    ctx.ensure_object(dict)
    ctx.obj["datafile"] = datafile


@cli.command("stanza")
@click.pass_context
def tokenize(ctx):
    stanza_annotations(ctx.obj["datafile"])


@cli.command("corenlp")
@click.pass_context
def corefs(ctx):
    print("corefs")


if __name__ == "__main__":
    cli(obj={})
