import re
from contextlib import contextmanager
from typing import Generator

import stanza
from stanza.models.common.doc import Sentence
from stanza.pipeline.core import Pipeline
from stanza.server import CoreNLPClient

from utils import make_token_id

STANZA_PROCESSORS = ",".join(
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

CORENLP_ANNOTATORS = [
    "tokenize",  # Tell to tokenize on white space
    "ssplit",  # Tell to split sentences on \n\n
    "openie",
    "coref",
]


@contextmanager
def corenlp_client(*args, **kwargs):
    try:
        yield CoreNLPClient(
            annotators=CORENLP_ANNOTATORS,
            memory="4G",
            endpoint="http://localhost:9001",
            be_quiet=True,
        )
    except FileNotFoundError:
        stanza.install_corenlp()
        yield CoreNLPClient(
            annotators=CORENLP_ANNOTATORS,
            memory="4G",
            endpoint="http://localhost:9001",
            be_quiet=True,
        )


def flatten_text(nested_tokens: list[list[str]]) -> str:
    text = ""
    for sentence in nested_tokens:
        text += " ".join(sentence) + "\n\n"
    return text[:-2]


def parse_sentences(text: str, nlp: Pipeline) -> Generator[Sentence, None, None]:
    # Parse the text
    doc = nlp(text)
    # Yield sentences from the parsed Document
    yield from doc.sentences  # type: ignore


def stanza_annotation(nlp: Pipeline, text: str) -> dict:
    tokenized_text = []
    tokens = []
    depedencies = []
    clean_text = re.sub(r"@", "", text)
    clean_text = re.sub(r"#", "", clean_text)

    # Loop through the stanza Sentence objects in the parsed text (Document)
    for sent in parse_sentences(clean_text, nlp):
        # Pull out the sentence's ID
        sent_id = str(sent.sent_id)
        # Convert all the sentence's tokens to dictionaries
        sent_tokens = sent.to_dict()
        # List all the tokens' text
        tokenized_text.append([t["text"] for t in sent_tokens])
        # Add the sentence's tokens to the document's list of tokens
        for token in sent_tokens:
            token_id = token["id"]
            token.update(
                {
                    "sent_id": sent_id,
                    "doc_token_id": make_token_id(sent_id=sent_id, token_id=token_id),
                }
            )
            tokens.append(token)

        for dep in sent.dependencies:
            # Every dependency is a triple: Head, Deprel, Word
            head = dep[0].to_dict()
            dependency_relation = dep[1]
            word = dep[2].to_dict()

            head.update({"sent_id": sent_id})
            word.update(
                {
                    "sent_id": sent_id,
                    "doc_token_id": make_token_id(sent_id=sent_id, token_id=word["id"]),
                }
            )
            if head["id"] != 0:
                head.update(
                    {
                        "doc_token_id": make_token_id(
                            sent_id=sent_id, token_id=head["id"]
                        )
                    }
                )
            depedencies.append(
                {
                    "head": head,
                    "deprel": dependency_relation,
                    "word": word,
                }
            )

    # Return the document's metadata, which will be added to doc data
    return {
        "text_tokenized": tokenized_text,
        "tokens": tokens,
        "dependencies": depedencies,
    }


def parse_corefs(client: CoreNLPClient, text: str) -> tuple[list, dict]:
    doc = client.annotate(
        text,
        properties={
            "annotators": ",".join(CORENLP_ANNOTATORS),
            "outputFormat": "json",
            "triple.strict": "true",
            "tokenize.whitespace": "true",
            "spplit.newlineIsSentenceBreak": "two",
        },
    )
    sentences = doc.get("sentences")  # type: ignore
    corefs = doc.get("corefs")  # type: ignore
    return sentences, corefs


def corenlp_annotation(client: CoreNLPClient, document: dict) -> dict:
    # De-tokenize the tokenized text
    flattened_text = flatten_text(document["text_tokenized"])

    # Annotate the prepared text
    sentences, corefs = parse_corefs(client=client, text=flattened_text)

    openie_triples = []
    entity_mentions = []
    for n, sent in enumerate(sentences):
        openies = sent["openie"]
        for openie in openies:
            openie.update({"sentence": n + 1})
            openie_triples.append(openie)

        mentions = sent["entitymentions"]
        for mention in mentions:
            mention.update({"sentence": n + 1})
            entity_mentions.append(mention)

    document.update(
        {
            "corefs": corefs,
            "openieTriples": openie_triples,
            "entityMentions": entity_mentions,
        }
    )

    return document


def annotate(text: str, nlp_pipeline: Pipeline, nlp_client: CoreNLPClient) -> dict:
    output = {}

    stanza_layer = stanza_annotation(nlp=nlp_pipeline, text=text)
    output.update(stanza_layer)

    return corenlp_annotation(client=nlp_client, document=stanza_layer)
