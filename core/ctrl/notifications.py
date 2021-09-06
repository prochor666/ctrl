from core import app, data
from core.ctrl import mailer


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
        'obj_type': obj_type,
        'obj_id': obj_id,
        'message': message,
        'json_data': json_data
    }
    notifs.insert_one(notification)
