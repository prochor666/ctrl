import os
import datetime
import re
import json
from pymongo import results
from validate_email import validate_email
from core import colors, app


def database_check():
    try:
        db_info = app.dbclient.server_info()
        db_db = app.dbclient.list_database_names()
        print(f"{colors.green('DB INSTANCE')}: MongoDB version {db_info['version']} at {app.config['mongodb']['host']}:{str(app.config['mongodb']['port'])}")
        print(f"{colors.blue('DATABASES')}: {db_db}")
    except Exception as error:
        print(f"{colors.red('ERROR')}: {str(error)}")


def byte_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor


def decimal_size(num, suffix="Hz"):
    factor = 1000
    for unit in ["", "K", "M", "G", "T", "P"]:
        if num < factor:
            return f"{num:.2f} {unit}{suffix}"
        num /= factor


def replace_all(text, r={}):
    for i, j in r.items():
        text = text.replace(i, j)
    return text


def in_dict(d, key):
    if type(d) is dict and key in d.keys():
        return True
    return False


def is_username(username=None):
    return all(ch.isalnum() or ch.isspace() for ch in str(username))


def now():
    return datetime.datetime.utcnow()


def app_root():
    p = os.path.dirname(os.path.abspath(__file__))
    return strip_end(p, f"{os.path.sep}core")


def strip_end(text, suffix):
    if suffix and text.endswith(suffix):
        return text[:-len(suffix)]
    return text


def format_response(status, text):
    return f"{colors.green('DONE')}: {text}" if status == True else f"{colors.red('ERROR')}: {text}"


def validate_data_pass(d):
    result = {}
    for k, v in d.items():
        if v != None:
            result[k] = v
    return result


def file_save(file, content=' '):
    fh = open(file, 'w')
    fh.write(content)
    fh.close()
    return True


def eval_key(key, data, data_type='str'):
    if data_type == 'str':
        return '' if str(key) not in data.keys() else str(data[key])

    if data_type == 'int':
        return 0 if str(key) not in data.keys() else int(data[key])


def collect(find_result):
    result = []
    for document in find_result:
        result.append(document)
    return result


def arg_json(arg):
    return json.loads(arg.replace('"', '').replace('\'', '"'))


def br2nl(s):
    return re.sub('<br\s*?>', '\n', str(s))


# 3rd party
# thx to: https://www.calebthorne.com/blog/python/2012/06/08/python-strip-tags
def strip_tags(string, allowed_tags=''):

    if allowed_tags != '':
        # Get a list of all allowed tag names.
        allowed_tags_list = re.sub(r'[\\/<> ]+', '', allowed_tags).split(',')
        allowed_pattern = ''

        for s in allowed_tags_list:

            if s == '':
                continue
                # Add all possible patterns for this tag to the regex.

            if allowed_pattern != '':
                allowed_pattern += '|'

            allowed_pattern += '<' + s + ' [^><]*>$|<' + s + '>|'

    # Get all tags included in the string.
    all_tags = re.findall(r'<]+>', string, re.I)

    for tag in all_tags:
        # If not allowed, replace it.
        if not re.match(allowed_pattern, tag, re.I):
            string = string.replace(tag, '')
        else:
            # If no allowed tags, remove all.
            string = re.sub(r'<[^>]*?>', '', string)

    return string
