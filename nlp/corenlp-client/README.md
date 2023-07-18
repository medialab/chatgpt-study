## Install MongoDB

MacOS

```shell
brew tap mongodb/brew
brew update
brew install mongodb-community@6.0
```

---

## Install annotation tool

```shell
pip install --upgrade pip setuptools wheel
pip install stanza==1.5.0 click==8.1.5 casanova==1.15.1 pymongo==4.4.1
```

---

## Start local MongoDB server

```shell
brew services start mongodb/brew/mongodb-community
```

---

## Annotate CSV data file with Stanza

```
python main.py --collection test stanza example.data.csv
```

---

## Annotate tokenized text with CoreNLP

```
python main.py --collection test corenlp
```
