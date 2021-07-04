from bson.objectid import ObjectId
from core import app, data


def list_servers(finder={}):
    finder['collection'] = 'servers'
    finder['exclude'] = filter_server_pattern()
    return data.ex(finder)


def load_server(finder, no_filter_pattern=False):
    finder['collection'] = 'servers'
    return data.one(finder, filter_server_pattern() if no_filter_pattern else None )


def filter_server_pattern():
    return {'acl': 0}