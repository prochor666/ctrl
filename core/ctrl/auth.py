import os
import json
from core import utils, app
from core.ctrl import secret, mailer, users


def authorization_process(api_method):

    result = {
        'message': "Authorization failed",
        'username': '',
        'status': False
    }

    if 'headers' in app.config.keys() and api_method in app.config['api']['rest_authorized'].keys():

        if 'Authorization' in app.config['headers'].keys():
            auth_token = extract_auth_token(
                app.config['headers']['Authorization'])

            if len(auth_token) > 63:
                login_obj = login({'auth_token': auth_token})
                return login_obj

    if api_method in app.config['api']['rest_free'].keys():
        result['message'] = "No authorization required"
        result['status'] = True

    return result


def extract_auth_token(header):
    auth_token = ''

    if header.startswith('Token ', 0, 6):
        auth_token = header[6:]

    return auth_token


def login(data_pass=None):
    result = {
        'message': "Token authorization failed",
        'username': '',
        'status': False
    }

    if 'auth_token' in data_pass.keys():
        username = get_user_from_token(data_pass['auth_token'])

        if len(username) > 0:
            user_data = get_user_from_secret_file(username)
            secret_key_check = hash_user(user_data)

            if 'username' in user_data.keys() and 'pwd' in user_data.keys() and data_pass['auth_token'] == user_data['pwd'] and secret_key_check == user_data['secret']:
                result['message'] = "Authorization succeeded"
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
    storage = os.path.join(
        utils.app_root(), app.config['filesystem']['seccets'])
    secret_file_name = os.path.join(storage, f"{username}.secret")
    return secret_file_name


def get_token_file_name(token):
    storage = os.path.join(utils.app_root(), app.config['filesystem']['auth'])
    token_file = os.path.join(storage, token)
    return token_file


def get_user_from_token(token):
    token_file = get_token_file_name(token)
    result = ""

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
    secret_key = secret.create_secret({
        'email': user_data['email'],
        'pwd': user_data['pwd']})
    return secret_key


def recover_user(data_pass=None):
    if type(data_pass) is dict and 'username' in data_pass.keys():

        secret_file_name = get_secret_file_name(data_pass['username'])

        if os.path.isfile(secret_file_name):
            user_data = get_user_from_secret_file(data_pass['username'])
            token_file_name = get_token_file_name(user_data['pwd'])

            if os.path.isfile(token_file_name):

                html_message = mailer.email_template('recover').format(**{
                    'app_full_name': app.config['full_name'],
                    'username': user_data['username'],
                    'pwd': user_data['pwd']
                })

                es = mailer.send(user_data['email'], f"{app.config['name']} account recovery", html_message)

                return {
                    'status': True,
                    'message': "Recovery succeeded, email sent",
                    'email_status': es
                }

    return {
        'status': False,
        'message': "Recovery failed, account not found"
    }

def register_user(data_pass=None):

    result = {
        'status': False,
        'message': "Data error",
        'secret_file': None
    }

    if type(data_pass) is dict and 'email' in data_pass.keys() and 'username' in data_pass.keys():

        if type(data_pass['email']) != str:
            result['message'] = "Enter valid email address"
            return result

        email_validation = mailer.check_email(data_pass['email'])
        if not email_validation['valid']:
            result['message'] = f"{data_pass['email']}: {email_validation['description']}"
            return result

        if type(data_pass['username']) != str:
            result['message'] = "Enter valid username"
            return result

        elif not utils.is_username(data_pass['username']):
            result['message'] = f"{data_pass['username']} is not a valid username. Only aplhanumeric and spaces are allowed"
            return result

        user_data = {
            'username': data_pass['username'],
            'email': data_pass['email'],
            'pwd': secret.token_urlsafe(64)
        }

        secret_key = hash_user(user_data)
        secret_file_name = get_secret_file_name(user_data['username'])
        token_file_name = get_token_file_name(user_data['pwd'])

        result['message'] = "Data ok, unknown state"
        result['secret_file'] = secret_file_name

        if os.path.isfile(secret_file_name):
            result['message'] = f"Secret for {user_data['username']} already exists"
            return result

        if secret_key == False:
            result['message'] = "User registration failed while hashing user data"
            return result

        secret_file_content = {
            'username': user_data['username'],
            'email': user_data['email'],
            'pwd': user_data['pwd'],
            'ts': utils.now().isoformat(),
            'secret': secret_key
        }

        html_message = mailer.email_template('register').format(**{
            'app_full_name': app.config['full_name'],
            'username': user_data['username'],
            'pwd': user_data['pwd']
        })

        es = mailer.send(user_data['email'], f"{app.config['name']} new account", html_message)

        utils.file_save(secret_file_name, json.dumps(secret_file_content))
        utils.file_save(token_file_name, user_data['username'])
        result['message'] = "User created successfully"
        result['status'] = True
        result['secret_file_content'] = secret_file_content
        result['email_status'] = es

        return result
