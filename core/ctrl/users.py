from bson.objectid import ObjectId
from core import app, utils, data
from core.ctrl import secret, mailer


def list_users(filter_data):
    finder = {
        'collection': 'users',
        'filter': filter_data,
        'exclude': filter_user_pattern()
    }
    return data.ex(finder)


def load_user(filter_data, no_filter_pattern=False):
    finder = {
        'collection': 'users',
        'filter': filter_data
    }
    if not no_filter_pattern:
        finder['exclude'] = filter_user_pattern()
    return data.one(finder)


def filter_user_pattern():
    return {'secret': 0, 'pwd': 0, 'salt': 0}


def insert(user_data):
    result = validator(user_data)

    if result['status'] == True:

        user = user_model(user_data)

        finder = load_user({
        '$or': [
                {'username': user['username']},
                {'email': user['email']}
            ]
        })

        if type(finder) is not dict:

            users = app.db['users']
            user['pwd'] = secret.token_urlsafe(64)
            user['salt'] = secret.token_rand(64)
            user['secret'] = hash_user(user)
            user['ulc'] = secret.token_urlsafe(32)
            user['pin'] = int(secret.pin(6))

            http_origin = ''
            if 'http_origin' in user_data.keys():
                http_origin = user_data.pop('http_origin', None)

            user['created_at'] = utils.now()
            user['creator'] = app.config['user']['_id']

            users.insert_one(user)

            html_message = mailer.email_template('register').format(**{
                'app_full_name': app.config['full_name'],
                'username': user['username'],
                'pin': user['pin'],
                'activation_link': activation_link(user, http_origin)
            })

            es = mailer.send(user['email'], f"{app.config['name']} new account", html_message)
            result['status'] = True
            result['message'] = f"User {user['username']} created"
            result['email_status'] = es
        else:
            param_found = ''
            if finder['username'] == user['username']:
                param_found = f"with username {user['username']}"
            if len(param_found)==0 and finder['email'] == user['email']:
                param_found = f"with email {user['email']}"

            result['status'] = False
            result['message'] = f"User {param_found} already exists"

    return result


def modify(user_data):
    result = validator(user_data)

    if 'id' not in user_data.keys():
        result['message'] = 'Need id for modify user'
        result['status'] = False

    if result['status'] == True:

        finder = load_user({
        '$and': [
            {
                '$or': [
                    {'username': user_data['username']},
                    {'email': user_data['email']}
                ],
            },
            {
            '_id': {
                    '$ne': ObjectId(str(user_data['id']))
                }
            }
        ]
        })

        modify_user = load_user({
            '_id': ObjectId(user_data['id'])
        }, no_filter_pattern=True)

        if type(finder) is not dict and type(modify_user) is dict:

            http_origin = ''
            if 'http_origin' in user_data.keys():
                http_origin = user_data.pop('http_origin', None)

            user = {**modify_user, **user_data}
            users = app.db['users']

            # Email changed, need authorize new auth token
            if user['email'] != modify_user['email']:
                user['pwd'] = secret.token_urlsafe(64)
                user['salt'] = secret.token_rand(64)
                user['pin'] = int(secret.pin(6))
                user['ulc'] = secret.token_urlsafe(32)
                html_template = 'modify-pw'
            else:
                #user['pwd'] = modify_user['pwd']
                html_template = 'modify'

            user['secret'] = hash_user(user)
            user['updated_at'] = utils.now()

            if 'created_at' not in modify_user:
                user['created_at'] = utils.now()

            if 'creator' not in modify_user:
                user['creator'] = app.config['user']['_id']

            user = user_model(user)
            users.update_one({'_id': ObjectId(user_data['id']) }, { '$set': user })

            html_message = mailer.email_template(html_template).format(**{
                'app_full_name': app.config['full_name'],
                'username': user['username'],
                'pin': user['pin'],
                'activation_link': activation_link(user, http_origin)
            })

            es = mailer.send(user['email'], f"{app.config['name']} account updated", html_message)
            result['status'] = True
            result['message'] = f"User {user['username']} modified"
            result['email_status'] = es
        else:
            param_found = ''
            if finder['username'] == user_data['username']:
                param_found = f"with username {user_data['username']}"
            if len(param_found)==0 and finder['email'] == user_data['email']:
                param_found = f"with email {user_data['email']}"

            result['status'] = False
            result['message'] = f"User {param_found} already exists"

    return result


