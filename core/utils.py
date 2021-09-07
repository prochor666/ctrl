import os
import glob
from datetime import timezone, datetime
import re
import json
import ipaddress
from core import colors, app
import dns.resolver


def database_check():
    try:
        db_info = app.dbclient.server_info()
        db_db = app.dbclient.list_database_names()
        print(
            f"{colors.green('DB INSTANCE')}: MongoDB version {db_info['version']} at {app.config['mongodb']['host']}:{str(app.config['mongodb']['port'])}")
        print(f"{colors.blue('DATABASES')}: {db_db}")
    except Exception as error:
        print(f"{colors.red('DATABASE ERROR')}: {str(error)}")


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
    dt_now = datetime.now(tz=timezone.utc).isoformat()
    return str(dt_now)


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


def ip_valid(ip):
    r = {
        'ip': ip,
        'version': 0,
        'is_global': False,
        'is_multicast': False,
        'is_private': False,
        'is_reserved': False,
        'is_loopback': False,
        'is_link_local': False,
    }
    try:
        i = ipaddress.ip_address(ip)
        r['version'] = i.version
        r['is_global'] = i.is_global
        r['is_multicast'] = i.is_multicast
        r['is_private'] = i.is_private
        r['is_reserved'] = i.is_reserved
        r['is_loopback'] = i.is_loopback
        r['is_link_local'] = i.is_link_local
        return r
    except:
        return r


def domain_dns_info(domain, record_filter=[]):
    record_types = [
        'A',
        'AAAA',
        'AFSDB',
        'ALIAS',
        'APL',
        'CAA',
        'CDNSKEY',
        'CDS',
        'CERT',
        'CNAME',
        'CSYNC',
        'DHCID',
        'DLV',
        'DNAME',
        'DNSKEY',
        'DS',
        'EUI48',
        'EUI64',
        'HINFO',
        'HIP',
        'IPSECKEY',
        'KEY',
        'KX',
        'LOC',
        'MX',
        'NAPTR',
        'NS',
        'NSEC',
        'NSEC3',
        'NSEC3PARAM',
        'OPENPGPKEY',
        'PTR',
        'RRSIG',
        'RP',
        'SIG',
        'SMIMEA',
        'SOA',
        'SRV',
        'SSHFP',
        'TA',
        'TKEY',
        'TLSA',
        'TSIG',
        'TXT',
        'URI',
        'ZONEMD',
        'SVCB',
        'HTTPS',
    ]
    result = []

    if type(record_filter) is list and len(record_filter) > 0:
        record_types = record_filter

    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            for rdata in answers:
                result.append({'type': record_type, 'value': rdata.to_text()})
        except Exception as e:
            pass

    return result


def detect_object_changes(keys, origin, new):
    for key in keys:
        if key in origin.keys() and key in new:
            if origin[key] != new[key]:
                return True
        else:
            pass

    return False


def list_ssh_keys():
    ssh_dir = f"{os.path.expanduser('~')}{os.path.sep}.ssh{os.path.sep}*"
    files = []
    for f in glob.glob(ssh_dir):
        filename, file_extension = os.path.splitext(f)
        if os.path.isfile(f) and os.path.basename(filename) not in ['known_hosts', 'authorized_keys', 'config'] and file_extension in ['.pub', '.pem', '.key']:
            files.append(f)

    return files


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

    if data_type == 'dict':
        return {} if str(key) not in data.keys() or type(data[key]) is not dict else data[key]

    if data_type == 'list':
        return [] if str(key) not in data.keys() or type(data[key]) is not list else data[key]

    if data_type == 'bool':
        return False if str(key) not in data.keys() else bool(data[key])

    if data_type == 'ipv4':
        return '' if str(key) not in data.keys() and ip_valid(data[key]).version == 4 else data[key]

    if data_type == 'ipv6':
        return '' if str(key) not in data.keys() and ip_valid(data[key]).version == 6 else data[key]


def apply_filter(data_pass):
    data_filter = {}
    data_sort = ['Id', 1]

    if type(data_pass) is dict:

        if 'filter' in data_pass.keys() and type(data_pass['filter']) is dict and len(data_pass['filter']) > 0:
            data_filter = data_pass['filter']

        if 'filter' in data_pass.keys() and type(data_pass['filter']) is list and len(data_pass['filter']) > 0:
            data_filter = filter_to_dict(data_pass['filter'])

        if 'filter' in data_pass.keys() and type(data_pass['filter']) is str and len(data_pass['filter']) > 0:
            df = data_pass['filter'].split(':')
            if len(df) == 2:
                data_filter = {df[0]: df[1]}

        if 'sort' in data_pass.keys() and type(data_pass['sort']) is list and len(data_pass['sort']) == 2:
            data_sort = data_pass['sort']

        if 'sort' in data_pass.keys() and type(data_pass['sort']) is str and len(data_pass['sort']) > 0:
            df = data_pass['sort'].split(':')
            if len(df) == 2:
                data_sort = [df[0]: df[1]]


    return {
        'filter': data_filter,
        'sort': data_sort
    }


def filter_to_dict(data_filter):
    d = {}
    # return filter_data
    for f in data_filter:
        s = f.split(':')
        if len(s) == 2:
            d[s[0]] = s[1]

    return d


def arg_json(arg):
    return json.loads(arg.replace('"', '').replace('\'', '"'))


def br2nl(s):
    return re.sub('<br\s*?>', "\n", str(s))


def nl2br(s):
    return '<br />'.join(s.split("\n"))


def dos2unix(s):
    return str(s).replace('\r\n', '\n')


def tag_parse(tag, raw):
    result = re.findall(
        f"<{tag}>(.*?)</{tag}>", raw, re.DOTALL)

    if len(result) > 0:
        return result[0]

    return ''


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
