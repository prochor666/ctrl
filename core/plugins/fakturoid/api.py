from core.plugins.fakturoid import http_client
from core import app, utils
import copy
import json


# Lists

def invoices(config, data=None):
    return http_client.get_data(config, 'invoices', data)


def subjects(config, data=None):
    return http_client.get_data(config, 'subjects', data)


def expenses(config, data=None):
    return http_client.get_data(config, 'expenses', data)


def account(config, data=None):
    return http_client.get_data(config, 'account', data)



# Actions & details

def inovice_detail(config, data=None):
    return http_client.get_data(config, f"invoices/{data['id']}")


def inovice_edit(config, data=None):
    # patch
    return http_client.send_data(config, f"invoices/{data['id']}", data, 'patch')


def inovice_action(config, data=None):
    # patch
    return http_client.send_data(config, f"invoices/{data['id']}/fire", data, 'post')


def inovice_delete(config, data=None):
    # delete
    return http_client.send_data(config, f"invoices/{data['id']}", data, 'delete')


def inovice_new(config, data=None):
    return http_client.send_data(config, f"invoices", data, 'post')


def expense_detail(config, data=None):
    return http_client.get_data(config, f"expenses/{data['id']}")


def expense_edit(config, data=None):
    # patch
    return http_client.send_data(config, f"expenses/{data['id']}", data, 'patch')


def expense_action(config, data=None):
    # patch
    return http_client.send_data(config, f"expenses/{data['id']}/fire", data, 'post')


def expense_delete(config, data=None):
    # delete
    return http_client.send_data(config, f"expenses/{data['id']}", data, 'delete')


def expense_new(config, data=None):
    return http_client.send_data(config, f"expenses", data, 'post')


def subject_detail(config, data=None):
    return http_client.get_data(config, f"subjects/{data['id']}")


def subject_edit(config, data=None):
    # patch
    return http_client.send_data(config, f"subjects/{data['id']}", data, 'patch')


def subject_delete(config, data=None):
    # delete
    return http_client.send_data(config, f"subjects/{data['id']}", data, 'delete')


def subject_new(config, data=None):
    # post
    return http_client.send_data(config, f"subjects", data, 'post')


def sync(config, data=None):

    result = {
        'invoices': [],
        'subjects': [],
        'expenses': [],
    }

    root_keys = copy.copy(result).keys()

    for key in root_keys:

        first_page = http_client.get_data(config, key, {
            'page': 1
        })
        pages = http_client.parse_headers(first_page['headers'])
        result[key] = first_page['data']
        result[f"{key}_pages"] = pages

        if pages > 1:

            for current_page in range(1, pages+1):

                if current_page > 1:

                    temp = http_client.get_data(config, key, {
                        'page': current_page
                    })
                    result[key].extend(temp['data'])

        result[f"{key}_data_length"] = len(result[key])
        result['download'] = '/resource/fakturoid.json'

        utils.file_save(
            f"{app.config['filesystem']['resources']}/fakturoid.json", json.dumps(result))

    return result
