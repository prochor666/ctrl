import os, json
from core import utils, initialize as app
from core.ctrl import secret


def authorization_level(headers):
    result = False

    return result


def login(data_pass=None):
    result = {
        'message': 'Auth failed',
        'username': '',
        'status': False
    }

    if 'auth_token' in data_pass.keys():
        username = get_user_from_token(data_pass['auth_token'])

        if len(username) > 0:
            user_data = get_user_from_secret_file(username)
            secret_key_check = hash_user(user_data)

            if 'username' in user_data.keys() and 'pwd' in user_data.keys() and data_pass['auth_token'] == user_data['pwd'] and secret_key_check == user_data['secret']:
                result['message'] = 'Auth ok'
                result['username'] = username
                result['status'] = True

    return result


def send_auth_code():
    return {}


def disable_user(username):
    user_data = get_user_from_secret_file(username)
    token_file_name = get_token_file_name(user_data['pwd'])

    if os.path.isfile(token_file_name):
        os.remove(token_file_name)


def get_secret_file_name(username):
    storage = os.path.join(utils.app_root(), app.config['filesystem']['seccets'])
    secret_file_name = os.path.join(storage, username+'.secret')
    return secret_file_name


def get_token_file_name(token):
    storage = os.path.join(utils.app_root(), app.config['filesystem']['auth'])
    token_file = os.path.join(storage, token)
    return token_file


def get_user_from_token(token):
    token_file = get_token_file_name(token)
    result = ''

    if os.path.isfile(token_file):
        fh = open(token_file, "r")
        result = fh.read().strip()
        fh.close()

    return str(result)


def get_user_from_secret_file(username):
    user_data = {}
    secret_file_name = get_secret_file_name(username)

    if os.path.isfile(secret_file_name):
        with open(secret_file_name) as user_handle:
            user_data = json.load(user_handle)

    return user_data


def hash_user(user_data):
    secret_key = secret.create_secret({'email': user_data['email'], 'username': user_data['username'], 'pwd': user_data['pwd']})
    return secret_key


def register_user(data_pass=None):

    result = {
        'status': False,
        'message': 'Data error',
        'secret_file': None
    }

    if type(data_pass) is dict and 'email' in data_pass.keys() and 'username' in data_pass.keys():

        if type(data_pass['email']) != str:
            result['message'] = 'Enter valid email address'
            return result

        elif not utils.is_email(data_pass['email']):
            result['message'] = '"' + str(data_pass['email']) + '" is not a valid email address'
            return result

        if type(data_pass['username']) != str:
            result['message'] = 'Enter valid username'
            return result

        elif not utils.is_username(data_pass['username']):
            result['message'] = '"' + str(data_pass['username']) + '" is not a valid username. Only aplhanumeric and spaces are allowed'
            return result

        user_data = {
            'username': data_pass['username'],
            'email': data_pass['email'],
            'pwd': secret.token_urlsafe()
        }

        secret_key = hash_user(user_data)
        secret_file_name = get_secret_file_name(user_data['username'])
        token_file_name = get_token_file_name(pwd)

        result['message'] = 'Data ok, unknown state'
        result['secret_file'] = secret_file_name

        if os.path.isfile(secret_file_name):
            result['message'] = 'User file already exists'
            return result

        if secret_key == False:
            result['message'] = 'User registration failed while hashing user data'
            return result

        secret_file_content = {
            'username': user_data['username'],
            'email': user_data['email'],
            'pwd': user_data['pwd'],
            'ts': utils.now().isoformat(),
            'secret': secret_key
        }

        utils.file_save(secret_file_name, json.dumps(secret_file_content))
        utils.file_save(token_file_name, data_pass['username'])
        result['message'] = 'User created successfully'
        result['status'] = True
        result['secret_file_content'] = secret_file_content

        return result
