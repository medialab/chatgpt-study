import json
import os
import sys
import unittest
from pprint import pprint

from texts import TEXTS

DIR = os.path.dirname(__file__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestTwitterStanza(unittest.TestCase):
    def setUp(self) -> None:
        from src.dep_parsing import TwitterStanzaAnnotator

        self.nlp = TwitterStanzaAnnotator()
        self.texts = TEXTS

    def test_annotation(self):
        from tqdm import tqdm
        from stanza.utils.conll import CoNLL
        import casanova

        outfile = DIR + "/conllu.csv"
        infile = DIR + "/data.csv"
        infile_length = casanova.reader.count(infile)
        with open(infile) as f, open(outfile, "w") as of:
            enricher = casanova.enricher(f, of, add=["conllu_string"])
            for row, text in tqdm(
                enricher.cells("text", with_rows=True), total=infile_length
            ):
                # Parse the text and generate a Document object
                ann = self.nlp(text=text)
                original_doc_obj = ann.doc_object

                # Convert the Document object into a string (format CoNLL)
                conllu_string = CoNLL.doc2conll_text(original_doc_obj)
                enricher.writerow(row, [conllu_string])

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


if __name__ == "__main__":
    unittest.main(warnings="ignore")
