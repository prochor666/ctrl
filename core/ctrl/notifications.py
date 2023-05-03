from core import app, data, utils
from core.ctrl import mailer


def list_notifications(filter_data, sort_data=None, exclude_data=None):
    finder = {
        'collection': 'notifications',
        'filter': filter_data,
        'sort': sort_data,
        'exclude': exclude_data
    }
    return data.ex(finder)


def email(case, template, subject, html_message_data, att = None):
    if app.config['user']['username'] != 'system':
        valid_users = data.collect(data.ex({
            'collection': 'users',
            'filter': {
                case: True
            }
        }))

        for user in valid_users:
            html_message_data['user'] = user
            html_message = mailer.assign_template(
                template, html_message_data)
            mailer.send(
                user['email'], subject, html_message, att)


def db(obj_type, obj_id, message, json_data=''):
    notifs = app.db['notifications']
    notification = {
        'user_id': app.config['user']['_id'],
        'created_at': utils.now(),
        'obj_type': obj_type,
        'obj_id': obj_id,
        'message': message,
        'json_data': json_data
    }
    notifs.insert_one(notification)
