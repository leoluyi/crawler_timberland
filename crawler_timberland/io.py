from pymongo import MongoClient
from contextlib import contextmanager


@contextmanager
def mongo_con(host, port, collection, user=None, pwd=None):
    try:
        client = MongoClient(host=host, port=port)
        db = client[collection]
        if user:
            db.authenticate(user, pwd)
            print('Authenticated!')

        yield db
    finally:
        client.close()
