import json
import re
from flask import render_template
from core import app, data, utils
from core.ctrl import device, network as net, mailer, users as usr, servers as srv, recipes as rcps, sites as sts, billing, remote, monit
from bson import json_util


def about(data_pass=None):
    data = {
        'OS': device.sys_info(),
        'Network': device.network_info(),
        'CPU': device.cpu_info(),
        'Memory': device.memory_info(),
        'Disk': device.disk_info()
    }
    return render_template('about.html', data=data)


def system(data_pass=None):
    return device.sys_info()


def network(data_pass=None):
    return device.network_info()


def cpu(data_pass=None):
    return device.cpu_info()


def memory(data_pass=None):
    return device.memory_info()


def disk(data_pass=None):
    return device.disk_info()


def login(data_pass=None):
    return {'status': True, 'message': "Logged in"}


def is_email(data_pass):
    if 'email' in data_pass.keys():
        return mailer.check_email(data_pass['email'])
    return False


def countries(data_pass=None):
    try:
        with open('json/iso-3166-1.json') as countries:
            return json.load(countries)
    except Exception as error:
        return []


def ssh_keys(data_pass=None):

    result = {
        'status': True,
        'message': 'Keys list',
        'data': utils.list_ssh_keys()
    }

    return result


def domain_info(data_pass=None):
    result = {'status': False, 'message': 'Data error', 'data': None, 'pass': data_pass}
    record_filter = []

    if 'filter' in data_pass.keys():

        if type(data_pass['filter']) is list and len(data_pass['filter']) > 0:
            record_filter = data_pass['filter']

        if type(data_pass['filter']) is str and len(data_pass['filter']) > 0:
            record_filter = data_pass['filter'].split(',')


    if 'domain' in data_pass.keys():
        result['data'] = utils.domain_dns_info(
            str(data_pass['domain']), record_filter)
        if len(result['data']) > 0:
            result['message'] = f"Domain {str(data_pass['domain'])} DNS records found"
            result['status'] = True

    return result


def client_ip(data_pass=None):
    return app.config['client_ip']


def ip(data_pass=None):
    return net.device_ip()


def scan_ip(data_pass=None):

    result = {
        'status': False,
        'message': "Data error"
    }

    if 'ip' in data_pass.keys():
        if 'ports' in data_pass.keys():
            scan = net.scan_ip(data_pass['ip'], data_pass['ports'].split(','))
        else:
            scan = net.scan_ip(data_pass['ip'])

        result['status'] = scan['scan_status']
        result['message'] = scan['scan_result']
        result['ports'] = scan['ports']
        result['time'] = scan['time']
    return result


def test(data_pass=None):
    return {
        'test': "Ok",
        'mode': app.mode
    }


def db_check(data_pass=None):
    return utils.database_check()


def get_enums(data_pass=None):
    return app.config['enum_options']


def users(data_pass=None):

    data_filter = utils.apply_filter(data_pass)
    ftype = None
    if 'filter' in data_pass.keys() and type(data_pass['filter']):
        ftype = type(data_pass['filter'])

    u = usr.list_users(data_filter)
    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No users",
        'users': [],
        'count': 0 if type(u) is str or u == None else u.count()
    }
    if result['count'] > 0:
        result['status'] = True

        if app.mode == 'http':
            for user in u:
                if user['username'] == 'system':
                    result['count'] = result['count'] - 1
                else:
                    result['users'].append(data.collect_one(user))
        else:
            result['users'] = data.collect(u)

        result['message'] = f"Found users: {result['count']}"

    return result


def get_system_user(data_pass=None):
    return usr.system_user()


def activate_user(data_pass=None):
    return usr.activate(data_pass)


def create_user(data_pass=None):
    result = usr.insert(data_pass)
    return result


def modify_user(data_pass=None):
    result = usr.modify(data_pass)
    return result


def delete_user(data_pass=None):
    result = usr.delete(data_pass)
    return result


def soft_recovery(data_pass=None):
    return usr.recover(data_pass, True)


def full_recovery(data_pass=None):
    return usr.recover(data_pass, False)


def servers(data_pass=None):

    data_filter = utils.apply_filter(data_pass)

    u = srv.list_servers(data_filter)
    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No servers",
        'servers': [],
        'count': 0 if type(u) is str or u == None else u.count()
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found servers: {result['count']}"
        result['servers'] = data.collect(u)

    return result


def create_server(data_pass=None):
    result = srv.insert(data_pass)
    return result


