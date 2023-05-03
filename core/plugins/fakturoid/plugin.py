import json
from core.plugins.fakturoid import api


def configure():
    with open('core/plugins/fakturoid/config.json') as config:
        data = json.load(config)
        return data
    return {}


def authform():
    config = configure()

    url = f"https://app.fakturoid.cz/api/v2/accounts/{config['slug']}"
    auth = (config['email'], config['apiKey'])
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': f"{config['app']} ({config['email']})"
    }

    return {
        'enabled': config['enabled'],
        'url': url,
        'auth': auth,
        'headers': headers
    }


def load(api_method='none', data=None):

    result = False

    if api_method != 'none' and api_method in dir(api):

        config = authform()
        if config['enabled'] == False:
            return False

        result = getattr(api, api_method)(config, data)

    return result
