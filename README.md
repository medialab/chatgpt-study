# ChatGPT Study

## Description

This repository contains some tools to annotate and query data collected for a study on discourses around ChatGPT and AI.

## Database

Go to the project's database directory.

```shell
cd nlp-db/
```

Activate a virtual Python environment and install dependencies.

```shell
pyenv virtualenv 3.11.* chatgpt-db
pyenv activate chatgpt-db
pip install -r requirements.txt
```

### How to test database connection

```shell
python test.py
```

### How to annotate Tweets

```shell
python main.py --index-name tweet-english-original annotate --datafile /PATH/TO/ENGLISH/TWEETS --lang en
```
