from bson.objectid import ObjectId
from core import app, data, utils


def list_servers(filter_data):
    finder = {
        'collection': 'servers',
        'filter': filter_data,
        'exclude': filter_server_pattern()
    }
    return data.ex(finder)


def load_server(filter_data, no_filter_pattern=False):
    finder = {
        'collection': 'servers',
        'filter': filter_data
    }
    if not no_filter_pattern:
        finder['exclude'] = filter_server_pattern()
    return data.one(finder)


def filter_server_pattern():
    return {'ssh_private_key': 0}


def delete(server_data):
    result = {
        'status': False,
        'message': 'Need id to delete server',
        'server_data': server_data
    }

    if 'id' in server_data.keys():
        modify_server = load_server({
            '_id': ObjectId(server_data['id'])
        }, no_filter_pattern=True)

        servers = app.db['servers']
        servers.delete_one({'id': ObjectId(server_data['id'])})

        result['modify_server'] = str(modify_server) if type(modify_server) is str else data.collect_one(modify_server)

    return result


def modify(server_data):
    result = validator(server_data)

    if 'id' not in server_data.keys():
        result['message'] = 'Need id to modify server'
        result['status'] = False

    if result['status'] == True:

        finder = load_server({
        '$and': [
            {
                '$or': [
                    {'name': server_data['name']},
                    {'ipv4': server_data['ipv4']},
                    {'ipv6': server_data['ipv6']}
                ],
            },
            {
            '_id': {
                    '$ne': ObjectId(server_data['id'])
                }
            }
        ]
        })

        modify_server = load_server({
            '_id': ObjectId(server_data['id'])
        }, no_filter_pattern=True)

        if type(finder) is not dict and type(modify_server) is dict:

            server = {**modify_server, **server_data}
            servers = app.db['servers']

            server = server_model(server)
            servers.update_one({'_id': ObjectId(server_data['id']) }, { '$set': server })

            result['status'] = True
            result['message'] = f"Server {server['name']} modified"

        else:
            result['message'] = "Server name or IPv4/IPv6 already exists"

    return result


def insert(server_data):
    result = validator(server_data)

    if result['status'] == True:

        server = server_model(server_data)
        finder = load_server({
        '$or': [
                {'name': server['name']},
                {'ipv4': server['ipv4']},
                {'ipv6': server['ipv6']},
            ]
        })

        if type(finder) is not dict:
            servers = app.db['servers']
            servers.insert_one(server)
            result['status'] = True
            result['message'] = f"Server {server['name']} created"
        else:
            result['status'] = False
            result['message'] = "Server name or IPv4/IPv6 already exists"

    return result


def validator(server_data):
    result = {
        'status': False,
        'message': "Data error",
    }

    if type(server_data) is dict and 'ipv4' in server_data.keys() and 'name' in server_data.keys():

        if type(server_data['ipv4']) != str:
            result['message'] = "Enter valid IPv4 address"
            return result

        if type(server_data['name']) != str:
            result['message'] = f"{server_data['name']} is not a valid server name"
            return result

        result['status'] = True

    return result


def server_model(server_data):
    if type(server_data) is not dict:
        server_data = {}

    server = {
        'name': utils.eval_key('name', server_data),
        'ipv4': utils.eval_key('ipv4', server_data),
        'ipv6': utils.eval_key('ipv6', server_data),
        'os': utils.eval_key('os', server_data),
        'provider': utils.eval_key('provider', server_data),
        'ssh_user': utils.eval_key('ssh_user', server_data),
        'ssh_pwd': utils.eval_key('ssh_pwd', server_data),
        'ssh_port': utils.eval_key('ssh_port', server_data),
        'ssh_dir': utils.eval_key('ssh_dir', server_data),
        'ssh_pub_key': utils.eval_key('ssh_pub_key', server_data),
        'publish': utils.eval_key('publish', server_data, 'bool'),
        'use': utils.eval_key('use', server_data, 'bool'),
        'owner': utils.eval_key('owner', server_data),
        'creator': utils.eval_key('creator', server_data),
        'created_at': utils.eval_key('created_at', server_data),
        'updated_at': utils.eval_key('updated_at', server_data),
    }

    return server