def modify_server(data_pass=None):
    result = srv.modify(data_pass)
    return result


def delete_server(data_pass=None):
    result = srv.delete(data_pass)
    return result


def test_connection(data_pass=None):
    result = {
        'status': False,
        'message': 'Data error',
        'shell': []
    }

    if 'id' in data_pass.keys() and len(data_pass['id']) > 0:
        result = remote.test_connection(data_pass['id'])

    return result


def install_monitoring_service(data_pass=None):
    result = {
        'status': False,
        'message': 'Data error',
        'shell': []
    }

    if 'id' in data_pass.keys() and len(data_pass['id']) > 0:
        result = remote.install_monitoring_service(data_pass['id'])

    return result


def deploy(data_pass=None):
    result = {
        'status': False,
        'message': 'Data error',
        'data': []
    }

    if 'id' in data_pass.keys() and type(data_pass['id']) is str and len(data_pass['id']) > 0:
        result = remote.deploy(data_pass['id'])

    return result


def validate_domain(data_pass=None):
    result = {
        'status': False,
        'message': 'Data error',
    }

    if 'domain' in data_pass.keys() and type(data_pass['domain']) is str and len(data_pass['domain']) > 0:
        pre = re.compile(
            r'^(?=.{1,253}$)(?!.*\.\..*)(?!\..*)([a-zA-Z0-9-]{,63}\.){,127}[a-zA-Z0-9-]{1,63}$')
        if not pre.match(data_pass['domain']):
            result['message'] = f"Domain name {data_pass['domain']} is invalid"
        else:
            result['status'] = True
            result['message'] = f"Domain name {data_pass['domain']} is valid"

    return result


# Recipes
def recipes(data_pass=None):

    data_filter = utils.apply_filter(data_pass)

    u = rcps.list_recipes(data_filter)
    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No recipes",
        'recipes': [],
        'count': 0 if type(u) is str or u == None else u.count()
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found recipes: {result['count']}"
        result['recipes'] = data.collect(u)

    return result


def create_recipe(data_pass=None):
    result = rcps.insert(data_pass)
    return result


def modify_recipe(data_pass=None):
    result = rcps.modify(data_pass)
    return result


def delete_recipe(data_pass=None):
    result = rcps.delete(data_pass)
    return result


# Sites
def sites(data_pass=None):

    data_filter = utils.apply_filter(data_pass)

    u = sts.list_sites(data_filter)
    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No sites",
        'sites': [],
        'count': 0 if type(u) is str or u == None else u.count()
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found sites: {result['count']}"

        _sites = data.collect(u)
        sites = []
        # Map servers and recipes, to be more complex
        for site_data in _sites:
            site_data['server'] = data.collect_one(
                srv.load_server({'id': site_data['server_id']}))
            site_data['recipe'] = data.collect_one(
                rcps.load_recipe({'id': site_data['recipe_id']}))
            sites.append(site_data)

        result['sites'] = sites

    return result


def create_site(data_pass=None):
    result = sts.insert(data_pass)
    return result


def modify_site(data_pass=None):
    result = sts.modify(data_pass)
    return result


def delete_site(data_pass=None):
    result = sts.delete(data_pass)
    return result


# Monitoring
def monitor_server(data_pass=None):
    if type(data_pass) is dict and 'id' in data_pass:
        return monit.survey(data_pass['id'])

    return {
        'status': False,
        'message': f"Server id is missing",
        'data': []
    }


def monitor(data_pass=None):
    cache_file = f"{app.config['filesystem']['resources']}/monitoring.json"

    try:
        with open(cache_file) as dump:
            result = json.load(dump)
            result['resource'] = 'cache'
    except Exception as error:
        result = monitor_servers(data_pass)
        result['resource'] = 'direct'

    return result


def monitor_servers(data_pass=None):
    result = {
        'status': False,
        'message': f"Monitoring results",
        'data': []
    }
    u = srv.list_servers({
            'publish': True,
            'use': True
    })
    count = 0 if type(u) is str or u == None else u.count()

    if count > 0:
        servers = data.collect(u)

        for server in servers:
            result['data'].append(monit.survey(server['_id']))

        result['status'] = True

        # Cache data file localy
        utils.file_save(f"{app.config['filesystem']['resources']}/monitoring.json",
                        json.dumps(result))

    return result


# Billing
def invoices(data_pass=None):
    result = billing.load_invoices(data_pass)
    return result
