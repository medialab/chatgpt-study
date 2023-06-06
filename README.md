# ChatGPT Study

## Access Data

The data is stored in a MongoDB Atlas database cluster. MongoDB was chosen because it is a document database and most queries will concern metadata associated with unique documents, specifically tweets.

### Prepare access to the database

1. Create a new virtual environment in version 3.11 of Python.
2. Install the tool's requirements.

```shell
pip install -r requirements.txt
```

3. Request access to the remote MongoDB database.
   1. Have/create a free account on the [MongoDB website](https://www.mongodb.com).
   2. Request that your account be added to the database cluster.
   3. Remember your account's username and password.

### Query the database

To query the database, you will need your MongoDB account's username and password as well as the name of the collection you wish to query. For tweets, that collection is named "tweets."

All query commands are preceded by the following command:

```shell
python db/mongo-cli.py --username YOUR_USERNAME --password YOUR_PASSWORD --collection COLLECTION_NAME
```

Required parameters:

- `--username` : your MongoDB account username
- `--password` : your MongoDB account password
- `--collection` : the name of the collection you're querying, i.e. "tweets"

Available commands:

- `count` : count the number of documents in the collection
- `find` : find tweets that match a query written in the MongoDB Query Language (MQL)

#### Measure the size of the collection (`count`)

```shell
python db/mongo-cli.py --username YOUR_USERNAME --password YOUR_PASSWORD --collection COLLECTION_NAME count
```

No additional parameters.

#### Search documents (`find`)

```shell
python db/mongo-cli.py --username YOUR_USERNAME --password YOUR_PASSWORD --collection COLLECTION_NAME find --field FIELD --condition CONDITION
```

Additional parameters:

- `--field` : the field in which you will search for matches
- `--condition` : the value or condition on which you want to match

For example, in the tweets collection, if you want to search for all text tokens that were analyzed to be a location ("LOC"), you would search for "LOC" (`--condition "LOC"`) within the field "tag" in a tweet document's array "annotations" (`--field "annotations.tag"`).

```shell
find --field "annotations.tag" --condition "LOC"
```

In MQL syntax, this query would be written like this: `{"annotations.tag" : "LOC"}`.

The output of all searches is written to a JSON file called `query-output.json`.

## Annotate Data

Collected tweets' texts were annotated with Named-Entity-Recognition (NER) tags. The script that performed this annotation is [here](nlp/named-entity-recognition.py). It follows the following steps:

1. Clean the Tweet metadata (dates, arrays, etc.).
1. Clean the Tweet's text by removing the # at the start of a hashtag as well as Twitter usernames and URLs.
1. Predict the text's NER tags using [Flair's](https://github.com/flairNLP/flair) `ner-large` tokenizer and NER models.
1. Format in JSON and write the predicts to a file.

The file produced by the steps above was then inserted into a MongoDB database using [this script](db/build.py).
