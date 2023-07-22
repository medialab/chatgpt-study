from opensearchpy import OpenSearch
from datetime import datetime
import random

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


if __name__ == "__main__":
    main()
