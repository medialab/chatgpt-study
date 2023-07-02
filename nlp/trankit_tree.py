from argparse import ArgumentParser

import casanova
from tqdm import tqdm
from trankit.trankit import Pipeline

token_columns = [
    "token_id",
    "token_text",
    "token_upos",
    "token_xpos",
    "token_feats",
    "token_head",
    "token_deprel",
    "token_lemma",
    "token_ner",
    "doc_span_start",
    "doc_span_end",
    "sent_span_start",
    "sent_span_end",
]


def main():
    parser = ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("outfile")
    args = parser.parse_args()

    print("downloading pipeline...")
    pipeline = Pipeline(lang="english", gpu=True)

    print("counting length of file...")
    length = casanova.reader.count(args.infile)
    with open(args.infile, "r") as f, open(args.outfile, "w") as of:
        enricher = casanova.enricher(f, of, select=["id", "text"], add=token_columns)
        # for row, text in enricher.cells("text", with_rows=True):
        for row, text in tqdm(enricher.cells("text", with_rows=True), total=length):
            doc = pipeline(text)
            if isinstance(doc, dict) and isinstance(doc.get("sentences"), list):
                for sentence in doc["sentences"]:
                    for token in sentence.get("tokens"):
                        addendum = {
                            "token_id": token.get("id"),
                            "token_text": token.get("text"),
                            "token_upos": token.get("upos"),
                            "token_xpos": token.get("xpos"),
                            "token_feats": token.get("feats"),
                            "token_head": token.get("head"),
                            "token_deprel": token.get("deprel"),
                            "token_lemma": token.get("lemma"),
                            "token_ner": token.get("ner"),
                            "doc_span_start": token.get("dspan")[0],
                            "doc_span_end": token.get("dspan")[1],
                            "sent_span_start": token.get("span")[0],
                            "sent_span_end": token.get("span")[1],
                        }
                        enricher.writerow(row, addendum.values())


if __name__ == "__main__":
    main()
