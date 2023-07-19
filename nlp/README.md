# Annotation of Tweet text

### Contents

- [Set Up](#set-up)
- [Usage](#usage)
- [Notes](#notes)

---

## Set up

### Install MongoDB

MacOS

```shell
brew tap mongodb/brew
brew update
brew install mongodb-community@6.0
```

### Install annotation tool

```shell
pip install --upgrade pip setuptools wheel
pip install stanza==1.5.0 click==8.1.5 casanova==1.15.1 pymongo==4.4.1
```

### Start local MongoDB server

```shell
brew services start mongodb/brew/mongodb-community
```

---

## Usage

### Annotate CSV data file with Stanza

```
python main.py --collection test stanza example.data.csv
```

### Annotate tokenized text with CoreNLP

```
python main.py --collection test corenlp
```

---

## Notes

### Phase 1: Sentence-level annotation

Proposed model: [Stanza](https://stanfordnlp.github.io/stanza/)

- graph-based
- biaffine attention
  > Peng Qi, Yuhao Zhang, Yuhui Zhang, Jason Bolton, and Christopher D. Manning. 2020. Stanza: A Python Natural Language Processing Toolkit for Many Human Languages. In _Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics: System Demonstrations_, pages 101–108, Online. Association for Computational Linguistics. [DOI 10.18653/v1/2020.acl-demos.14](https://aclanthology.org/2020.acl-demos.14/).

Proposed annotations:

- tokenize
- mwt (only available for French and German)
- pos
- lemma
- depparse
- ner
- constituency

### Phase 2: Document-level annotation

Proposed model: [CoreNLP](https://stanfordnlp.github.io/CoreNLP/)

> Christopher Manning, Mihai Surdeanu, John Bauer, Jenny Finkel, Steven Bethard, and David McClosky. 2014. The Stanford CoreNLP Natural Language Processing Toolkit. In Proceedings of 52nd Annual Meeting of the Association for Computational Linguistics: System Demonstrations, pages 55–60, Baltimore, Maryland. Association for Computational Linguistics. [DOI 10.3115/v1/P14-5010](https://aclanthology.org/P14-5010/).

- Downsides

  - old architecture (2014)
  - lacking developments in span-based coreference (Lee et al., 2017)

- Positives
  - well-maintained (version 4.5.4 released 15 March 2023)
  - easy to use with Stanza Python client

---

### Other potential models for document-level annotation

To justify use of document-level annotator (maybe CoreNLP), check performance against other options.

- For coreference

  - Experimental SpaCy (`spacy-experimental`) end-to-end neural coreference resolution. [Blog post](https://explosion.ai/blog/coref) published 6 October 2022 on SpaCy's explosion.ai site.
  - [v. 0.6.0](https://github.com/explosion/spacy-experimental/releases/tag/v0.6.0) published 28 September 2022.
  - Documentation with [example](https://github.com/explosion/projects/tree/v3/experimental/coref).

- For relation extraction

  - REBEL (Relation Ex- traction By End-to-end Language generation)

    - transformer-based
    - seq2seq

    > Pere-Lluís Huguet Cabot and Roberto Navigli. 2021. REBEL: Relation Extraction By End-to-end Language generation. In _Findings of the Association for Computational Linguistics: EMNLP 2021_, pages 2370–2381, Punta Cana, Dominican Republic. Association for Computational Linguistics. [DOI 10.3115/v1/P14-5010](https://aclanthology.org/P14-5010/).

    - [HuggingFace model card](https://huggingface.co/Babelscape/rebel-large?text=Punta+Cana+is+a+resort+town+in+the+municipality+of+Higuey%2C+in+La+Altagracia+Province%2C+the+eastern+most+province+of+the+Dominican+Republic)
