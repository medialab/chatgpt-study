# Dependency Parsing Tweets

## Objective

Parse the text of a Tweet.

`Example 1`

```
Try talking with ChatGPT, our new AI system which is optimized for dialogue. Your feedback will help us improve it. https://openai.com/blog/chatgpt/
```

`Example 2`

```
I asked ChatGPT (a new AI system that is optimized for dialogue) to teach me SEO in a minute.

The result: https://...
```

Identify subject-action-object triples.

```json
{
  "Example 1": [
    {
      "subject": "your feedback",
      "action": "improve",
      "object": "ChatGPT"
    }
  ],
  "Example 2": [
    {
      "subject": "I",
      "action": "ask",
      "object": "ChatGPT"
    },
    {
      "subject": "ChatGPT",
      "action": "teach",
      "object": "me"
    }
  ]
}
```

---

### Challenges

#### Dependency Parsing

Most dependency parsers are trained on long-form and/or formally written texts, such as Wikipedia articles.

Solution: [`TweebankNLP`](https://github.com/mit-ccc/TweebankNLP/) is a dependency parser, based on the well-cited [`Stanza`](https://github.com/stanfordnlp/stanza) parser, that has been re-trained on English-language Tweets. Their June 2022 paper, "Annotating the Tweebank Corpus on Named Entity Recognition and Building NLP Models for Social Media Analysis," can be read and cited [here](https://aclanthology.org/2022.lrec-1.780/).

#### Coreference

Resolve different noun phrases within and across sentences that refer to the same thing.

```
Input:
Try talking with ChatGPT, our new AI system which is optimized for dialogue. Your feedback will help us improve it.

Desired Output:
Try talking with ChatGPT, our new AI system which is optimized for dialogue. Your feedback will help us improve [ChatGPT].
```

Solution:

... still working.

#### Triples

Once the Tweet text has been tokenized, the dependencies parsed, and the tokens resolved to whatever they're referencing within and without the sentence, we want to parse the dependency information and extract subject-action-object triples.

Solution:

... still working.

Ideas:

- [Semgrex and Ssurgeon, Searching and Manipulating Dependency Graphs](https://aclanthology.org/2023.tlt-1.7/)
