from flask import render_template
import json, os
from core.ctrl import device, network as net, auth, secret, utils


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
    return auth.login(data_pass)


def register(data_pass=None):
    return auth.register(data_pass)


def token(data_pass=None):
    return secret.token_core()


def countries(data_pass=None):
    with open('json/iso-3166-1.json') as countries:
        return json.load(countries)
    return []


def ip(data_pass=None):
    return net.device_ip()


def scan(data_pass=None):

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


def headers(data_pass=None):
    return data_pass['config']['headers']


def test(data_pass=None):
    return {'test':'Ok'}