import pymongo


def connect(db_config):
    client = pymongo.MongoClient(
        db_config['host'], db_config['port'], serverSelectionTimeoutMS=2000)
    return client


def init(dbclient):
    db = dbclient.ctrl
    return db
