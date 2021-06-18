from bson.objectid import ObjectId
from core import app, utils
from core.ctrl import secret, mailer


def list_users(finder={}):
    q_filter = {}
    q_sort = ['username', 1]
    users = app.db['users']

    if type(finder) is dict and 'filter' in finder.keys() and type(finder['filter']) is dict:
        q_filter = finder['filter']

    if type(finder) is dict and 'sort' in finder.keys() and type(finder['sort']) is list and len(finder['sort']) == 2:
        q_sort = finder['sort']
        from_str = {
            'asc': 1,
            'desc': -1
        }
        if type(q_sort[1]) is str and q_sort[1].lower() in from_str.keys():
            q_sort[1] = from_str[q_sort[1]]

    return users.find(q_filter, filter_user_pattern()).sort(q_sort[0], q_sort[1])


def one(finder, no_filter_pattern=False):
    if 'users' in app.db.list_collection_names():

        if no_filter_pattern == True:
            return app.db['users'].find_one(finder)

        return app.db['users'].find_one(finder, filter_user_pattern())
    return False


def filter_user_pattern():
    return {'secret': 0, 'pwd': 0}


def insert(user_data):

    result = validator(user_data)

    if result['status'] == True:

        user = user_model(user_data)

        finder = one({
        '$or': [
                {'username': user['username']},
                {'email': user['email']}
            ]
        })

        if type(finder) is not dict:

            users = app.db['users']
            user['pwd'] = secret.token_urlsafe(64)
            user['secret'] = hash_user(user)
            users.insert_one(user)

            html_message = mailer.email_template('register').format(**{
                'app_full_name': app.config['full_name'],
                'username': user['username'],
                'pwd': user['pwd']
            })

            es = mailer.send(user['email'], f"{app.config['name']} new account", html_message)
            result['status'] = True
            result['message'] = f"User {user['username']} created"
            result['email_status'] = es
        else:
            result['message'] = "Username or email already exists"

    return result


def modify(user_data):

    result = validator(user_data)

    if result['status'] == True:

        user = user_model(user_data)

        finder = one({
        '$and': [
            {
                '$or': [
                    {'username': user['username']},
                    {'email': user['email']}
                ],
            },
            {
            '_id': {
                    '$ne': ObjectId(user_data['id'])
                }
            }
        ]
        })

        modify_user = one({
            '_id': ObjectId(user_data['id'])
        }, no_filter_pattern=True)

        if type(finder) is not dict and type(modify_user) is dict:

            users = app.db['users']

            # Email changed, need authorize new auth token
            if user['email'] != modify_user['email']:
                user['pwd'] = secret.token_urlsafe(64)
                html_template = 'modify-pw'
            else:
                user['pwd'] = modify_user['pwd']
                html_template = 'modify'

            user['secret'] = hash_user(user)
            users.update_one({'_id': ObjectId(user_data['id']) }, { '$set': user })

            html_message = mailer.email_template(html_template).format(**{
                'app_full_name': app.config['full_name'],
                'username': user['username'],
                'pwd': user['pwd']
            })

            es = mailer.send(user['email'], f"{app.config['name']} account updated", html_message)
            result['status'] = True
            result['message'] = f"User {user['username']} modified"
            #result['finder'] = finder
            result['email_status'] = es
        else:
            #result['message'] = "Username or email already exists"
            result['finder'] = finder

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
            result['message'] = f"{user_data['email']}: {email_validation['description']}"
            return result

        if type(user_data['username']) != str:
            result['message'] = "Enter valid username"
            return result

        elif not utils.is_username(user_data['username']):
            result['message'] = f"{user_data['username']} is not a valid username. Only aplhanumeric and spaces are allowed"
            return result

        result['status'] = True

    return result



def user_model(user_data):
    if type(user_data) is not dict:
        user_data = {}

    user = {
        'username': utils.eval_key('username', user_data),
        'email': utils.eval_key('email', user_data),
        'firstname': utils.eval_key('firstname', user_data),
        'lastname': utils.eval_key('lastname', user_data),
        'role': utils.eval_key('role', user_data),
        'pwd': utils.eval_key('pwd', user_data),
        'secret': utils.eval_key('secret', user_data)
    }

    return user


def hash_user(user_data):
    secret_key = secret.create_secret({
        'email': user_data['email'],
        'pwd': user_data['pwd']})
    return secret_key
