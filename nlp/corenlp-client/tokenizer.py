from typing import Generator

import stanza
from stanza.models.common.doc import Sentence
from stanza.pipeline.core import Pipeline

from utils import database_connection, yield_data

LANG = "en"
PROCESSORS = ",".join(
    [
        "tokenize",
        "mwt",  # only available for French and German
        "pos",
        "lemma",
        "depparse",
        "ner",
        "constituency",
    ]
)


def parse_sentences(text: str, nlp: Pipeline) -> Generator[Sentence, None, None]:
    # Parse the text
    doc = nlp(text)
    # Yield sentences from the parsed Document
    yield from doc.sentences


def pipeline_manager(text: str, pipeline: Pipeline) -> dict:
    # Prepare empty dictionary for document's "sentences" field
    sentences = {}
    # Prepare empty list for document's "text_tokenized" field
    tokenized_text = []

    # Loop through the stanza Sentence objects in the parsed text (Document)
    for sent in parse_sentences(text, pipeline):
        # Convert all the sentence's tokens to dictionaries
        tokens = sent.to_dict()
        # List all the tokens' text
        tokenized_text.append([t["text"] for t in tokens])
        # Pull out the sentence's ID
        sent_id = str(sent.sent_id)

        # Prepare empty dictionary for the sentence's "dependencies" field
        depedencies = {}
        for i, dep in enumerate(sent.dependencies):
            # Every dependency is a triple: Head, Deprel, Word
            # Note: database requires all keys are strings
            depedencies[str(i)] = {
                "head": dep[0].to_dict(),
                "deprel": dep[1],
                "word": dep[2].to_dict(),
            }

        # Add the sentence's "tokens" and "dependencies" fields
        sentences.update(
            {
                sent_id: {
                    "tokens": tokens,
                    "dependencies": depedencies,
                }
            }
        )

    # Return the document's metadata, which will be added to doc data
    return {"text_tokenized": tokenized_text, "sentences": sentences}


def stanza_annotations(datafile):
    # Set up the stanza pipeline
    stanza.download(LANG)
    nlp = stanza.Pipeline(lang=LANG, processors=PROCESSORS, use_gpu=True)

    # Set up the database connection
    collection = database_connection(
        collection_name="tweets-english-original", drop=True
    )

    # Insert enriched data into document database
    for data in yield_data(datafile=datafile):
        metadata = pipeline_manager(text=data["text"], pipeline=nlp)
        data.update(metadata)
        collection.insert_one(data)
