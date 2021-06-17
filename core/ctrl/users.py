from core import app


def list_users():
    users = app.db['users']
    return users


def one(finder):
    users = app.db['users']
    user = users.find_one(finder)
    return user


def insert(user):
    users = app.db['users']
    users.insert_one(user)


