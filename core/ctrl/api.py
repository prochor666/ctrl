import json
from flask import render_template
from core import app, data, utils
from core.ctrl import device, network as net, mailer, users as usr, servers as srv, recipes as rcps, sites as sts
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
    with open('json/iso-3166-1.json') as countries:
        return json.load(countries)
    return []


def domain_info(data_pass=None):
    result = {'status': False, 'message': 'Data error', 'data': {}}
    record_filter = []

    if 'filter' in data_pass.keys() and type(data_pass['filter']) is list and len(data_pass['filter'])>0:
        record_filter = data_pass['filter']

    if 'filter' in data_pass.keys() and type(data_pass['filter']) is str and len(data_pass['filter'])>0:
        record_filter = data_pass['filter'].split(',')



    if 'domain' in data_pass.keys():
        result['data'] = utils.domain_dns_info(str(data_pass['domain']), record_filter)
        if len(result['data'])>0:
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


def users(data_pass=None):

    data_filter = utils.apply_filter(data_pass)

    u = usr.list_users(data_filter)
    result = {
        'status': False,
        'message': str(u) if type(u) is str else "No users",
        'users': [],
        'count': 0 if type(u) is str or u == None else u.count()
    }
    if result['count'] > 0:
        result['status'] = True
        result['message'] = f"Found users: {result['count']}"

    if app.mode == 'http':
        for user in data.collect(u):
            if user['username'] == 'system':
                result['count'] = result['count'] - 1
            else:
                result['users'].append(user)
    else:
        result['users'] = data.collect(u)

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


def soft_recovery(data_pass):
    return usr.recover(data_pass, True)


def full_recovery(data_pass):
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


# Recipes
def recipes(data_pass=None):

    data_filter = utils.apply_filter(data_pass)

    u = rcps.list_recipes(data_pass)
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
