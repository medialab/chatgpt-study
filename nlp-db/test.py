import json
import random
from datetime import datetime

from opensearchpy import OpenSearch

from utils import scroll_index

host = "localhost"
port = 9200
auth = ("admin", "admin")  # For testing only. Don't store credentials in code.
index_name = "test"
messages = ["greetings", "what do you want", "hello world", "hey girl hey"]


def main():
    # Create the client with SSL/TLS enabled, but hostname verification disabled.
    client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_compress=True,  # enables gzip compression for request bodies
        http_auth=auth,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )

    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)
    index_body = {"settings": {"index": {"number_of_shards": 4}}}
    response = client.indices.create(index_name, body=index_body)
    print("\nCreating index")
    print(response)

    for _ in range(20):
        client.index(
            index=index_name,
            body={
                "msg": random.choice(messages),
                "time": datetime.utcnow(),
            },
        )

    # Pull all documents from the index
    output = []
    for _, entry in scroll_index(client=client, index=index_name):
        output.append(entry)

    print(
        f"Writing {len(output)} documents from index '{index_name}' to 'export.json' file."
    )
    with open("export.json", "w") as of:
        json.dump(output, of, indent=4)


if __name__ == "__main__":
    main()
