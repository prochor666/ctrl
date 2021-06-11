from flask import render_template
import json, os
from core import utils
from core.ctrl import device, network as net, auth, secret


def about(app, data_pass=None):
    data = {
        'OS': device.sys_info(),
        'Network': device.network_info(),
        'CPU': device.cpu_info(),
        'Memory': device.memory_info(),
        'Disk': device.disk_info()
    }
    return render_template('about.html', data=data)


def system(app, data_pass=None):
    return device.sys_info()


def network(app, data_pass=None):
    return device.network_info()


def cpu(app, data_pass=None):
    return device.cpu_info()


def memory(app, data_pass=None):
    return device.memory_info()


def disk(app, data_pass=None):
    return device.disk_info()


def login(app, data_pass=None):
    return auth.login(data_pass)


def register(app, data_pass=None):
    return auth.register(data_pass)


def token(app, data_pass=None):
    return secret.token_core()


def countries(app, data_pass=None):
    with open('json/iso-3166-1.json') as countries:
        return json.load(countries)
    return []


def client_ip(app, data_pass=None):
    return app.config['client_ip']


def ip(app, data_pass=None):
    return net.device_ip()


def scan_ip(app, data_pass=None):

    result = {
        'status': False,
        'message': 'Data error'
    }

    if 'ip' in data_pass:
        scan = net.scan_ip(data_pass['ip'])
        result['status'] = scan['scan_status']
        result['message'] = scan['scan_result']
        result['ports'] = scan['ports']
        result['time'] = scan['time']

    return result


def headers(app, data_pass=None):
    return app.config['headers']


def test(app, data_pass=None):
    return {'test':'Ok'}
