import pymongo


def connect(db):
    client = pymongo.MongoClient(db['host'], db['port'], serverSelectionTimeoutMS=1000)
    return client


def init(db):
    return True