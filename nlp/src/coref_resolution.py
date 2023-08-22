import json
import logging
import os
from datetime import datetime
from dataclasses import dataclass, field

import spacy
from spacy.tokens import Doc

import click

from src.constants import TWEET_STANZA_MAPPINGS
from src.utils import (
    create_client,
    scroll_index,
    search_document,
    setup_index,
    yield_data,
)

# log_filename = "screen_{}_{}.log".format(os.getenv("STY"), datetime.utcnow())
# logging.basicConfig(filename=log_filename, encoding="utf-8", level=logging.ERROR)


@dataclass
class SpacyDocResult:
    sent_starts: list = field(default_factory=list)
    words: list = field(default_factory=list)
    lemmas: list = field(default_factory=list)
    pos: list = field(default_factory=list)
    deps: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    heads: list = field(default_factory=list)


class SpacyDoc:
    def __init__(self, nlp):
        self.nlp = nlp

    def __call__(self, tokens: list[dict], deps: list[dict]):
        result = SpacyDocResult()
        dependency_dict = {}
        for dep in deps:
            dependency_dict.update(
                {dep["word"]["sequential_token_id"]: dep["word"]["head"]}
            )
        for token in tokens:
            doc_token_id = token["doc_token_id"]
            result.words.append(token["text"])
            result.lemmas.append(token["lemma"])
            result.pos.append(token["upos"])
            result.deps.append(token["deprel"])
            result.tags.append(token["ner"])
            result.heads.append(dependency_dict[doc_token_id])
            if token["id"] == 0:
                result.sent_starts.append(True)
            else:
                result.sent_starts.append(False)
        return Doc(
            vocab=self.nlp.vocab,
            words=result.words,
            sent_starts=result.sent_starts,
            lemmas=result.lemmas,
            deps=result.deps,
        )


@dataclass
class AnnotationLayer:
    text: str
    corefs: str


class CorefResolver:
    def __init__(self):
        self.nlp = spacy.load(
            "en_core_web_trf",
            exclude=["lemmatizer", "tokenizer", "parser"],
        )
        self.nlp.add_pipe("coreferee")

    def __call__(self, docs):
        for doc in self.nlp.pipe(docs):
            coref_chains = doc._.coref_chains
            yield AnnotationLayer(
                text=doc.text, corefs=coref_chains.pretty_representation
            )


@click.command()
@click.option("--index-name", required=True)
@click.option("--reset-index", is_flag=True, show_default=True, default=False)
def main(index_name, reset_index):
    client = create_client()
    # coref_index_name = index_name + "-with-coref-resolution"
    # setup_index(client=client, index_name=index_name, reset=reset_index, mappings=)

    # Set up coref model
    coref_resolver = CorefResolver()
    to_spacy_doc = SpacyDoc(nlp=coref_resolver.nlp)

    for batch in scroll_index(client=client, index=index_name, pagesize=10):
        docs = [
            doc["_source"]
            for doc in batch
            # if not search_document(
            #     client=client, id=doc["_source"]["id"], index_name=coref_index_name
            # )
        ]
        spacy_docs = [to_spacy_doc(doc["tokens"]) for doc in docs]
        for annotation in coref_resolver(spacy_docs):
            print(
                f"\n\n----------\nTEXT: {annotation.text}\nCOREFS: {annotation.corefs}"
            )


if __name__ == "__main__":
    main()  # type: ignore
