import casanova
from opensearchpy import OpenSearch
from tqdm import tqdm

from src.constants import BODY, TWEET_STANZA_MAPPINGS


def create_client():
    host = "localhost"
    port = 9200
    auth = ("admin", "admin")
    client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )
    if client.ping():
        print("Connected to database.")
        return client
    else:
        raise RuntimeError


def setup_index(
    client: OpenSearch,
    index_name: str,
    reset: bool = False,
    mappings: dict | None = None,
) -> None:
    body = BODY
    if mappings:
        body.update({"mappings": mappings})
    if reset:
        client.indices.delete(index_name)
    if not client.indices.exists(index_name):
        response = client.indices.create(index=index_name, body=body)
        print("\nCreated index.\n", response)
    else:
        print(f"\nFound index '{index_name}'.")


class CSVRowFormatter:
    def __init__(self, fieldnames: list) -> None:
        self.fields = fieldnames
        self.boolean_fields = [
            k
            for k, v in TWEET_STANZA_MAPPINGS["properties"].items()
            if v["type"] == "boolean"
        ]
        self.integer_fields = [
            k
            for k, v in TWEET_STANZA_MAPPINGS["properties"].items()
            if v["type"] == "integer"
        ]
        self.float_fields = [
            k
            for k, v in TWEET_STANZA_MAPPINGS["properties"].items()
            if v["type"] == "float"
        ]
        self.concatenated_fields = [
            "links",
            "domains",
            "media_urls",
            "media_files",
            "media_types",
            "media_alt_texts",
            "mentioned_names",
            "mentioned_ids",
            "hashtags",
        ]
        self.array_fields = ["place_coordinates"]

    def __call__(self, row: list) -> dict:
        row_dict = {k: v for k, v in list(zip(self.fields, row))}
        formatted_dict = {}
        for k, v in row_dict.items():
            # Replace empty string with None
            if v == "":
                v = None
            if v:
                # Convert boolean fields to True/False
                if k in self.boolean_fields:
                    if v == "1":
                        v = True
                    else:
                        v = False
                # Split array fields by separator
                elif k in self.concatenated_fields:
                    v = v.split("|")
                # Cast strings to integers
                elif k in self.integer_fields:
                    v = int(v)
                # Cast strings to float
                elif k in self.float_fields:
                    v = float(v)
                formatted_dict.update({k: v})
        return formatted_dict


def yield_data(datafile: str, reverse: bool = False, single_column: str | None = None):
    print("\nCounting data file length...")
    total = casanova.reader.count(datafile)
    with open(datafile, "r") as f:
        # Set up the desired reader
        if reverse:
            reader = casanova.reverse_reader(f)
        else:
            reader = casanova.reader(f)

        # Yield either a single column or the whole row
        if single_column:
            for cell in tqdm(reader.cells(single_column), total=total):
                yield cell
        else:
            fieldnames = reader.fieldnames
            print("\nProcessing documents...")
            if isinstance(fieldnames, list):
                csv_row_formatter = CSVRowFormatter(fieldnames=fieldnames)
                for row in tqdm(
                    reader,
                    total=total,
                ):
                    yield csv_row_formatter(row)


def search_document(client: OpenSearch, id: str, index_name: str):
    response = client.search(body={"query": {"terms": {"_id": [id]}}}, index=index_name)
    hits = response["hits"]["total"]["value"]

    # If Tweet is not in the database, annotate it and add it
    if hits >= 1:
        return response["hits"]["hits"][0]["_source"]
    else:
        return None


def scroll_index(
    client: OpenSearch, index: str, pagesize: int = 250, scroll_timeout="1m", **kwargs
):
    is_first = True
    scroll_id = None
    while True:
        # Scroll to next document
        if is_first:  # Initizize scroll
            result = client.search(
                index=index, scroll="1m", **kwargs, body={"size": pagesize}
            )
            is_first = False
        else:
            result = client.scroll(
                body={"scroll_id": scroll_id, "scroll": scroll_timeout}
            )
        scroll_id = result["_scroll_id"]
        hits = result["hits"]["hits"]
        # Stop after no more docs
        if not hits:
            break
        # Yield documents
        yield hits
