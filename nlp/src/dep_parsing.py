from dataclasses import dataclass, field
from pathlib import Path

import stanza
from stanza.models.common.doc import Document

# Path to cloned TweebankNLP repo
TWEEBANK_PATH = Path("TweebankNLP")

# Path to downloaded models' directory (in TweebankNLP repo)
MODEL_PATH = TWEEBANK_PATH.joinpath("twitter-stanza/saved_models")

# Paths to individual TweebankNLP models
tokenize_model_path = MODEL_PATH.joinpath("tokenize/en_tweet_tokenizer.pt")
lemma_model_path = MODEL_PATH.joinpath("lemma/en_tweet_lemmatizer.pt")
pos_model_path = MODEL_PATH.joinpath("pos/en_tweet_tagger.pt")
depparse_model_path = MODEL_PATH.joinpath("depparse/en_tweet_parser.pt")
ner_model_path = MODEL_PATH.joinpath("ner/en_tweet_nertagger.pt")

TWITTER_STANZA_CONFIG = {
    "processors": "tokenize,lemma,pos,depparse",
    "lang": "en",
    "tokenize_pretokenized": False,  # disable tokenization
    "tokenize_model_path": str(tokenize_model_path.absolute()),
    "lemma_model_path": str(lemma_model_path.absolute()),
    "pos_model_path": str(pos_model_path.absolute()),
    "depparse_model_path": str(depparse_model_path.absolute()),
    # "ner_model_path": str(ner_model_path.absolute()),
}


@dataclass
class AnnotationLayer:
    doc_object: Document = Document(sentences=[])
    sentences: list = field(default_factory=list)
    dependencies: list = field(default_factory=list)

    def asdict(self) -> dict:
        attrs = [self.dependencies, self.sentences]
        for attr in attrs:
            if len(attr) == 0:
                attr = [{}]
        return {
            "dependencies": self.dependencies,
            "sentences": self.sentences,
        }


class TwitterStanzaAnnotator:
    def __init__(self) -> None:
        stanza.download("en")  # type: ignore
        self.nlp = stanza.Pipeline(**TWITTER_STANZA_CONFIG)  # type: ignore

    def parse(self, text) -> Document:
        return self.nlp(text)  # type: ignore

    def __call__(self, text: str) -> AnnotationLayer:
        annotation = AnnotationLayer()
        doc = self.parse(text)
        annotation.doc_object = doc
        annotation.sentences = doc.to_dict()
        annotation.dependencies = [sent.dependencies for sent in doc.sentences]

        return annotation


if __name__ == "__main__":
    import argparse
    import gzip
    from contextlib import contextmanager

    import casanova
    from stanza.utils.conll import CoNLL
    from tqdm import tqdm

    # Try reading gzipped file
    @contextmanager
    def open_infile(infile):
        if infile.endswith(".gz"):
            with gzip.open(infile, "rt") as f:
                yield f
        else:
            with open(infile, "r") as f:
                yield f

    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("outfile")
    args = parser.parse_args()

    print("Counting file length...")
    file_length = casanova.reader.count(args.infile)

    nlp = TwitterStanzaAnnotator()

    with open_infile(args.infile) as f, open(args.outfile, "w") as of:
        enricher = casanova.enricher(input_file=f, output_file=of, add=["conll_string"])
        for row, text in tqdm(
            enricher.cells("text", with_rows=True), total=file_length
        ):
            ann = nlp(text=text)
            doc = ann.doc_object

            # Convert the Document object into a string (format CoNLL)
            conllu_string = CoNLL.doc2conll_text(doc)
            enricher.writerow(row, [conllu_string])
