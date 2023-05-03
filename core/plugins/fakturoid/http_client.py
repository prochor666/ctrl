import json
import requests
import urllib


def get_data(config, endpoint, data_filter=None):

    url = f"{config['url']}/{endpoint}.json"

    if type(data_filter) is dict:
        url += f"?{urllib.parse.urlencode(data_filter, doseq=False)}"

    response = requests.get(
        url, auth=config['auth'], headers=config['headers'])

    if response.status_code == 200:
        data = json.loads(response.text)
    else:
        data = []

    return {
        'headers': dict(response.headers),
        'status_code': response.status_code,
        'request_url': url,
        'data_len': len(data),
        'data': data
    }


def send_data(config, endpoint, data=None, action='post'):

    config['url'] += f"/{endpoint}.json"
    expected_status_code = [200]

    if action=='post':
        response = requests.post(
            config['url'], auth=config['auth'], headers=config['headers'], data=data)
        expected_status_code = [200, 201]

    if action=='patch':
        response = requests.patch(
            config['url'], auth=config['auth'], headers=config['headers'], data=data)
        expected_status_code = [200]

    if action == 'delete':
        response = requests.delete(
            config['url'], auth=config['auth'], headers=config['headers'], data=data)
        expected_status_code = [204]

    if response.status_code in expected_status_code:
        data = json.loads(response.text)
    else:
        data = []

    return {
        'headers': dict(response.headers),
        'status_code': response.status_code,
        'request_url': config['url'],
        'data': json.loads(response.text)
    }


def parse_headers(headers):

    pages = 1

    if 'Link' in headers:
        links = headers['Link'].split(',')

        for index in links:
            link = parse_link_by_rel(index)

            if link[0] == 'last':
                pages = int(link[1])

    return pages


def parse_link_by_rel(link):
    pattern = link.replace('<', '').replace('>', '').replace('"', '').split(';')
    url = pattern[0]
    page = int(pattern[0].split('?')[1].split('=')[1])
    rel = pattern[1].split('=')[1]

    return [rel, page]
