import re
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

    if len(str(site_data['id'])) != 24:
        result['message'] = 'Site id is invalid'
        result['status'] = False

    if result['status'] == True:

        if 'alias_domains' in site_data.keys() and type(site_data['alias_domains']) is str:
            site_data['alias_domains'] = site_data['alias_domains'].splitlines()

        if 'dev_domain' in site_data.keys() and len(site_data['dev_domain']) > 0:
            finder = load_site({
            '$and': [
                {
                    '$or': [
                        {'name': site_data['name']},
                        {'domain': site_data['domain']},
                        {'dev_domain': site_data['dev_domain']}
                    ],
                },
                {
                '_id': {
                        '$ne': ObjectId(site_data['id'])
                    }
                }
            ]
            })

        else:
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

            site = dict()
            site.update(modify_site)
            site.update(site_data)

            if modify_site['domain'] != site['domain']:
                # Domain change deteced, we have to modify config file
                # TO-DO: Autodeploy changes
                pass

            site['updated_at'] = utils.now()

            sites = app.db['sites']

            site = site_model(site)
            sites.update_one({'_id': ObjectId(_id) }, { '$set': site }, { '$unset': { 'server': None, 'recipe': None } })

            result['status'] = True
            result['message'] = f"Site {site['name']} modified"

        else:
            param_found = ''
            if finder['name'] == site_data['name']:
                param_found = f"with name {site_data['name']}"
            if len(param_found)==0 and finder['domain'] == site_data['domain']:
                param_found = f"with same domain {site_data['domain']}"
            if len(param_found)==0 and finder['dev_domain'] == site_data['dev_domain']:
                param_found = f"with same dev domain {site_data['dev_domain']}"

            result['status'] = False
            result['message'] = f"Site {param_found} already exists"

    return result


def insert(site_data):
    result = validator(site_data)

    if result['status'] == True:

        if 'alias_domains' in site_data.keys() and type(site_data['alias_domains']) is str:
            site_data['alias_domains'] = site_data['alias_domains'].splitlines()

        site = site_model(site_data)

        finder = load_site({
        '$or': [
                {'name': site['name']},
                {'domain': site['domain']},
                {'dev_domain': site_data['dev_domain']}
            ]
        })

        if type(finder) is not dict:

            site_data.pop('id', None)
            site_data.pop('updated_at', None)

            site['created_at'] = utils.now()
            site['creator'] = app.config['user']['_id']

            sites = app.db['sites']
            sites.insert_one(site)
            result['status'] = True
            result['message'] = f"Site {site['name']} created"
        else:

            param_found = ''
            if finder['name'] == site['name']:
                param_found = f"with name {site['name']}"
            if len(param_found)==0 and finder['domain'] == site['domain']:
                param_found = f"with same domain {site['domain']}"
            if len(param_found)==0 and finder['dev_domain'] == site['dev_domain']:
                param_found = f"with same dev domain {site['dev_domain']}"

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

        if 'name' not in site_data.keys() or type(site_data['name']) is not str or len(site_data['name'])<2:
            result['message'] = f"'{str(site_data['name'])}' is not a valid site name"
            return result

        if 'recipe_id' not in site_data.keys() or type(site_data['recipe_id']) is not str or len(site_data['recipe_id'])!=24:
            result['message'] = f"Recipe id is required"
            return result

        if 'server_id' not in site_data.keys() or type(site_data['server_id']) is not str or len(site_data['server_id'])!=24:
            result['message'] = f"Server id is required"
            return result

        if 'domain' not in site_data.keys() or type(site_data['domain']) is not str or len(site_data['domain'])<4:
            result['message'] = f"Domain is required"
            return result

        # server validation
        server_data = servers.load_server({'id':site_data['server_id']})

        if type(server_data) is not dict or len(server_data) == 0:
            result['message'] = f"Server not found"
            return result

        # Domain name DNS validation
        #if not is_domain_on_server(site_data['domain'], server_data['ipv4']):
        #    result['message'] = f"Domain {site_data['domain']} is not redirected on selected server"
        #    return result

        # Domain name validation
        pre = re.compile(r'^(?=.{1,253}$)(?!.*\.\..*)(?!\..*)([a-zA-Z0-9-]{,63}\.){,127}[a-zA-Z0-9-]{1,63}$')
        if not pre.match(site_data['domain']):
            result['message'] = f"Domain name {site_data['domain']} is invalid"
            return result

        # Optional Dev domain name validation
        if 'dev_domain' in site_data.keys() and type(site_data['dev_domain']) is str and len(site_data['dev_domain'])>3 and not pre.match(site_data['dev_domain']):
            result['message'] = f"Dev domain name {site_data['dev_domain']} is invalid"
            return result

        # Optional Alias domains name validation
        if 'alias_domains' in site_data.keys() and type(site_data['alias_domains']) is str and len(site_data['alias_domains'])>3:

            for alias_domain in site_data['alias_domains'].splitlines():

                if len(alias_domain)<4 or not pre.match(alias_domain):
                    result['message'] = f"Alias domain name {alias_domain} is invalid"
                    return result

        # Recipe validation
        recipe_data = recipes.load_recipe({'id':site_data['recipe_id']})

        if type(recipe_data) is not dict or len(recipe_data) == 0:
            result['message'] = f"Recipe not found"
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
        'recipe_id': utils.eval_key('recipe_id', site_data),
        'publish': utils.eval_key('publish', site_data, 'bool'),
        'domain': utils.eval_key('domain', site_data),
        'dev_domain': utils.eval_key('dev_domain', site_data),
        'alias_domains': utils.eval_key('alias_domains', site_data, 'list'),
        'owner': utils.eval_key('owner', site_data),
        'creator': utils.eval_key('creator', site_data),
        'created_at': utils.eval_key('created_at', site_data),
        'updated_at': utils.eval_key('updated_at', site_data),
    }

    return site
