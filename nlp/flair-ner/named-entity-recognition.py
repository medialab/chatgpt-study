# =============================================================================
# Flair NER Annotation
# =============================================================================
#
# Python script with CLI arguments to apply NER annotations to tweet data.
#
import json
from argparse import ArgumentParser

import casanova
import flair
from flair.data import Sentence
from flair.nn import Classifier
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from tweets import format_tweet


def clean(text: str) -> str:
    tokens_without_hashtags = " ".join(
        [token for token in text.split("#") if token != "#"]
    )
    tokens = [
        token
        for token in tokens_without_hashtags.split()
        if not token.startswith("@") and not token.startswith("http")
    ]
    doc = " ".join(tokens)
    return doc


def count_length_of_file(infile: str) -> int:
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), TimeElapsedColumn()
    ) as progress:
        task = progress.add_task("[red]Measuring file", total=None)
        total = casanova.reader.count(infile)
        progress.update(task_id=task, completed=1)
    return total


def format_ner_prediction(sentence: flair.data.Sentence):
    if sentence.annotation_layers:
        data_spans = [
            span.data_point
            for span in [
                ner_layer for ner_layer in sentence.annotation_layers.get("ner")
            ]
            if getattr(span, "data_point")
        ]
    else:
        data_spans = []
    tokens = [
        {
            "index": token.idx,
            "token": token.form,
            "start_position": token.start_position,
            "end_position": token.end_position,
        }
        for token in sentence.tokens
        if isinstance(token, flair.data.Token)
    ]
    annotations = [
        {
            "tag": span.tag,
            "text": span.text,
            "score": float(span.score),
            "start_position": span.start_position,
            "end_position": span.end_position,
        }
        for span in data_spans
        if isinstance(span, flair.data.Span)
    ]
    return tokens, annotations


def main():
    # Parse the CLI arguments
    parser = ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    infile = args.file

    # Get the total length of the CSV file
    total = count_length_of_file(infile)
    print(f"Detected a file with {total} documents.")

    # Set up a JSON object for the output
    output = {"items": []}

    # Load the flair NER Classifier
    print("Downloading the NER classifier.")
    tagger = Classifier.load("ner-large")

    # Process the CSV file with the NER pipeline
    with Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as progress, open(infile, "r") as f:
        reader = casanova.reader(f)
        fieldnames = reader.fieldnames
        task = progress.add_task("[green]NER analysis", total=total)
        for row, text in reader.cells("text", with_rows=True):
            # Clean the document's metadata
            data_dict = dict(zip(fieldnames, [cell for cell in row]))
            formatted_prediction = format_tweet(tweet_data=data_dict)
            # Remove CHATGPT and URLs from the document
            doc = clean(text)
            # Process the document with the flair NER classifier
            flair_sentence = Sentence(doc)
            tagger.predict(flair_sentence)
            # Format the NER prediction
            tokens, annotations = format_ner_prediction(flair_sentence)
            formatted_prediction.update(
                {
                    "annotations": annotations,
                    "tokens": tokens,
                }
            )
            # Add the prediction to the output array
            output["items"].append(formatted_prediction)
            progress.update(task, advance=1)

    # Dump all the NER anslyses into the out-file
    with open("ner-output.json", "w") as of:
        json.dump(output, of, indent=4)


if __name__ == "__main__":
    main()
