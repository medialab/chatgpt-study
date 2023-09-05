from typing import Any, List
import torch
from dataclasses import dataclass, field
import spacy
from fastcoref import spacy_component, LingMessCoref, FCoref


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


class FastCorefAnnotator:
    def __init__(self):
        # mps_device = torch.device("mps")
        self.nlp = spacy.load(
            "en_core_web_lg", disable=["parser", "lemmatizer", "ner", "textcat"]
        )
        self.nlp.add_pipe(
            "fastcoref",
            config={
                "model_architecture": "LingMessCoref",
                "model_path": "biu-nlp/lingmess-coref",
                "device": "cpu",  # mps not currently supported (see https://github.com/pytorch/rl/issues/1198)
            },
        )

    def __call__(self, texts: list):
        docs = self.nlp.pipe(texts, component_cfg={"fastcoref": {"resolve_text": True}})
        return [doc._.resolved_text for doc in docs]


def test():
    mps_device = torch.device("mps")

    model = FCoref(device=mps_device)

    preds = model.predict(
        texts=[
            "We are so happy to see you using our coref package. This package is very fast!",
            "We are so happy to see you using our coref package. This package is very fast!",
            "We are so happy to see you using our coref package. This package is very fast!",
            "We are so happy to see you using our coref package. This package is very fast!",
        ]
    )

    pred = preds[0]


if __name__ == "__main__":
    test()
