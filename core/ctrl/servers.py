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
    return {'ssh_pub_key': 0, 'ssh_pw': 0}


def modify(server_data):
    result = validator(server_data)

    if 'id' not in server_data.keys():
        result['message'] = 'Need id to modify server'
        result['status'] = False

    else:

        if len(server_data['id']) != 24:
            result['message'] = 'Server id is invalid'
            result['status'] = False

        if result['status'] == True:

            if len(server_data['ipv6']) > 0:
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
            else:
                finder = load_server({
                '$and': [
                    {
                        '$or': [
                            {'name': server_data['name']},
                            {'ipv4': server_data['ipv4']}
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
                _id = server_data.pop('id', None)
                server_data.pop('creator', None)
                server_data.pop('created_at', None)

                server = dict()
                server.update(modify_server)
                server.update(server_data)

                server['updated_at'] = utils.now()

                servers = app.db['servers']

                server = server_model(server)
                servers.update_one({'_id': ObjectId(_id) }, { '$set': server })

                result['status'] = True
                result['message'] = f"Server {server['name']} modified"

            else:
                param_found = ''
                if finder['name'] == server_data['name']:
                    param_found = f"with name {server_data['name']}"
                if len(param_found)==0 and finder['ipv4'] == server_data['ipv4']:
                    param_found = f"with IPv4 {server_data['ipv4']}"
                if len(param_found)==0 and finder['ipv6'] == server_data['ipv6']:
                    param_found = f"with IPv6 {server_data['ipv6']}"
                result['status'] = False

                result['message'] = f"Server {param_found} already exists"

    return result


def insert(server_data):
    result = validator(server_data)

    if result['status'] == True:

        server = server_model(server_data)

        if len(server['ipv6']) > 0:
            finder = load_server({
            '$or': [
                    {'name': server['name']},
                    {'ipv4': server['ipv4']},
                    {'ipv6': server['ipv6']},
                ]
            })

        else:

            finder = load_server({
            '$or': [
                    {'name': server['name']},
                    {'ipv4': server['ipv4']}
                ]
            })

        if type(finder) is not dict:

            server_data.pop('id', None)
            server_data.pop('updated_at', None)

            server['created_at'] = utils.now()
            server['creator'] = app.config['user']['_id']

            servers = app.db['servers']
            servers.insert_one(server)
            result['status'] = True
            result['message'] = f"Server {server['name']} created"
        else:

            param_found = ''
            if finder['name'] == server['name']:
                param_found = f"with name {server['name']}"
            if len(param_found)==0 and finder['ipv4'] == server['ipv4']:
                param_found = f"with IPv4 {server['ipv4']}"
            if len(param_found)==0 and finder['ipv6'] == server['ipv6']:
                param_found = f"with IPv6 {server['ipv6']}"

            result['status'] = False
            result['message'] = f"Server {param_found} already exists"

    return result


def delete(server_data):
    result = {
        'status': False,
        'message': 'Need id to delete server',
        'server_data': server_data
    }

    if 'id' in server_data.keys():
        """ modify_server = load_server({
            '_id': ObjectId(server_data['id'])
        }, no_filter_pattern=True)
        """
        servers = app.db['servers']
        r = servers.delete_one({'_id': ObjectId(server_data['id'])})
        result['delete_status'] = r.deleted_count
        result['status'] = False if r.deleted_count == 0 else True
        result['message'] = 'Server delete error' if r.deleted_count == 0 else 'Server deleted'

    return result


def validator(server_data):
    result = {
        'status': False,
        'message': "Data error",
    }

    if type(server_data) is dict and 'ipv4' in server_data.keys() and 'name' in server_data.keys():

        if type(server_data['name']) != str or len(server_data['name'])<2:
            result['message'] = f"{server_data['name']} is not a valid server name"
            return result

        if utils.ip_valid(server_data['ipv4'])['version'] != 4:
            result['message'] = "Enter valid IPv4 address"
            return result

        if len(server_data['ipv6'])>0 and utils.ip_valid(server_data['ipv6'])['version'] != 6:
            result['message'] = "Enter valid IPv6 address"
            return result

        result['status'] = True

    return result


def server_model(server_data):
    if type(server_data) is not dict:
        server_data = {}

    server = {
        'name': utils.eval_key('name', server_data),
        'ipv4': utils.eval_key('ipv4', server_data, 'ipv4'),
        'ipv6': utils.eval_key('ipv6', server_data, 'ipv6'),
        'os': utils.eval_key('os', server_data),
        'provider': utils.eval_key('provider', server_data),
        'ssh_user': utils.eval_key('ssh_user', server_data),
        'ssh_pwd': utils.eval_key('ssh_pwd', server_data),
        'ssh_port': utils.eval_key('ssh_port', server_data),
        'ssh_key': utils.eval_key('ssh_key', server_data),
        'publish': utils.eval_key('publish', server_data, 'bool'),
        'use': utils.eval_key('use', server_data, 'bool'),
        'owner': utils.eval_key('owner', server_data),
        'creator': utils.eval_key('creator', server_data),
        'created_at': utils.eval_key('created_at', server_data),
        'updated_at': utils.eval_key('updated_at', server_data),
    }

    return server
