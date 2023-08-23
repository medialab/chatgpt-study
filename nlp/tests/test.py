import csv
import gzip
import json
import os
import sys
import unittest
from contextlib import contextmanager
from pprint import pprint

from texts import TEXTS

DIR = os.path.dirname(__file__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Try reading gzipped file
@contextmanager
def open_infile(infile):
    if infile.endswith(".gz"):
        with gzip.open(infile, "rt") as f:
            yield f
    else:
        with open(infile, "r") as f:
            yield f


class TestTwitterStanza(unittest.TestCase):
    def setUp(self) -> None:
        from src.dep_parsing import TwitterStanzaAnnotator

        self.nlp = TwitterStanzaAnnotator()
        self.texts = TEXTS

    def test_annotation(self):
        import casanova
        from stanza.utils.conll import CoNLL
        from tqdm import tqdm

        # Parse file paths and count infile length
        outfile = DIR + "/conllu.csv"
        infile = DIR + "/data.csv"
        try:
            infile_length = casanova.reader.count(infile)
        except Exception:
            infile = DIR + "/data.csv.gz"
            infile_length = casanova.reader.count(infile)

        # Enrich file
        with open_infile(infile) as f, open(outfile, "w") as of:
            enricher = casanova.enricher(
                input_file=f, output_file=of, add=["conllu_string"]
            )
            for row, text in tqdm(
                enricher.cells("text", with_rows=True), total=infile_length
            ):
                # Parse the text and generate a Document object
                ann = self.nlp(text=text)
                original_doc_obj = ann.doc_object

                # Convert the Document object into a string (format CoNLL)
                conllu_string = CoNLL.doc2conll_text(original_doc_obj)
                enricher.writerow(row + [conllu_string])

                # Re-convert the string back into a Document object
                new_doc_obj = CoNLL.conll2doc(input_str=conllu_string)
                # Because the CoNLL format doesn't have NER, the processor
                # did not do NER and a key "misc" needs removed from each token
                new_doc = []
                for sentence in new_doc_obj.to_dict():
                    sent = []
                    for token in sentence:
                        token.pop("misc")
                        sent.append(token)
                    new_doc.append(sent)

                # Verify that the Document was successfully converted
                # into a string and that it can be converted back
                assert original_doc_obj.to_dict() == new_doc


class TestCasanova(unittest.TestCase):
    def test_zipped_file(self):
        import casanova

        # Gzipped file path
        infile = DIR + "/data.csv.gz"

        with open_infile(infile) as f:
            reader = casanova.reader(f)
            for _ in reader:
                pass


if __name__ == "__main__":
    unittest.main(warnings="ignore")
