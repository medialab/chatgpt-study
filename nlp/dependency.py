import argparse
from dataclasses import dataclass, field
from pprint import pprint
from typing import List

import casanova
import emoji
import stanza
from casanova import TabularRecord
from stanza.utils.conll18_ud_eval import CONTENT_DEPRELS
from tqdm import tqdm


@dataclass
class Dependencies(TabularRecord):
    sentence_id: str | None = None
    sentence: str | None = None
    root_text: str | None = None
    root_lemma: str | None = None
    root_pos: str | None = None
    goeswith_root: List[str] | None = field(default_factory=list)
    dep_verb_text: List[str] | None = field(default_factory=list)
    dep_verb_lemma: List[str] | None = field(default_factory=list)
    dep_noun_text: List[str] | None = field(default_factory=list)
    dep_noun_lemma: List[str] | None = field(default_factory=list)
    dep_adj_text: List[str] | None = field(default_factory=list)
    dep_adj_lemma: List[str] | None = field(default_factory=list)
    dep_pronoun_text: List[str] | None = field(default_factory=list)
    dep_pronoun_lemma: List[str] | None = field(default_factory=list)
    dep_adverb_text: List[str] | None = field(default_factory=list)
    dep_adverb_lemma: List[str] | None = field(default_factory=list)


def clean_doc(doc: str) -> str:
    # Take out links from the Tweet text
    without_urls = " ".join(
        [token for token in doc.split() if not token.startswith("http")]
    )

    # Remove hashtags and @ signs from the front of tokens
    without_tags = "".join(
        [char for char in without_urls if char != "#" and char != "@"]
    )

    # Remove emojis
    return emoji.replace_emoji(without_tags, replace="")


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("language")
    parser.add_argument("outfile")
    args = parser.parse_args()
    return args.infile, args.language, args.outfile


def parse_sentence(sent, doc_id, n) -> Dependencies:
    # Set up the Tabular Record
    row = Dependencies(sentence=sent.text)

    # Give this record a unique ID
    row.sentence_id = doc_id + "_" + str(n)

    # Set up a dictionary to store parts of the dependency graph
    graph = {"root": {"word": {}}, "dependencies": []}

    # Get the root word from the parsed sentence
    for word in sent.words:
        if word.deprel == "root":
            graph["root"]["word"] = word.to_dict()
            row.root_text = word.text
            row.root_lemma = word.lemma
            row.root_pos = word.upos

    # Get an iterable of all the words that directly depend on the root
    for word in sent.words:
        if word.head == graph["root"]["word"]["id"] and word.deprel in CONTENT_DEPRELS:
            graph["dependencies"].append(word.to_dict())

    # Find any words that go with the root word
    root_id = graph["root"]["word"]["id"]
    for word in sent.words:
        if word.head == root_id and word.deprel == "goeswith":
            label = word.text + " {{" + word.upos + "}}"
            row.goeswith_root.append(label)
            row.goeswith_root.append(word.lemma)

    # For all the words that directly depend on the root,
    # add their data to the right column
    for dep in graph["dependencies"]:
        pos = dep.get("xpos")
        text = dep.get("text")
        lemma = dep.get("lemma")
        upos = dep.get("upos")
        if pos.startswith("V"):
            label = text + " {{" + upos + "}}"
            row.dep_verb_text.append(label)
            row.dep_verb_lemma.append(lemma)
        elif pos.startswith("N"):
            label = text + " {{" + upos + "}}"
            row.dep_noun_text.append(label)
            row.dep_noun_lemma.append(lemma)
        elif pos.startswith("J"):
            label = text + " {{" + upos + "}}"
            row.dep_adj_text.append(label)
            row.dep_adj_lemma.append(lemma)
        elif pos.startswith("PR"):
            label = text + " {{" + upos + "}}"
            row.dep_pronoun_text.append(label)
            row.dep_pronoun_lemma.append(lemma)
        elif pos.startswith("RB"):
            label = text + " {{" + upos + "}}"
            row.dep_adverb_text.append(label)
            row.dep_adverb_lemma.append(lemma)

    # Return the Tabular Record
    return row


def main():
    infile, language, outfile = parse_cli_args()

    # Set up the Stanza Pipeline
    stanza.download(language)
    stanza_pipeline = stanza.Pipeline(
        lang=language,
        processors="tokenize,mwt,pos,lemma,depparse",
    )

    # Set up the data files
    print("counting file length...")
    file_length = casanova.reader.count(infile)
    fieldnames = Dependencies.fieldnames()

    # Enrich the data with dependencies
    with open(infile, "r", encoding="utf-8") as f, open(outfile, "w") as of:
        enricher = casanova.enricher(f, of, add=fieldnames)
        id_pos = enricher.headers["id"]
        for row, text in tqdm(
            enricher.cells("text", with_rows=True), total=file_length
        ):
            # Clean the tweet text
            text = clean_doc(text)

            # Process the cleaned text with the Stanza pipeline
            doc = stanza_pipeline(text)

            # Write a new line in the enriched CSV for every sentence in the tweet text
            for n, sent in enumerate(doc.sentences):
                addendum = parse_sentence(sent=sent, tweet_id=row[id_pos], n=n)
                enricher.writerow(row, addendum)


if __name__ == "__main__":
    main()
