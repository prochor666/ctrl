from core.config import app_config
import json
import datetime
import logging
from flask import Flask, render_template, Response, request
from core import compat, app
from core.ctrl import api, auth

compat.check_version()
webapp = Flask(__name__)
app.mode = 'http'


@webapp.route('/')
def index():
    if request.headers.get('X-Forwarded-For') != None:
        app.config['client_ip'] = request.headers.get('X-Forwarded-For')
    else:
        app.config['client_ip'] = request.remote_addr

    if request.headers.get('X-Real-Ip') != None:
        app.config['client_ip'] = request.headers.get('X-Real-Ip')

    return render_template('index.html', config=app.config)


@webapp.route('/api/')
@webapp.route('/api/<path:api_method>', methods=['POST', 'GET'])
def respond(api_method=None):
    if request.headers.get('X-Forwarded-For') != None:
        app.config['client_ip'] = request.headers.get('X-Forwarded-For')
    else:
        app.config['client_ip'] = request.remote_addr

    if request.headers.get('X-Real-Ip') != None:
        app.config['client_ip'] = request.headers.get('X-Real-Ip')


    api_method = str(api_method).replace('/', '')
    reason = f"API route {api_method} is not supported"
    module_status = False
    result = None
    request_method = "Unknown"

    if api_method != None and api_method in dir(api):

        reason = f"API route: {api_method}"
        data_pass = {}

        if request.method == 'POST':
            request_method = 'POST'

            if request.headers.get('Content-type') != None and request.headers.get('Content-type').startswith('application/json'):
                request_method = 'POST-JSON'
                data_pass = request.get_json()
            else:
                data_pass = request.form
        else:
            request_method = 'GET'
            data_pass = request.args

        data_pass = dict(data_pass)

        logged = auth.authorization_process(api_method)
        result = logged

        if logged['status'] == True:
            # Start api request passing
            module_status = True

            if api_method != 'login':
                result = getattr(api, api_method)(data_pass)

    res = json.dumps({
        'api': f"{app.config['full_name']} REST api 1.0",
        'module_status': module_status,
        'request_method': request_method,
        'reason': reason,
        'result': result
    })

    return Response(res, mimetype='application/json')


if __name__ == '__main__':
    today = datetime.date.today()
    logging.basicConfig(filename=f"storage/logs/ctrl-server-{today.strftime('%Y-%m')}.log",level=logging.INFO)

    # Open, any host allowed
    webapp.run(debug=True, host='0.0.0.0', port='5007')

    # Secure, only localhost allowed
    # webapp.run(debug=True, host='127.0.0.1', port='5007')
