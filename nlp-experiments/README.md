# Annotation of Tweet text

### Contents

- [Set Up](#set-up)
- [Usage](#usage)
- [Notes](#notes)

---

## Set up

### Install [old version](https://www.mongodb.com/download-center/community/releases/archive) of MongoDB (=< 4.0.3)

MacOS

```shell
$ curl -O https://fastdl.mongodb.org/osx/mongodb-osx-ssl-x86_64-4.0.3.tgz
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
