import os
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
        print(f"{colors.green('DB INSTANCE')}: MongoDB version {db_info['version']} at {app.config['mongodb']['host']}:{str(app.config['mongodb']['port'])}")
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



def domain_dns_info(domain):
    record_types = [
        'ALIAS',
        'NONE',
        'A',
        'NS',
        'MD',
        'MF',
        'CNAME',
        'SOA',
        'MB',
        'MG',
        'MR',
        'NULL',
        'WKS',
        'PTR',
        'HINFO',
        'MINFO',
        'MX',
        'TXT',
        'RP',
        'AFSDB',
        'X25',
        'ISDN',
        'RT',
        'NSAP',
        'NSAP-PTR',
        'SIG',
        'KEY',
        'PX',
        'GPOS',
        'AAAA',
        'LOC',
        'NXT',
        'SRV',
        'NAPTR',
        'KX',
        'CERT',
        'A6',
        'DNAME',
        'OPT',
        'APL',
        'DS',
        'SSHFP',
        'IPSECKEY',
        'RRSIG',
        'NSEC',
        'DNSKEY',
        'DHCID',
        'NSEC3',
        'NSEC3PARAM',
        'TLSA',
        'HIP',
        'CDS',
        'CDNSKEY',
        'CSYNC',
        'SPF',
        'UNSPEC',
        'EUI48',
        'EUI64',
        'TKEY',
        'TSIG',
        'IXFR',
        'AXFR',
        'MAILB',
        'MAILA',
        'ANY',
        'URI',
        'CAA',
        'TA',
        'DLV',
    ]
    result = []

    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            for rdata in answers:
                result.append({'type': record_type, 'value': rdata.to_text()})
        except Exception as e:
            pass

    return result

def domain_dns_check(domain):

    return True


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
