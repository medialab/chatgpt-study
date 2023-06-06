# =============================================================================
# MongoDB Database Queries
# =============================================================================
#
# PyMongo commands to query a collection in a MongoDB database.
#
def count_documents(collection):
    return collection.count_documents({})


def find_documents(collection, query):
    for match in collection.find(query):
        yield match
