from bson.objectid import ObjectId
from core import app, data, utils
from core.ctrl import servers, recipes


def list_sites(filter_data):
    finder = {
        'collection': 'sites',
        'filter': filter_data,
    }
    return data.ex(finder)


def load_site(filter_data):
    finder = {
        'collection': 'sites',
        'filter': filter_data
    }
    return data.one(finder)


def modify(site_data):
    result = validator(site_data)

    if 'id' not in site_data.keys():
        result['message'] = 'Need id to modify site'
        result['status'] = False

    if len(site_data['id']) != 24:
        result['message'] = 'Site id is invalid'
        result['status'] = False

    if result['status'] == True:

        finder = load_site({
        '$and': [
            {
                '$or': [
                    {'name': site_data['name']},
                    {'domain': site_data['domain']}
                ],
            },
            {
            '_id': {
                    '$ne': ObjectId(site_data['id'])
                }
            }
        ]
        })

        modify_site = load_site({
            '_id': ObjectId(site_data['id'])
        })

        if type(finder) is not dict and type(modify_site) is dict:
            _id = site_data.pop('id', None)
            site_data.pop('creator', None)
            site_data.pop('created_at', None)

            site = {**modify_site, **site_data}

            site['updated_at'] = utils.now()

            sites = app.db['sites']

            site = site_model(site)
            sites.update_one({'_id': ObjectId(_id) }, { '$set': site })

            result['status'] = True
            result['message'] = f"Site {site['name']} modified"

        else:
            param_found = ''
            if finder['name'] == site_data['name']:
                param_found = f"with name {site_data['name']}"
            if len(param_found)==0 and finder['content'] == site_data['content']:
                param_found = f"with same content"

            result['status'] = False
            result['message'] = f"Site {param_found} already exists"

    return result


def insert(site_data):
    result = validator(site_data)

    if result['status'] == True:

        site = site_model(site_data)

        finder = load_site({
        '$or': [
                {'name': site['name']},
                {'domain': site['domain']}
            ]
        })

        if type(finder) is not dict:

            site_data.pop('id', None)
            site_data.pop('updated_at', None)

            site['created_at'] = utils.now()
            site['creator'] = app.config['user']['_id']

            sites = app.db['sites']
            #sites.insert_one(site)
            result['status'] = True
            result['message'] = f"Site {site['name']} created"
        else:

            param_found = ''
            if finder['name'] == site['name']:
                param_found = f"with name {site['name']}"
            if len(param_found)==0 and finder['content'] == site['content']:
                param_found = f"with same content"

            result['status'] = False
            result['message'] = f"Site {param_found} already exists"

    return result


def delete(site_data):
    result = {
        'status': False,
        'message': 'Need id to delete site',
        'site_data': site_data
    }

    if 'id' in site_data.keys():
        sites = app.db['sites']
        r = sites.delete_one({'_id': ObjectId(site_data['id'])})
        result['delete_status'] = r.deleted_count
        result['status'] = False if r.deleted_count == 0 else True
        result['message'] = 'Site delete error' if r.deleted_count == 0 else 'site deleted'

    return result


def validator(site_data):
    result = {
        'status': False,
        'message': "Data error",
    }

    if type(site_data) is dict:

        if 'name' in site_data.keys() or type(site_data['name']) is not str or len(site_data['name'])<2:
            result['message'] = f"'{str(site_data['name'])}' is not a valid site name"
            return result

        if 'recipes' in site_data.keys() or type(site_data['recipes']) is not dict or len(site_data['recipes'])<1:
            result['message'] = f"At least on recipe is required"
            return result

        if 'server_id' in site_data.keys() or type(site_data['server_id']) is not str or len(site_data['server_id'])!=24:
            result['message'] = f"Server id is required"
            return result

        if 'domain' in site_data.keys() or type(site_data['domain']) is not str or len(site_data['domain'])<1:
            result['message'] = f"Domain is required"
            return result

        # server validation
        server_data = servers.load_server({'id':site_data['server_id']})

        if type(server_data) is not dict or len(server_data) == 0:
            result['message'] = f"Server not found"
            return result

        # domain name validation
        if not is_domain_on_server(site_data['domain'], server_data['ipv4']):
            result['message'] = f"Domain {site_data['domain']} is not redirected on selected server"
            return result

        result['status'] = True

    return result


def is_domain_on_server(domain, server_ip):
    dns_records = utils.domain_dns_info(domain, ['A', 'CNAME', 'ALIAS'])

    if len(dns_records) > 0:

        for r in dns_records:
            if r['type'] == 'A' and r['value'] == server_ip:
                return True

            if r['type'] in ['CNAME','ALIAS']:
                dns_records_cn = utils.domain_dns_info(r['value'], ['A'])

                for x in dns_records_cn:
                    if x['type'] == 'A' and x['value'] == server_ip:
                        return True

    return False


def site_model(site_data):
    if type(site_data) is not dict:
        site_data = {}

    site = {
        'name': utils.eval_key('name', site_data),
        'description': utils.eval_key('description', site_data),
        'server_id': utils.eval_key('server_id', site_data),
        'recipes': utils.eval_key('recipes', site_data, 'dict'),
        'publish': utils.eval_key('publish', site_data, 'bool'),
        'domain': utils.eval_key('domain', site_data),
        'dev_domain': utils.eval_key('domains', site_data),
        'alias_domains': utils.eval_key('alias_domains', site_data, 'list'),
        'owner': utils.eval_key('owner', site_data),
        'creator': utils.eval_key('creator', site_data),
        'created_at': utils.eval_key('created_at', site_data),
        'updated_at': utils.eval_key('updated_at', site_data),
    }

    return site
