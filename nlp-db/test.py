import json
import random
import unittest
from datetime import datetime
from tqdm import tqdm

from utils import create_client, scroll_index


host = "localhost"
port = 9200
auth = ("admin", "admin")  # For testing only. Don't store credentials in code.
index_name = "test"
messages = ["greetings", "what do you want", "hello world", "hey girl hey"]


mappings = {
    "properties": {
        "msg": {"type": "text"},
        "time": {"type": "date"},
    }
}


class TestInsert(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_client(authentication=auth)

    def test_insert(self):
        print("\nTEST INSERT")

        # Create the test index
        if self.client.indices.exists(index=index_name):
            self.client.indices.delete(index=index_name)
        index_body = {
            "settings": {"index": {"number_of_shards": 4}},
            "mappings": mappings,
        }
        self.client.indices.create(index_name, body=index_body)

        # Insert documents to the test index
        for _ in tqdm(range(20), total=20):
            self.client.index(
                index=index_name,
                body={
                    "msg": random.choice(messages),
                    "time": datetime.utcnow(),
                },
            )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestInsert("test_insert"))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
