from pathlib import Path

JAR_FILE_LOCATION = "/Users/kelly.christensen/Dev/stanfordnlp/stanford-corenlp-4.5.4/*"
ANNOTATORS = "tokenize,ssplit,pos,lemma,ner,depparse,coref,cleanxml"
DATA = "/Users/kelly.christensen/Dev/chatgpt/data/chatgpt-english-original.csv"
DATA_DIR = Path().cwd().joinpath("data_by_day")
INPUT_DIR_NAME = "corenlp-input"
