from core import app
from core.ctrl import users
from flask import request

def authorization_process(api_method):

    result = {
        'message': "Authorization failed",
        'username': '',
        'role': '',
        'status': False
    }

    if 'headers' in app.config.keys() and api_method in app.config['api']['rest_authorized'].keys():


        if request.headers.get('Authorization') != None:
            auth_token = extract_auth_token(
                request.headers.get('Authorization'))

            if len(auth_token) > 63:
                login_obj = login({'auth_token': auth_token})
                return login_obj

    if api_method in app.config['api']['rest_free'].keys():
        result['message'] = "No authorization required"
        result['status'] = True

    return result


def login(data_pass=None):
    result = {
        'message': "Token authorization failed",
        'username': '',
        'role': '',
        'status': False
    }

    if 'auth_token' in data_pass.keys():
        user_data = get_user_from_db(data_pass['auth_token'])

        if type(user_data) is dict:
            secret_key_check = users.hash_user({
                'email': user_data['email'],
                'salt':  user_data['salt'],
                'pwd': data_pass['auth_token']
            })

            result['message'] = "User found, secret check failed"

            if 'username' in user_data.keys() and 'pwd' in user_data.keys() and data_pass['auth_token'] == user_data['pwd'] and secret_key_check == user_data['secret']:
                result['message'] = "Authorization succeeded"
                result['username'] = user_data['username']
                result['role'] = user_data['role']
                result['status'] = True

    return result


def extract_auth_token(header):
    auth_token = ''

    if header.startswith('Token ', 0, 6):
        auth_token = header[6:]

    return auth_token


def get_user_from_db(token):
    user = users.one({
        'pwd': token
    }, no_filter_pattern=True)

    if type(user) is dict:
        return user

    return False
