import os
from validate_email import validate_email
from core import colors


def database_check(app):
    try:
        db_info = app.db.server_info()
        print(colors.green('DB OK') + ': MongoDB version ' + db_info['version'] + ' at ' + app.config['mongodb']['host'] + ':' + str(app.config['mongodb']['port']))
    except Exception as error:
        print(colors.red('ERROR') + ': ' + str(error))


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


def is_email(email=None):
    return validate_email(email_address=str(email), check_format=True, check_blacklist=True, check_dns=True, dns_timeout=15)


def is_username(username=None):
    return all(ch.isalnum() or ch.isspace() for ch in str(username))


def app_root():
    p = os.path.dirname(os.path.abspath(__file__))
    return strip_end(p, os.path.sep+'core')


def strip_end(text, suffix):
    if suffix and text.endswith(suffix):
        return text[:-len(suffix)]
    return text


def format_response(status, text):
    return colors.green('DONE') + ': ' + text if status == True else colors.red('ERROR') + ': ' + text


def file_save(file, content):
    f = file
    fh = open(f, 'w')
    fh.write(content)
    fh.close()
    return True