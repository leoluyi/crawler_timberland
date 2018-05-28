from crawler_timberland.crawler import upsert_timberland
from crawler_timberland.io import mongo_con
import os
import re
from dotenv import load_dotenv
load_dotenv('.env')

# Variables of mongodb
MONGODB_HOST = os.environ.get("MONGODB_HOST", "localhost")
MONGODB_PORT = int(os.environ.get("MONGODB_PORT", 27017))
MONGODB_DB = os.environ.get("MONGODB_DB", "")
MONGODB_USER = os.environ.get("MONGODB_USER", "")
MONGODB_PWD = os.environ.get("MONGODB_PWD", "")
MONGODB_COLLECTION='timberland'


def main():
    with mongo_con(MONGODB_HOST, MONGODB_PORT, MONGODB_DB, MONGODB_USER, MONGODB_PWD) as db:
        upsert_timberland(db, MONGODB_COLLECTION, product_number='product_number')


if __name__ == '__main__':
    main()
