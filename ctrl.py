import argparse
from core import compat, app, utils, colors
from core.ctrl import api

compat.check_version()
app.mode = 'cli'

parser = argparse.ArgumentParser(
    description="CTRL command line tool",
    epilog="All accessible arguments listed above"
)

parser.add_argument('method', help="Specify API method")
parser.add_argument('-id', type=str)
parser.add_argument('-username', type=str)
parser.add_argument('-email', type=str)
parser.add_argument('-firstname', type=str)
parser.add_argument('-lastname', type=str)
parser.add_argument('-role', type=str)
parser.add_argument('-filter', type=str)
parser.add_argument('-ulc', type=str)
parser.add_argument('-pin', type=int)
parser.add_argument('-sort', type=str)
parser.add_argument('-vhost', type=str)
parser.add_argument('-ip', type=str)
#parser.add_argument('-auth_token', type=str)
parser.add_argument('-http_origin', type=str)


args, unknown = parser.parse_known_args()

data_pass = utils.validate_data_pass(dict(vars(args)))

method = data_pass.pop('method', None)

for key, value in data_pass.items():

    if key in ['filter', 'sort']:
        data_pass[key] = utils.arg_json(value)


if method != None and method in dir(api) and method in app.config['api']['cli']:

    #data_pass['config'] = app.config
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
            print(f"{colors.blue(key)} : {str(value)}")

    if type(result) == list or type(result) == tuple or type(result) == set:

        for value in result:
            print(str(value))

else:
    print(utils.format_response(False, f"Method {method} is not allowed"))
