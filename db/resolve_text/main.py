import os
import sys
from pathlib import Path

import casanova
import click
import pandas as pd
import spacy
import torch
from ebbe import Timer
from fastcoref import spacy_component
from rich.progress import (
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

torch.set_num_threads(10)

"""
Performance Test

Cores: 10 (8 performance and 2 efficiency)
Memory: 32G
Chip: Apple M1 Pro

| threads | processes | chunksize | time (1k) | rate    | time (100k)
|   10    |     1     |    250    | 0:11:28   | 688s/1k | 19:01:40
---------------------------------------------------------------------
| threads | processes | chunksize | time (2k) | rate    | time (100k)
|   10    |     2     |    250    | 0:16:55   | 508s/1k | 14:06:39
---------------------------------------------------------------------
| threads | processes | chunksize | time (3k) | rate    | time (100k)
|   10    |     3     |    250    | 0:23:13   | 465s/1k | 12:54:59
---------------------------------------------------------------------
| threads | processes | chunksize | time (4k) | rate    | time (100k)
|   10    |     4     |    250    | 0:30:52   | 463s/1k | 12:51:39
"""

chunksize = 250

OUTDIR = Path("output")
OUTDIR.mkdir(exist_ok=True)


@click.command()
@click.option("--infile", required=True)
def main(infile):
    # Make outfile path
    infile_name = Path(infile).name
    outfile = OUTDIR.joinpath(infile_name)

    # Load SpaCy's English-language model, excluding most processors
    nlp = spacy.load(
        "en_core_web_lg", disable=["parser", "lemmatizer", "ner", "textcat"]
    )

    # Add FastCoref to the SpaCy pipeline
    nlp.add_pipe(
        "fastcoref",
        config={
            "model_architecture": "LingMessCoref",
            "model_path": "biu-nlp/lingmess-coref",
            "device": "cpu",  # mps not currently supported (see https://github.com/pytorch/rl/issues/1198)
        },
    )

    print("\nCounting file length...")
    file_length = casanova.reader.count(infile)

    base = round(file_length / chunksize)
    additional = file_length % chunksize
    if additional > 0:
        total_chunks = base + 1
    else:
        total_chunks = base

    # Use pandas to process chunks
    new_file = True
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        MofNCompleteColumn(),
        SpinnerColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as progress, Timer(file=sys.stdout):
        # Set up progress bar
        task = progress.add_task(
            "[bold blue]Processing chunks...\n", total=total_chunks
        )

        for chunk in pd.read_csv(infile, chunksize=chunksize, iterator=True):
            texts = chunk.text.to_list()

            # Resolve Tweet text coreferences
            docs = nlp.pipe(texts, component_cfg={"fastcoref": {"resolve_text": True}})
            resolved_texts = [doc._.resolved_text for doc in docs]

            # Add resolved texts to pandas dataframe
            chunk["text_resolved"] = resolved_texts

            # If starting anew, overwrite the file
            if new_file:
                mode = "w"
            else:
                mode = "a"

            # Write the dataframe chunk to the csv
            chunk.to_csv(outfile, header=True, mode=mode)

            # At the end of the loop, the file is no longer new
            new_file = False

            # Update progress bar
            progress.update(task, advance=1)

    os.system(f'say "Program has finished."')


if __name__ == "__main__":
    main()
