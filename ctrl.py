import argparse, os, sys
from core.ctrl import config, utils, colors, auth, api, network

conf = config.configure()

parser = argparse.ArgumentParser(
    description='CTRL command line tool',
    epilog='All accessible arguments listed above'
)

parser.add_argument('method', help='Specify API method')
parser.add_argument('-email', type=str)
parser.add_argument('-username', type=str)
parser.add_argument('-vhost', type=str)
parser.add_argument('-ip', type=str)

args, unknown = parser.parse_known_args()

data_pass = dict(vars(args))

method = data_pass.pop('method', None)

if method in conf['api']['cli']:

    data_pass['config'] = conf
    result = getattr(api, str(method))(data_pass)

    if type(result) == dict:
        status = True
        message = 'completed'

        if 'status' in result:
            status = result['status']
            result.pop('status', None)

        if 'message' in result:
            message = result['message']
            result.pop('message', None)

        print(utils.format_response(status, message))

        for key, value in result.items():
            print(colors.blue(key) + ': ' + str(value))

    if type(result) == list or type(result) == tuple or type(result) == set:

        for value in result:
            print(str(value))


else:

    print(utils.format_response(False, 'Method "' + method + '" is not allowed'))