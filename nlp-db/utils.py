from typing import Generator

import casanova
from opensearchpy import OpenSearch
from tqdm import tqdm

from constants import HOST, INDEX_BODY, PORT


def create_client(authentication: tuple) -> OpenSearch:
    client = OpenSearch(
        hosts=[{"host": HOST, "port": PORT}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=authentication,
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


def create_index(client: OpenSearch, index_name: str):
    # Create an index with non-default settings.
    response = client.indices.create(index_name, body=INDEX_BODY)
    print("\nCreating index:")
    print(response)


def yield_data(datafile: str, reverse: bool = False) -> Generator[dict, None, None]:
    print("\nCounting data file length...")
    total = casanova.reader.count(datafile)
    with open(datafile, "r") as f:
        if reverse:
            reader = casanova.reverse_reader(f)
        else:
            reader = casanova.reader(f)
        fieldnames = reader.fieldnames
        print("\nProcessing documents...")
        if isinstance(fieldnames, list):
            for row in tqdm(
                reader,
                total=total,
            ):
                yield {k: v for k, v in list(zip(fieldnames, row))}
        else:
            raise TypeError


def make_token_id(sent_id: int | str, token_id: int | str):
    return f"s{sent_id}t{token_id}"


def scroll_index(
    client: OpenSearch, index: str, pagesize=250, scroll_timeout="15m", **kwargs
):
    """
    Helper to iterate ALL values from a single index
    Yields all the documents.
    """
    is_first = True
    scroll_id = None
    while True:
        # Scroll next
        if is_first:  # Initialize scroll
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
        # Yield each entry
        yield from ((hit["_id"], hit["_source"]) for hit in hits)
