import json
import os


def locate_dirs():
    return {'templates': 'templates', 'json': 'json', 'static': 'static'}


def app_config():
    app_dirs = locate_dirs()
    with open(app_dirs['json']+'/app.json') as config:
        data = json.load(config)
        data['dirs'] = app_dirs

        # with open(app_dirs['json']+'/iso-3166-1.json') as countries:
        #    data['countries'] = json.load(countries)
        for key, value in data['filesystem'].items():
            data['filesystem'][key] = value.replace('/', os.path.sep)
        return data

    return {}


def configure():
    return app_config()


def smtp_config():
    app_dirs = locate_dirs()
    with open(app_dirs['json']+'/smtp.json') as smtp:
        data = json.load(config)
        return data

    return False
