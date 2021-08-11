from bson.objectid import ObjectId
from core import app, utils


def ex(finder={}):
    try:
        _ = proxy(finder)
        return _['data_source'].find(_['filter'], _['exclude']).sort(_['sort'][0], _['sort'][1])

    except Exception as e:
        return f"Database server error {str(e)}"


def one(finder={}):
    try:
        _ = proxy(finder)
        return _['data_source'].find_one(_['filter'], _['exclude'])

    except Exception as e:
        return f"Database server error {str(e)}"


def collect_one(document):
    document['_id'] = str(document['_id'])
    if 'creator' in document:
        document['creator'] = str(document['creator'])
    if 'owner' in document:
        document['owner'] = str(document['owner'])

    return document


def collect(find_result):
    result = []
    for document in find_result:
        result.append(collect_one(document))
    return result


def proxy(finder):
    col = finder.get('collection')
    data_source = app.db[col]
    if type(finder) is dict:
        _filter = finder.get('filter', None)
        _exclude = finder.get('exclude', None)
        _sort = finder.get('sort', ['Id', 1])
        _from_str = {
            'asc': 1,
            'desc': -1
        }

        if 'id' in _filter:
            _filter['_id'] = ObjectId(_filter.pop('id'))

        if type(_sort) is list and len(_sort) == 2:
            if type(_sort[1]) is str and _sort[1].lower() in _from_str.keys():
                _sort[1] = _from_str[_sort[1]]

        return {
            'data_source': data_source,
            'filter': _filter,
            'exclude': _exclude,
            'sort': _sort,
        }
