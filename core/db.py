import pymongo


def connect(db_config):
    client = pymongo.MongoClient(
        db_config['host'], db_config['port'], serverSelectionTimeoutMS=1000)
    return client


def init(db):
    return True
