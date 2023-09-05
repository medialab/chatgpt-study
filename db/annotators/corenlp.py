from contextlib import contextmanager
from dataclasses import dataclass, field

import stanza
from stanza.server import CoreNLPClient, StartServer


CORENLP_ANNOTATORS = [
    "tokenize",  # Tell to tokenize on white space
    "ssplit",  # Tell to split sentences on \n\n
    "openie",
    "coref",
]


@dataclass
class AnnotationLayer:
    openie_triples: list = field(default_factory=list)
    entity_mentions: list = field(default_factory=list)
    nested_corefs: list = field(default_factory=list)

    def asdict(self) -> dict:
        attrs = [self.openie_triples, self.entity_mentions, self.nested_corefs]
        for attr in attrs:
            if len(attr) == 0:
                attr = [{}]
        return {
            "openieTriples": self.openie_triples,
            "entityMentions": self.entity_mentions,
            "corefs": self.nested_corefs,
        }


class CoreNLPAnnotator:
    def __init__(self) -> None:
        stanza.download("en")  # type: ignore
        self.nlp = self.corenlp_client()

    @contextmanager
    def corenlp_client():
        try:
            yield CoreNLPClient(
                annotators=CORENLP_ANNOTATORS,
                memory="4G",
                endpoint="http://localhost:9001",
                be_quiet=True,
                preload=True,
                start_server=StartServer.TRY_START,
            )
        except FileNotFoundError:
            stanza.install_corenlp()
            yield CoreNLPClient(
                annotators=CORENLP_ANNOTATORS,
                memory="4G",
                endpoint="http://localhost:9001",
                be_quiet=True,
                preload=True,
                start_server=StartServer.TRY_START,
            )

    def parse_doc(self, text: str):
        with self.nlp as nlp:
            doc = nlp.annotate(
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

    def flatten_nested_tokens(self, nested_tokens):
        output = ""
        sentence_tokens = nested_tokens.values()
        i = 0
        while i < len(sentence_tokens):
            output += " ".join(list(sentence_tokens)[i])
            output += "\n\n"
            i += 1
        return output

    def __call__(self, pretokenized_text: str) -> AnnotationLayer:
        result = AnnotationLayer()

        text = self.flatten_nested_tokens(pretokenized_text)
        sentences, corefs = self.parse_doc(text=text)

        return result


class CoreNLPAnnotation:
    def __init__(self, client: CoreNLPClient) -> None:
        self.client = client
        self.openie_triples = []
        self.entity_mentions = []
        self.nested_corefs = []

    def parse_corefs(self, text: str) -> tuple[list, dict]:
        doc = self.client.annotate(
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

    def __call__(self, flattened_text: str) -> None:
        # Annotate the prepared text
        sentences, corefs = self.parse_corefs(text=flattened_text)
        for n, sent in enumerate(sentences):
            openie_tripes = sent["openie"]
            for openie in openie_tripes:
                openie.update({"sentence": n + 1})
                self.openie_triples.append(openie)

            mentions = sent["entitymentions"]
            for mention in mentions:
                mention.update({"sentence": n + 1})
                self.entity_mentions.append(mention)

        for coref_id, coref_list in corefs.items():
            updated_coref_list = []
            for coref in coref_list:
                coref.update({"coref_id": coref_id})
                updated_coref_list.append(coref)

            self.nested_corefs.append(updated_coref_list)
