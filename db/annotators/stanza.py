from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator

import stanza

# Path to cloned TweebankNLP repo
TWEEBANK_PATH = Path("resources/TweebankNLP")

# Path to downloaded models' directory (in TweebankNLP repo)
MODEL_PATH = TWEEBANK_PATH.joinpath("twitter-stanza/saved_models")

# Paths to individual TweebankNLP models
tokenize_model_path = MODEL_PATH.joinpath("tokenize/en_tweet_tokenizer.pt")
lemma_model_path = MODEL_PATH.joinpath("lemma/en_tweet_lemmatizer.pt")
pos_model_path = MODEL_PATH.joinpath("pos/en_tweet_tagger.pt")
depparse_model_path = MODEL_PATH.joinpath("depparse/en_tweet_parser.pt")
ner_model_path = MODEL_PATH.joinpath("ner/en_tweet_nertagger.pt")

TWITTER_STANZA_CONFIG = {
    "processors": "tokenize,lemma,pos,depparse,ner",
    "lang": "en",
    "tokenize_pretokenized": True,  # disable tokenization
    "tokenize_model_path": str(tokenize_model_path.absolute()),
    "lemma_model_path": str(lemma_model_path.absolute()),
    "pos_model_path": str(pos_model_path.absolute()),
    "depparse_model_path": str(depparse_model_path.absolute()),
    "ner_model_path": str(ner_model_path.absolute()),
}


def make_token_id(sent_id: int | str, token_id: int | str):
    return f"s{sent_id}t{token_id}"


@dataclass
class AnnotationLayer:
    text_tokenized: list = field(default_factory=list)
    tokens: list = field(default_factory=list)
    dependencies: list = field(default_factory=list)

    def asdict(self) -> dict:
        attrs = [self.text_tokenized, self.tokens, self.dependencies]
        for attr in attrs:
            if len(attr) == 0:
                attr = [{}]
        return {
            "text_tokenized": self.text_tokenized,
            "tokens": self.tokens,
            "dependencies": self.dependencies,
        }


class TwitterStanzaAnnotator:
    def __init__(self) -> None:
        stanza.download("en")  # type: ignore
        self.nlp = stanza.Pipeline(**TWITTER_STANZA_CONFIG)  # type: ignore

    def yield_sentences(self, text) -> Generator:
        doc = self.nlp(text)
        yield from doc.sentences  # type:ignore

    def __call__(self, text: str) -> AnnotationLayer:
        result = AnnotationLayer()
        for sent_id, sent in enumerate(self.yield_sentences(text)):
            sent_tokens = sent.to_dict()

            # Add a new list of tokens to the doc's tokenized_text
            result.text_tokenized.append(
                {f"sent_{sent_id}": [t["text"] for t in sent_tokens]}
            )

            # Add new tokens to doc's tokens
            for token in sent_tokens:
                token_id = token["id"]
                token.update(
                    {
                        "sent_id": sent_id,
                        "doc_token_id": make_token_id(
                            sent_id=sent_id, token_id=token_id
                        ),
                    }
                )
                result.tokens.append(token)

            # Add new dependencies to doc's dependencies
            for dep in sent.dependencies:
                head = dep[0].to_dict()
                dependency_relation = dep[1]
                word = dep[2].to_dict()

                head.update({"sent_id": sent_id})
                word.update(
                    {
                        "sent_id": sent_id,
                        "doc_token_id": make_token_id(
                            sent_id=sent_id, token_id=word["id"]
                        ),
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
                result.dependencies.append(
                    {
                        "head": head,
                        "deprel": dependency_relation,
                        "word": word,
                    }
                )
        return result


import click
import casanova


@click.command()
@click.argument("file")
def test(file):
    i = 0
    texts = []
    with open(file) as f:
        reader = casanova.reader(f)
        for tweet_text in reader.cells("text"):
            i += 1
            stanza_annotator = TwitterStanzaAnnotator()
            stanza_annotation = stanza_annotator(tweet_text)
            texts.append(stanza_annotation.asdict())
            if i > 9:
                break


if __name__ == "__main__":
    test()