def recover(user_data, soft=True):
    result = {
        'message': "User not found",
        'status': False,
        'recovery_type': "soft" if soft == True else "full"
    }

    if type(user_data) is dict and 'username' in user_data.keys():
        unifield = user_data['username']

        user = load_user({
            '$or': [
                {'username': unifield},
                {'email': unifield}
            ]
        }, no_filter_pattern=True)

        if type(user) is dict:

            http_origin = ''
            if 'http_origin' in user_data.keys():
                http_origin = user_data.pop('http_origin', None)

            result['message'] = f"Found user {user['username']}"
            result['status'] = True
            html_template = 'soft-recovery'

            user['pin'] = int(secret.pin(6))
            user['ulc'] = secret.token_urlsafe(32)

            new_activation_link = activation_link(user, http_origin)
            subject_suffix = "account activation"

            if app.mode == 'cli':
                result['pin'] = user['pin']
                result['ulc'] = user['ulc']
                result['activation_link'] = new_activation_link

            if soft == False:
                user['pwd'] = secret.token_urlsafe(64)
                user['salt'] = secret.token_rand(64)
                user['secret'] = hash_user(user)
                html_template = 'full-recovery'
                subject_suffix = "account recovery"

            users = app.db['users']
            user['updated_at'] = utils.now()

            users.update_one({'_id': ObjectId(user['_id']) }, { '$set': user })

            html_message = mailer.email_template(html_template).format(**{
                'app_full_name': app.config['full_name'],
                'username': user['username'],
                'pin': user['pin'],
                'activation_link': new_activation_link
            })

            es = mailer.send(user['email'], f"{app.config['name']} {subject_suffix}", html_message)
            result['email_status'] = es

    return result


def activate(user_data):
    user = load_user({
        '$and': [
            {'ulc': utils.eval_key('ulc', user_data)},
            {'pin': utils.eval_key('pin', user_data, 'int')}
        ]
    }, no_filter_pattern=True)

    result = {
        'message': "Invalid activation",
        'status': False,
        'ulc': utils.eval_key('ulc', user_data),
        'pin': utils.eval_key('pin', user_data, 'int'),
    }

    if type(user) is dict:
        result['status'] = True
        result['message'] = "Valid activation"
        result['username'] = user['username']
        result['role'] = user['role']
        result['pwd'] = user['pwd']

    return result


def activation_link(user_data, http_origin=''):
    link = ""

    if int(user_data['pin']) > 99999:
        client_url = compose_client_url(user_data, http_origin)
        link = f"{client_url}/activate/?ulc={str(user_data['ulc'])}&pin={str(user_data['pin'])}"

    return link


def compose_client_url(user_data, http_origin=''):
    if len(http_origin) > 0 and http_origin.startswith(('http://', 'https://')):
        if http_origin.endswith('/'):
            return http_origin[:-1]

        return http_origin

    protocol = "http"
    if app.config['https'] == True:
        protocol = "https"

    port = f":{app.config['mask_http_port']}"
    if port in [":80", ":443"]:
        port = ""

    link = f"{protocol}://{app.config['mask_http_origin']}{port}"

    return link


def delete(user_data):
    result = {
        'status': False,
        'message': 'Need id to delete user',
        'user_data': user_data
    }

    if 'id' in user_data.keys():
        users = app.db['users']
        r = users.delete_one({'_id': ObjectId(user_data['id'])})
        result['delete_status'] = r.deleted_count
        result['status'] = False if r.deleted_count == 0 else True
        result['message'] = 'User delete error' if r.deleted_count == 0 else 'User deleted'

    return result


def validator(user_data):
    result = {
        'status': False,
        'message': "Data error",
    }

    if type(user_data) is dict and 'email' in user_data.keys() and 'username' in user_data.keys():

        if type(user_data['email']) != str:
            result['message'] = "Enter valid email address"
            return result

        email_validation = mailer.check_email(user_data['email'])
        if not email_validation['valid']:
            result['message'] = f"Email '{user_data['email']}' is invalid. {email_validation['description']}"
            return result

        if type(user_data['username']) != str:
            result['message'] = "Enter valid username"
            return result

        elif not utils.is_username(user_data['username']):
            result['message'] = f"{user_data['username']} is not a valid username. Only aplhanumeric and spaces are allowed"
            return result

        result['status'] = True

    return result


def system_user():
    finder = load_user({
        'username': 'system'
    })

    if type(finder) is not dict:
        create_system_user()

        finder = load_user({
            'username': 'system'
        })

    return finder


def create_system_user():

    user = user_model({
        'username': 'system',
        'firstname': 'System',
        'lastname': 'User',
        'role': 'admin',
        'email': 'noreply@local.none'
    })

    users = app.db['users']

    user['pwd'] = 'system'
    user['salt'] = secret.token_rand(64)
    user['secret'] = hash_user(user)
    user['ulc'] = ''
    user['pin'] = 0

    users.insert_one(user)

    return user


def user_model(user_data):
    if type(user_data) is not dict:
        user_data = {}

    user = {
        'username': utils.eval_key('username', user_data),
        'email': utils.eval_key('email', user_data),
        'firstname': utils.eval_key('firstname', user_data),
        'lastname': utils.eval_key('lastname', user_data),
        'role': utils.eval_key('role', user_data),
        'pin': utils.eval_key('pin', user_data, 'int'),
        'pwd': utils.eval_key('pwd', user_data),
        'salt': utils.eval_key('salt', user_data),
        'secret': utils.eval_key('secret', user_data),
        'ulc': utils.eval_key('ulc', user_data),
        'creator': utils.eval_key('creator', user_data),
        'created_at': utils.eval_key('created_at', user_data),
        'updated_at': utils.eval_key('updated_at', user_data),
    }

    return user


def hash_user(user_data):
    secret_key = secret.create_secret({
        'email': user_data['email'],
        'salt': user_data['salt'],
        'pwd': user_data['pwd']})
    return secret_key
