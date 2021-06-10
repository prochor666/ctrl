import os
from ctrl import secret, utils


def login(token=None):
    return False


def get_user(auto):
    auto = auto


def send_auth_code():

    return {}



def register(data_pass=None):

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

        storage = os.path.join(utils.app_root(), data_pass['config']['filesystem']['secure'])
        secret_content = secret.create_secret({'email': data_pass['email'], 'username': data_pass['username']})
        secret_file = os.path.join(storage, data_pass['username']+'.secret')

        result['message'] = 'Data ok, unknown state'
        result['secret_file'] = secret_file

        if os.path.isfile(secret_file):
            result['message'] = 'User file already exists'
            return result

        if secret_content == False:
            result['message'] = 'User registration failed'
            return result

        #utils.file_save(secret_file, secret_content)
        result['message'] = 'User created successfully'
        result['status'] = True

        return result
