# ChatGPT Study

## Description

This repository contains some tools to annotate and query data collected for a study on discourses around ChatGPT and AI.

### Table of contents

- [How to query annotated data](#access-data)
  - [Set up access](#prepare-access-to-the-database)
  - [Query data](#query-the-database)
- [How to annotate data](#annotate-data)

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
python db/mongo-cli.py --username YOUR_USERNAME --password YOUR_PASSWORD --collection COLLECTION_NAME find --field FIELD --value VALUE
```

Additional parameters:

- `--field` : the field in which you will search for matches
- `--value` : the value or condition on which you want to match

The output of all searches is written to a JSON file called `query-output.json`.

Examples

<table>
   <tr>
      <th>Research question</th>
      <th><code>--field</code></th>
      <th><code>--value</code></th>
      <th>Query in MongoDB syntax</th>
      <th colspan=4>Example matches</th>
   </tr>
   <tr>
      <th colspan=4></th>
      <th>Tweet text</th>
      <th>NER results</th>
      <th>Tweet text</th>
      <th>NER results</th>
   </tr>
   <tr>
      <td>What tweets have locations in the text?</td>
      <td><code>'annotations.tag'</code></td>
      <td><code>'LOC'</code></td>
      <td><code>{"annotation.tag" : "LOC"}</code></td>
      <td>ChatGPT BOT on "Is cannabis legal in Italy and Israel" https://...</td>
      <td>
      Annotation:<br/>
         <code>"tag":"LOC",</code><br/>
         <code>"text":"Italy",</code><br/>
         <code>"score":0.9999960660934448,</code><br/>
         <code>"start_position":37,</code><br/>
         <code>"end_position":42</code><br/>
      </td>
      <td>"- This is a big innovation in the Metaverse industry, you can just walk up and ask the #AI #ChatGPT ​​any question.<br/><br/>@Enter_Realm reform Metaverse! « Enter_Realm: The future is here!<br/><br/>#AI is taking over Realm's Metaverse!...</td>
      <td>
      Annotation:<br/>
         <code>"tag":"LOC",</code><br/>
         <code>"text":"Metaverse",</code><br/>
         <code>"score":0.6627128720283508,</code><br/>
         <code>"start_position":393,</code><br/>
         <code>"end_position":402</code><br/>
      </td>
   </tr>
   <tr>
      <td>What tweets have the words "fake", "misinformation" or "disinformation" in the text?</td>
      <td><code>'tokens.token'</code></td>
      <td><code>'{ "$in": ["fake", "misinformation", "disinformation"]}'</code></td>
      <td><code>{"tokens.token" : { $in: ["fake", "misinformation", "disinformation"] } }</code></td>
      <td>ChatGPT - What people think it looks like vs. reality<br/>So much #AI hype & misinformation around these days.<br/><br/>I'm a strong proponent of using AI technology in healthcare, but we must approach its use responsibly, with an emphasis on:<br/><br/>High quality data & Real-world applications</td>
      <td>
      Token:<br/>
         <code>"index":16,</code><br/>
         <code>"token":"misinformation",</code><br/>
         <code>"start_position":72,</code><br/>
         <code>"end_position":86</code><br/>
      </td>
      <td>I have 5 numbers of contacts on my phone two are Businesses.<br/>None are family.<br/>Pictures and emails and profile pictures are super easy to fake. Chatgpt or whatever is going to make things so much more complicated.  Even if its from the genuine person. You can not trust it.</td>
      <td>
      Token:<br/>
      <code>"index":28,</code><br/>
      <code>"token":"fake",</code><br/>
      <code>"start_position":137,</code><br/>
      <code>"end_position":141</code><br/>
      </td>
   </tr>
</table>

## Annotate Data

Collected tweets' texts were annotated with Named-Entity-Recognition (NER) tags. The script that performed this annotation is [here](nlp/named-entity-recognition.py). It follows the following steps:

1. Clean the Tweet metadata (dates, arrays, etc.).
1. Clean the Tweet's text by removing the # at the start of a hashtag as well as Twitter usernames and URLs.
1. Predict the text's NER tags using [Flair's](https://github.com/flairNLP/flair) `ner-large` tokenizer and NER models.
1. Format in JSON and write the predictions to a file.

The file produced by the steps above was then inserted into a MongoDB database using [this script](db/build.py).
