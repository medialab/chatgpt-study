from contextlib import contextmanager
from tqdm import tqdm

import stanza
from stanza.server import CoreNLPClient

from utils import database_connection

ANNOTATORS = [
    "tokenize",  # Tell to tokenize on white space
    "ssplit",  # Tell to split sentences on \n\n
    "openie",
    "coref",
]


def flatten_text(nested_tokens: list[list[str]]) -> str:
    text = ""
    for sentence in nested_tokens:
        text += " ".join(sentence) + "\n\n"
    return text[:-2]


@contextmanager
def client_manager(*args, **kwargs):
    try:
        yield CoreNLPClient(
            annotators=ANNOTATORS,
            memory="4G",
            endpoint="http://localhost:9001",
            be_quiet=True,
        )
    except FileNotFoundError:
        stanza.install_corenlp()
        yield CoreNLPClient(
            annotators=ANNOTATORS,
            memory="4G",
            endpoint="http://localhost:9001",
            be_quiet=True,
        )


def client_annotation(client: CoreNLPClient, text: str) -> tuple[list, dict]:
    doc = client.annotate(
        text,
        properties={
            "annotators": ",".join(ANNOTATORS),
            "outputFormat": "json",
            "triple.strict": "true",
            "tokenize.whitespace": "true",
            "spplit.newlineIsSentenceBreak": "two",
        },
    )
    sentences = doc.get("sentences")
    corefs = doc.get("corefs")
    return sentences, corefs


def corenlp_annotations(collection_name) -> None:
    # Set up the database connection
    collection = database_connection(collection_name=collection_name)

    print("getting indexed document IDs...")
    doc_ids = [d["_id"] for d in collection.find()]

    # Iterate through documents in the database collection
    with client_manager() as client:
        for doc_id in tqdm(doc_ids, total=len(doc_ids)):
            # Get the indexed document
            document = collection.find_one({"_id": doc_id})
            document.update({"corefs": {}})

            # Get the tokenized text produced during phase 1 (stanza)
            text = document.get("text_tokenized")

            # De-tokenize the tokenized text
            flattened_text = flatten_text(text)

            # Annotate the prepared text
            sentences, corefs = client_annotation(client=client, text=flattened_text)

            # Modify the document with the new annotations
            for sentence in sentences:
                sent_id = str(sentence["index"])
                # When possible, match the CoreNLP annotations to the stanza annotations
                if document["sentences"].get(sent_id):
                    original_sentence = document["sentences"][sent_id]
                    original_sentence.update({"corenlp_layer": sentence})
            document["corefs"] = corefs

            # Update the database document with the modifications
            collection.update_one(
                filter={"_id": doc_id}, update={"$set": document}, upsert=False
            )
